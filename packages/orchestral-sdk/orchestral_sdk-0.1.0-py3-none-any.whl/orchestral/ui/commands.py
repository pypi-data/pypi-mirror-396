def handle_command(command, agent, console, streaming_display=None):
    command = command.strip()
    if command == 'reset':
        agent.context.clear()
        console.print("[bold green]Context reset.[/bold green]")
        if streaming_display:
            streaming_display.finalize_and_redraw()
    elif command == 'undo':
        success = agent.context.undo()
        if success:
            console.print("[bold green]Undone. Last user message and responses removed.[/bold green]")
            if streaming_display:
                streaming_display.finalize_and_redraw()
        else:
            console.print("[bold yellow]Nothing to undo. No user messages in context.[/bold yellow]")
    elif command == 'cost':
        console.print(f"[bold blue]Total cost so far: ${agent.get_total_cost():.5f}[/bold blue]")
    elif command.startswith('save'):
        raise NotImplementedError("Save command is not implemented yet.")
        filename = command.split(' ', 1)[1] if ' ' in command else None
        if not filename:
            console.print("[bold red]Please provide a filename.[/bold red]")
            return
        try:
            print(f"Saving context to {filename}...")
            # with open(filename, 'w') as f:
            #     f.write(agent.context)
            # console.print(f"[bold green]Context saved to {filename}.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error saving context: {e}[/bold red]")
    elif command == 'help':
        console.print("[bold yellow]Available commands:[/bold yellow]")
        console.print("/reset - Reset the conversation context")
        console.print("/undo - Remove the last user message and all responses")
        console.print("/cost - Display total cost of the conversation")
        console.print("/context - Display the current conversation context")
        console.print("/save <filename> - Save the current context to a file")
        console.print("/help - Show this help message")
    else:
        console.print(f"[bold red]Unknown command: {command}[/bold red]")
        console.print("Type /help for a list of commands.")
