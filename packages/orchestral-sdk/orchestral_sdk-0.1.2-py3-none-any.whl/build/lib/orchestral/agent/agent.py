from orchestral.llm.base.llm import LLM
from orchestral.llm.openai.client import GPT
from orchestral.context.context import Context
from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from typing import Optional, Callable
import time


class Agent:
    def __init__(self,
            llm: Optional[LLM] = None,
            context: Optional[Context] = None,
            tools: Optional[list] = None,
            system_prompt: Optional[str] = None,
            debug: bool = False,
            display_hook: Optional[Callable] = None,
            tool_hooks: Optional[list] = None,
            max_tool_interations: int = 8,
            conversation_id: str = "default",
            # on_stream_callback: Optional[Callable] = None
    ):
        self.llm = llm if llm is not None else GPT()
        self.system_prompt = system_prompt or "You are a helpful assistant."
        self.context = Context(system_prompt=self.system_prompt) if context is None else context
        self.debug = debug
        self.display_hook = display_hook
        self.tool_hooks = tool_hooks or []  # List of ToolHook instances
        self.conversation_id = conversation_id
        # self.on_stream_callback = on_stream_callback
        self.interrupt_flag = None  # Optional interrupt support (set by WebSocket handler or other UI)
        if tools is not None:
            # Inject context into tools before passing to LLM
            # This allows tools to access context.metadata for shared state
            self._inject_context_into_tools(tools)
            # Inject conversation_id into tools that support it
            self._inject_conversation_id_into_tools(tools)
            self.llm.set_tools(tools)
        self.max_tool_interations = max_tool_interations

    def _inject_context_into_tools(self, tools: list):
        """Inject agent context reference into tools that support it.

        Tools with an agent_context StateField receive a reference to the agent's
        context object. This allows them to:
        - Read/write context.metadata for shared state
        - Access conversation-specific data that persists across saves/loads

        Note: Tools receive a reference to the same Context instance, so changes
        to context.metadata are immediately visible to all tools.
        """
        for tool in tools:
            if hasattr(tool, 'agent_context'):
                # Direct assignment - StateField should handle this
                tool.agent_context = self.context

    def _inject_conversation_id_into_tools(self, tools: list):
        """Inject conversation_id into tools that support it.

        Tools with a conversation_id StateField receive the agent's conversation_id.
        This enables conversation-scoped features like todo lists without exposing
        the conversation_id to the LLM.
        """
        from orchestral.tools.base.field_utils import is_state_field

        for tool in tools:
            tool_class = tool.__class__
            if hasattr(tool_class, 'model_fields') and 'conversation_id' in tool_class.model_fields:
                field_info = tool_class.model_fields['conversation_id']
                if is_state_field(field_info):
                    tool.conversation_id = self.conversation_id


    def _call_display_hook(self):
        """Call the display hook if it's set"""
        if self.display_hook:
            self.display_hook(self.context)

    def send_text_message(self, message: str, **llm_kwargs) -> Message:
        self.context.add_message(Message(role="user", text=message))
        self._call_display_hook()  # Show user message

        response = self.llm.get_response(self.context, **llm_kwargs)
        self.context.add_message(response)
        self._call_display_hook()  # Show agent response (potentially with pending tools)
        return response.message
    

    def run(self, message: str, max_iterations=8, **llm_kwargs) -> Message:
        # Defensive: ensure context is valid before starting
        self.context.fix_orphaned_results()
        self.context.fix_missing_ids()

        response = self.send_text_message(message, **llm_kwargs)
        iteration_count = 0

        if self.debug:
            print(f"Initial response: {response}", "", sep="\n")

        while response.tool_calls and iteration_count < max_iterations:
            self._handle_tool_calls()
            self._call_display_hook()  # Show updated context after tool execution

            llm_response = self.llm.get_response(self.context, **llm_kwargs)
            if self.debug:
                print(f"Iteration count: {iteration_count}", f"LLM response after tool calls: {llm_response}", "", sep="\n")
            self.context.add_message(llm_response)  # Add full Response object
            self._call_display_hook()  # Show agent response (potentially with more pending tools)

            response = llm_response.message         # Update response for loop condition
            iteration_count += 1

        # If max iterations reached, fix any unmatched tool calls
        if iteration_count >= max_iterations and response.tool_calls:
            self.context.fix_orphaned_results()
            self.context.fix_missing_ids()
            if self.debug:
                print(f"Warning: Reached maximum tool call iterations ({max_iterations})")

        return response
    

    def stream_text_message(self, message: str, **llm_kwargs):
        # Defensive: ensure context is valid before starting
        self.context.fix_orphaned_results()
        self.context.fix_missing_ids()

        # Handle the user's message
        self.context.add_message(Message(role="user", text=message))

        response_generator = self._stream_response(**llm_kwargs)
        for text_chunk in response_generator:
            yield text_chunk

        
    def _handle_tool_calls(self):
        """Handle any tool calls in the latest Response"""
        response = self.context.messages[-1]
        assert isinstance(response, Response), "Expected the latest message to be a Response"

        if not response.message.tool_calls:
            return  # No tool calls to handle

        for tool_call in response.message.tool_calls:
            # Check for interrupt between tool calls
            if self.interrupt_flag and self.interrupt_flag.is_set():
                break  # Stop executing more tools

            self._handle_tool_call(tool_call)


    def _handle_tool_call(self, tool_call):
        """Handle a single tool call with optional streaming support and tool hooks"""
        tool_arguments = tool_call.arguments
        tool_name = tool_call.tool_name

        # --- PRE-EXECUTION HOOKS ---
        # Run before_call tool_hooks - short-circuit on first rejection
        for hook in self.tool_hooks:
            try:
                pre_result = hook.before_call(tool_name, tool_arguments)
                if not pre_result.approved:
                    # Hook rejected the tool call - create error message
                    error_message = Message(
                        role="tool",
                        text=pre_result.error_message or f"Tool call to {tool_name} was rejected by hook",
                        tool_call_id=tool_call.id,
                        failed=True
                    )
                    self.context.add_message(error_message)
                    self._call_display_hook()  # Show the error message

                    # Check if we should interrupt execution entirely
                    if pre_result.should_interrupt and self.interrupt_flag:
                        self.interrupt_flag.set()

                    return
            except Exception as e:
                # Hook raised an exception - treat as rejection
                error_message = Message(
                    role="tool",
                    text=f"Hook error in {hook.__class__.__name__}: {str(e)}",
                    tool_call_id=tool_call.id,
                    failed=True
                )
                self.context.add_message(error_message)
                self._call_display_hook()  # Show the error message
                return

        # --- TOOL EXECUTION ---
        try:
            tool = self.llm.tool_router[tool_name]
        except KeyError:
            error_message = Message(
                role="tool",
                text=f"Tool '{tool_name}' not found! Available tools: {list(self.llm.tool_router.keys())}",
                tool_call_id=tool_call.id,
                failed=True
            )
            self.context.add_message(error_message)
            return


        # Set up streaming callback if agent has one configured
        stream_callback = None                                                  # type: ignore
        if hasattr(self, 'tool_stream_callback') and self.tool_stream_callback:
            def stream_callback(chunk: str):
                self.tool_stream_callback(
                    tool_call_id=tool_call.id,
                    tool_name=tool_name,
                    chunk=chunk
                )

        # Time the tool execution and catch exceptions
        start_time = time.perf_counter()
        try:
            tool_response = tool.execute(stream_callback=stream_callback, **tool_arguments)
        except Exception as e:
            # Tool execution failed - create error message
            end_time = time.perf_counter()
            runtime_ms = (end_time - start_time) * 1000

            error_message = Message(
                role="tool",
                text=f"Tool execution failed: {str(e)}",
                tool_call_id=tool_call.id,
                failed=True
            )
            error_message.metadata['runtime_ms'] = runtime_ms
            self.context.add_message(error_message)
            return

        end_time = time.perf_counter()
        runtime_ms = (end_time - start_time) * 1000

        response_message = Message(
            role="tool",
            text=str(tool_response),
            tool_call_id=tool_call.id
        )
        response_message.metadata['runtime_ms'] = runtime_ms

        # --- POST-EXECUTION HOOKS ---
        # Run after_call hooks - chain modifications
        for hook in self.tool_hooks:
            try:
                post_result = hook.after_call(tool_name, response_message)
                response_message = post_result.apply_to(response_message)
            except Exception as e:
                # Hook failed - log warning but continue with current message
                if self.debug:
                    print(f"Warning: Hook {hook.__class__.__name__} failed in after_call: {e}")

        self.context.add_message(response_message)

        # Call completion callback if set (for UI updates)
        if hasattr(self, 'tool_complete_callback') and self.tool_complete_callback:
            self.tool_complete_callback(tool_call.id, tool_name)


    def _stream_response(self, **llm_kwargs):
        # self.context.add_message(Message(role="user", text=message))
        response_generator = self.llm.stream_response(self.context, **llm_kwargs)
        accumulated_text = ""

        try:
            while True:
                # Check for interrupt before getting next chunk
                if self.interrupt_flag and self.interrupt_flag.is_set():
                    # print(f"[DEBUG AGENT] Interrupt detected! Stopping stream immediately")
                    # Stop the LLM stream and handle the partial response
                    self._handle_interrupt(accumulated_text)
                    return

                text_chunk = next(response_generator)
                accumulated_text += text_chunk
                # if self.on_stream_callback:  # If you want a callback...
                #     self.on_stream_callback(text_chunk)
                yield text_chunk
        except StopIteration as e:
            response = e.value  # The Response object
            self.context.add_message(response)
            # DON'T call fix_missing_ids() here - let the caller handle tool execution
            # The tool loop will call fix_missing_ids() only if max iterations is reached

    def _handle_interrupt(self, accumulated_text: str):
        """Handle streaming interrupt - add partial response to context."""
        # Create partial response with what we received so far
        partial_response = Response(
            id="interrupted",
            model=self.llm.model,
            message=Message(role="assistant", text=accumulated_text),
            usage=None
        )
        self.context.add_message(partial_response)

        # Fix any unmatched tool calls from previous operations
        self.context.fix_orphaned_results()
        self.context.fix_missing_ids()

        # Cleanup LLM streaming resources if needed
        if hasattr(self.llm, 'cleanup_stream'):
            self.llm.cleanup_stream()


    def set_system_prompt(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.context.set_system_prompt(system_prompt)
        

    def get_total_cost(self):
        return self.context.get_total_cost()

    def get_total_tokens(self):
        return self.context.get_total_tokens()

    
    def __str__(self):
        s = '--- Agent ---'
        s += f'\nLLM: {self.llm}'
        s += f'\nTools: {[tool.get_name() for tool in self.llm.tools]}'
        s += f'\nContext: {self.context}'
        return s