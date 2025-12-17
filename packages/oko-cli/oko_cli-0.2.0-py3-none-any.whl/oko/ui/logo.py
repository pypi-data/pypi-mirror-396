from rich.console import Console

console = Console()

LOGO_OKO = """
    ███████    █████   ████    ███████   
  ███░░░░░███ ░░███   ███░   ███░░░░░███ 
 ███     ░░███ ░███  ███    ███     ░░███
░███      ░███ ░███████    ░███      ░███
░███      ░███ ░███░░███   ░███      ░███
░░███     ███  ░███ ░░███  ░░███     ███ 
 ░░░███████░   █████ ░░████ ░░░███████░  
   ░░░░░░░    ░░░░░   ░░░░    ░░░░░░░    
"""


def print_logo():
    """
    Imprime el logo de OKO cli
    """
    console.print(f"[medium_orchid]{LOGO_OKO}[/medium_orchid]")
