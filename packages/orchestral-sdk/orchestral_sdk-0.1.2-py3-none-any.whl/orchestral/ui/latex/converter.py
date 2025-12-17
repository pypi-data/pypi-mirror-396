"""
LaTeX converter for Orchestral Message objects.

Converts Message objects (with nested tool calls and results) to LaTeX code
that uses the orchestralmessage environments defined in orchestral.tex.
"""

import re
from typing import List, Dict, Optional
from orchestral.context.message import Message
from orchestral.llm.base.tool_call import ToolCall


class LatexConverter:
    """Convert Orchestral Message objects to LaTeX."""

    def __init__(self):
        pass

    def convert_markdown_formatting(self, text: str) -> str:
        """
        Convert basic markdown formatting to LaTeX before escaping.

        Handles:
        - Links: [text](url) -> \href{url}{text}
        - Bold: **text** -> \textbf{text}
        - Italic: *text* -> \textit{text}
        - Inline code: `code` -> \texttt{code}
        """
        if not text:
            return ""

        # Convert links: [text](url) -> \href{url}{text}
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\\href{\2}{\1}', text)

        # Convert bold: **text** -> \textbf{text}
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\\textbf{\1}', text)

        # Convert italic: *text* -> \textit{text} (but not if part of **)
        # This is tricky - we need to avoid matching * that are part of **
        text = re.sub(r'(?<!\*)\*(?!\*)([^\*]+)\*(?!\*)', r'\\textit{\1}', text)

        # Convert inline code: `code` -> \texttt{code}
        text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', text)

        return text

    def escape_latex(self, text: str, protect_commands: bool = False) -> str:
        """
        Escape LaTeX special characters in text.

        Args:
            text: Text to escape
            protect_commands: If True, preserve \texttt{} and other commands
        """
        if not text:
            return ""

        # Convert markdown formatting first (before escaping)
        text = self.convert_markdown_formatting(text)

        # Protect LaTeX commands from escaping
        protected = []
        if protect_commands:
            # Find and protect LaTeX commands: \textbf{...}, \href{...}{...}, etc.
            # Use alphanumeric-only placeholders to avoid escaping issues
            def protect_command(match):
                idx = len(protected)
                protected.append(match.group(0))
                return f"XLATEXPROTECTEDX{idx}XLATEXPROTECTEDX"

            # Match \command{content} or \command{arg1}{arg2}
            # We need to handle nested braces carefully
            patterns = [
                r'\\href\{[^}]+\}\{[^}]+\}',  # \href{url}{text}
                r'\\textbf\{[^}]+\}',          # \textbf{text}
                r'\\textit\{[^}]+\}',          # \textit{text}
                r'\\texttt\{[^}]+\}',          # \texttt{text}
            ]

            for pattern in patterns:
                text = re.sub(pattern, protect_command, text)

        # First, escape backslashes that aren't part of our protected LaTeX commands
        # Do this BEFORE other escaping to avoid double-escaping
        result = text
        result = re.sub(r'\\(?!XLATEXPROTECTEDX)', r'\\textbackslash{}', result)

        # Now escape other special characters
        result = result.replace('~', r'\textasciitilde{}')
        result = result.replace('^', r'\textasciicircum{}')
        result = result.replace('&', r'\&')
        result = result.replace('%', r'\%')
        result = result.replace('$', r'\$')
        result = result.replace('#', r'\#')
        result = result.replace('_', r'\_')
        result = result.replace('{', r'\{')
        result = result.replace('}', r'\}')

        # Restore protected commands
        for idx, cmd in enumerate(protected):
            result = result.replace(f"XLATEXPROTECTEDX{idx}XLATEXPROTECTEDX", cmd)

        return result

    def detect_code_blocks(self, text: str) -> List[Dict]:
        """
        Detect markdown code blocks in text.

        Returns list of dicts with:
        - start, end: indices
        - language: detected language (or 'text')
        - code: the code content
        """
        blocks = []
        pattern = r'```(\w*)\n(.*?)```'

        for match in re.finditer(pattern, text, re.DOTALL):
            lang = match.group(1) or 'text'
            code = match.group(2).strip()
            blocks.append({
                'start': match.start(),
                'end': match.end(),
                'language': lang,
                'code': code,
                'full_match': match.group(0)
            })

        return blocks

    def format_code_block(self, code: str, language: str = 'text') -> str:
        """
        Format a code block for LaTeX using minted for syntax highlighting.

        Args:
            code: The code content
            language: Language for syntax highlighting (python, bash, etc.)
        """
        # Map common language identifiers to minted lexers
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'sh': 'bash',
            'shell': 'bash',
            'txt': 'text',
            '': 'text',
        }

        # Normalize language name
        lang = language.lower().strip()
        lang = language_map.get(lang, lang)

        # Convert tabs to 4 spaces to avoid ^^I rendering in minted
        code = code.replace('\t', '    ')

        # Use minted for syntax highlighting
        # The style and other options are configured globally in orchestral.tex
        return f"\\begin{{minted}}{{{lang}}}\n{code}\n\\end{{minted}}"

    def detect_lists(self, text: str) -> List[Dict]:
        """
        Detect markdown-style lists in text.

        Returns list of dicts with:
        - start, end: indices
        - type: 'ordered' or 'unordered'
        - items: list of item texts
        """
        lists = []
        lines = text.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for ordered list (1. 2. 3. or 1) 2) 3))
            ordered_match = re.match(r'^\s*(\d+)[.)] (.+)$', line)
            # Check for unordered list (- * +)
            unordered_match = re.match(r'^\s*[-*+] (.+)$', line)

            if ordered_match or unordered_match:
                # Found start of a list
                list_type = 'ordered' if ordered_match else 'unordered'
                items = []
                start_line = i

                # Collect all consecutive list items
                while i < len(lines):
                    line = lines[i]

                    if list_type == 'ordered':
                        match = re.match(r'^\s*\d+[.)] (.+)$', line)
                    else:
                        match = re.match(r'^\s*[-*+] (.+)$', line)

                    if match:
                        items.append(match.group(1))
                        i += 1
                    elif line.strip() == '':
                        # Empty line might continue the list
                        i += 1
                        # Check if next line is also a list item
                        if i < len(lines):
                            next_line = lines[i]
                            if list_type == 'ordered':
                                next_match = re.match(r'^\s*\d+[.)] (.+)$', next_line)
                            else:
                                next_match = re.match(r'^\s*[-*+] (.+)$', next_line)

                            if not next_match:
                                # End of list
                                break
                    else:
                        # Not a list item, end of list
                        break

                if items:
                    # Calculate character positions
                    start_pos = sum(len(lines[j]) + 1 for j in range(start_line))  # +1 for \n
                    end_pos = sum(len(lines[j]) + 1 for j in range(i))

                    lists.append({
                        'start': start_pos,
                        'end': end_pos,
                        'type': list_type,
                        'items': items,
                        'start_line': start_line,
                        'end_line': i
                    })
            else:
                i += 1

        return lists

    def format_list(self, list_type: str, items: List[str]) -> str:
        """
        Format a list as LaTeX enumerate or itemize.

        Args:
            list_type: 'ordered' or 'unordered'
            items: list of item texts (already escaped)
        """
        env = 'enumerate' if list_type == 'ordered' else 'itemize'

        lines = [f"\\begin{{{env}}}"]
        for item in items:
            # Escape the item text
            escaped_item = self.escape_latex(item, protect_commands=True)
            lines.append(f"  \\item {escaped_item}")
        lines.append(f"\\end{{{env}}}")

        return '\n'.join(lines)

    def process_text_content(self, text: str) -> str:
        """
        Process text content: escape LaTeX, handle code blocks, lists, etc.
        """
        if not text:
            return ""

        # Find code blocks and lists
        code_blocks = self.detect_code_blocks(text)
        lists = self.detect_lists(text)

        # Combine all special regions (code blocks and lists) and sort by position
        special_regions = []

        for block in code_blocks:
            special_regions.append({
                'start': block['start'],
                'end': block['end'],
                'type': 'code',
                'data': block
            })

        for lst in lists:
            special_regions.append({
                'start': lst['start'],
                'end': lst['end'],
                'type': 'list',
                'data': lst
            })

        # Sort by start position
        special_regions.sort(key=lambda x: x['start'])

        if not special_regions:
            # No special formatting - just escape and return
            return self.escape_latex(text, protect_commands=True)

        # Process text with special regions
        result = []
        last_end = 0

        for region in special_regions:
            # Add text before this region (escaped)
            before = text[last_end:region['start']]
            if before:
                result.append(self.escape_latex(before, protect_commands=True))

            # Add the special region (formatted)
            if region['type'] == 'code':
                block = region['data']
                result.append("\n\n" + self.format_code_block(block['code'], block['language']) + "\n\n")
            elif region['type'] == 'list':
                lst = region['data']
                result.append("\n\n" + self.format_list(lst['type'], lst['items']) + "\n\n")

            last_end = region['end']

        # Add any remaining text
        after = text[last_end:]
        if after:
            result.append(self.escape_latex(after, protect_commands=True))

        return ''.join(result)

    def format_tool_arguments(self, arguments: Dict) -> str:
        """
        Format tool arguments for display in title.

        For simple args, shows them inline. For complex args (like code),
        returns empty string and we'll show args in body instead.
        """
        if not arguments:
            return ""

        # Check if any arg looks like code (long, multi-line, or has 'code' in key name)
        has_complex_args = False
        for key, value in arguments.items():
            if 'code' in key.lower() or (isinstance(value, str) and (len(value) > 50 or '\n' in value)):
                has_complex_args = True
                break

        if has_complex_args:
            return ""  # Will show in body

        # Format simple args for title
        arg_strs = []
        for key, value in arguments.items():
            # Truncate long values
            val_str = str(value)
            if len(val_str) > 30:
                val_str = val_str[:27] + "..."
            arg_strs.append(f"{key}={val_str}")

        return ", ".join(arg_strs)

    def format_tool_body(self, tool_call: ToolCall, tool_result: Optional[Message]) -> str:
        """
        Format the body content of a tool panel.

        Shows arguments (if complex) and the result/output.
        """
        parts = []

        # Show complex arguments in body
        has_complex_args = False
        for key, value in tool_call.arguments.items():
            if 'code' in key.lower() or (isinstance(value, str) and (len(value) > 50 or '\n' in value)):
                has_complex_args = True

                # Show this argument
                parts.append(f"\\textbf{{{self.escape_latex(key)}:}}\n\n")

                if 'code' in key.lower() and isinstance(value, str):
                    # It's code - use verbatim
                    parts.append(self.format_code_block(value, language='python'))
                else:
                    # Long text - use verbatim
                    parts.append(self.format_code_block(value, language='text'))

                parts.append("\n\n")

        # Show result/output
        if tool_result:
            if has_complex_args:
                parts.append("\\textbf{Output:}\n\n")

            if tool_result.text:
                # Always format tool output as monospace code
                output_text = tool_result.text.strip()
                parts.append(self.format_code_block(output_text, language='text'))

        return ''.join(parts)

    def convert_message_to_latex(self, message: Message,
                                   all_messages: Optional[List[Message]] = None,
                                   message_index: Optional[int] = None) -> str:
        """
        Convert a single Message to LaTeX.

        Args:
            message: The message to convert
            all_messages: Full message list (needed to find tool results)
            message_index: Index of this message in all_messages

        Returns:
            LaTeX code string
        """

        if message.role == 'user':
            return self._convert_user_message(message)
        elif message.role == 'assistant':
            return self._convert_assistant_message(message, all_messages, message_index)
        elif message.role == 'system':
            return self._convert_system_message(message)
        elif message.role == 'tool':
            # Tool messages are handled as part of assistant messages
            # Should not be called directly
            return ""
        else:
            # Unknown role - treat as generic message
            return self._convert_generic_message(message)

    def _convert_user_message(self, message: Message) -> str:
        """Convert user message to LaTeX."""
        content = self.process_text_content(message.text or "")
        # Indent content by 4 spaces for readability
        indented_content = '\n'.join('    ' + line if line.strip() else '' for line in content.split('\n'))

        return f"""\\begin{{orchestralusermessage}}
{indented_content}
\\end{{orchestralusermessage}}"""

    def _convert_system_message(self, message: Message) -> str:
        """Convert system message to LaTeX."""
        content = self.process_text_content(message.text or "")
        # Indent content by 4 spaces for readability
        indented_content = '\n'.join('    ' + line if line.strip() else '' for line in content.split('\n'))

        return f"""\\begin{{orchestralsystemmessage}}
{indented_content}
\\end{{orchestralsystemmessage}}"""

    def _convert_assistant_message(self, message: Message,
                                     all_messages: Optional[List[Message]] = None,
                                     message_index: Optional[int] = None) -> str:
        """
        Convert assistant message to LaTeX.

        This is the complex case - may include text and/or tool calls.
        Tool calls need to be matched with their results from subsequent tool messages.
        Also includes any continuation assistant messages after tools.
        """
        parts = []

        parts.append("\\begin{orchestralagentmessage}")

        # Add assistant's text content if any
        if message.text and message.text.strip():
            content = self.process_text_content(message.text)
            indented_content = '\n'.join('    ' + line if line.strip() else '' for line in content.split('\n'))
            parts.append(indented_content)

        # Add tool calls (if any) - including subsequent assistant messages with more tool calls
        if message.tool_calls and all_messages and message_index is not None:
            # Process all tool calls in this agent panel (may span multiple assistant messages)
            current_index = message_index

            while current_index < len(all_messages):
                current_msg = all_messages[current_index]

                # Stop if we hit a user or system message (different turn)
                if current_msg.role in ('user', 'system'):
                    break

                # Process assistant messages with tool calls
                if current_msg.role == 'assistant' and current_msg.tool_calls:
                    # Find corresponding tool result messages
                    tool_results_map = self._match_tool_results(current_msg.tool_calls,
                                                                 all_messages,
                                                                 current_index)

                    for tool_call in current_msg.tool_calls:
                        tool_latex = self._convert_tool_call(tool_call, tool_results_map.get(tool_call.id))
                        # Indent the entire tool block
                        indented_tool = '\n'.join('    ' + line if line.strip() else '' for line in tool_latex.split('\n'))
                        parts.append("\n\n" + indented_tool)

                # Collect continuation text from assistant messages without tool_calls
                elif current_msg.role == 'assistant' and not current_msg.tool_calls:
                    if current_msg.text and current_msg.text.strip():
                        content = self.process_text_content(current_msg.text)
                        indented_content = '\n'.join('    ' + line if line.strip() else '' for line in content.split('\n'))
                        parts.append("\n\n" + indented_content)

                current_index += 1

        parts.append("\n\\end{orchestralagentmessage}")

        return '\n'.join(parts)

    def _convert_tool_call(self, tool_call: ToolCall, tool_result: Optional[Message]) -> str:
        """
        Convert a tool call (and its result) to LaTeX.

        Creates a nested orchestraltoolmessage environment.
        """
        # Format title: "ToolName: args" or just "ToolName"
        args_str = self.format_tool_arguments(tool_call.arguments)

        if args_str:
            title = f"{tool_call.tool_name}: \\texttt{{{self.escape_latex(args_str)}}}"
        else:
            title = tool_call.tool_name

        # Format body
        body = self.format_tool_body(tool_call, tool_result)
        # Indent body content by 4 spaces for readability
        indented_body = '\n'.join('    ' + line if line.strip() else '' for line in body.split('\n'))

        return f"""\\begin{{orchestraltoolmessage}}{{{title}}}
{indented_body}
\\end{{orchestraltoolmessage}}"""

    def _match_tool_results(self, tool_calls: List[ToolCall],
                             all_messages: List[Message],
                             assistant_index: int) -> Dict[str, Message]:
        """
        Match tool calls with their result messages.

        Looks for tool messages after the assistant message with matching tool_call_id.

        Returns dict: tool_call_id -> tool result Message
        """
        results = {}

        # Get tool call IDs
        tool_call_ids = {tc.id for tc in tool_calls}

        # Search subsequent messages for tool results
        for i in range(assistant_index + 1, len(all_messages)):
            msg = all_messages[i]

            # Stop when we hit a user or system message (different turn)
            if msg.role in ('user', 'system'):
                break

            # Match tool result
            if msg.role == 'tool' and msg.tool_call_id in tool_call_ids:
                results[msg.tool_call_id] = msg

        return results

    def _find_continuation_messages(self, tool_calls: List[ToolCall],
                                      all_messages: List[Message],
                                      assistant_index: int) -> str:
        """
        Find continuation assistant messages after tool results.

        After an assistant message with tool calls and their results,
        there may be additional assistant messages that are part of the same panel.
        This collects their text.

        Returns combined text from continuation messages.
        """
        continuation_texts = []

        # Get tool call IDs to know when we've passed all tool results
        tool_call_ids = {tc.id for tc in tool_calls}
        found_tool_results = set()

        # Search subsequent messages
        for i in range(assistant_index + 1, len(all_messages)):
            msg = all_messages[i]

            # Stop when we hit a user or system message (different turn)
            if msg.role in ('user', 'system'):
                break

            # Track tool results
            if msg.role == 'tool' and msg.tool_call_id in tool_call_ids:
                found_tool_results.add(msg.tool_call_id)
                continue

            # Collect assistant messages that come after tools
            if msg.role == 'assistant':
                # Only include if we've seen at least some tool results
                # (otherwise it might be a different panel)
                if found_tool_results and msg.text and msg.text.strip():
                    continuation_texts.append(msg.text.strip())

                # Stop if this assistant message has its own tool calls
                # (that would be a new panel)
                if msg.tool_calls:
                    break

        return '\n\n'.join(continuation_texts)

    def _convert_generic_message(self, message: Message) -> str:
        """Convert unknown message type to LaTeX."""
        content = self.process_text_content(message.text or "")
        role = message.role or "Unknown"

        # Use user message style as default
        return f"""\\begin{{orchestralusermessage}}
\\textbf{{{role}:}} {content}
\\end{{orchestralusermessage}}"""
