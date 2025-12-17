from rich.theme import Theme

custom_theme = Theme(
    {
        # Mensajes generales
        "info": "cyan",
        "title": "orchid1",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        # Estructura lógica de pasos / procesos
        "step": "bold bright_blue",
        "label": "bold white",
        "value": "bright_cyan",
        "highlight": "bold magenta",
        # Resultados de API
        "status_ok": "bold green",
        "status_fail": "bold red",
        "status_warn": "bold yellow",
        "status_info": "cyan",
        # Para requests/responses
        "method_get": "bold bright_blue",
        "method_post": "bold green",
        "method_put": "bold yellow",
        "method_delete": "bold red",
        "method_patch": "bold magenta",
        # Para logs internos o debug
        "debug": "dim white",
        "trace": "dim cyan",
        "verbose": "bright_black",
        # Inputs y outputs
        "input": "bold white",
        "output": "bright_white",
        "prompt": "bold cyan",
        # Estética general
        "primary": "blue",
        "secondary": "bright_cyan",
        "accent": "bright_magenta",
        # Estilos de bloqueo o atención
        "critical": "bold reverse red",
        "important": "bold underline bright_white",
    }
)
