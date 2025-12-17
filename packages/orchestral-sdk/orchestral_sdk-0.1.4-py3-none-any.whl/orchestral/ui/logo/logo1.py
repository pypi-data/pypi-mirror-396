from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule

orchestral = """[bold blue]                   _                _              _   
                  ( )              ( )_           ( _) 
    __   ___   ___| |__    __   ___|  _) ___  ___ | | 
  / _ \(  __)/ ___)  _  \/ __ \  __) | (  __) _  )| | 
 ( (_) ) |  ( (___| | | |  ___/__  \ |_| | ( (_| || | 
  \___/(_)   \____)_) (_)\____)____/\__)_)  \__ _)___)[/]"""

group = Group(
    orchestral,
    Rule(style="white"),
    f'[bold bright_black]{' '*50}v3.0[/]',
)

logo1 = Panel.fit(
    group,
    title="[blue]Welcome to...[/]",
    title_align="left",
    border_style="white",
)

console = Console()

if __name__ == "__main__":
    console.print(logo1)
