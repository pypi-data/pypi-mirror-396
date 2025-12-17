def format_status_code(status_code: int) -> str:
    if 200 <= status_code < 300:
        style = "status_ok"
    elif 300 <= status_code < 400:
        style = "status_info"
    elif 400 <= status_code < 500:
        style = "status_warn"
    else:
        style = "status_fail"

    return f"[{style}]{status_code}[/{style}]"


def format_http_method(method: str) -> str:
    method = method.upper()
    style = f"method_{method.lower()}"
    return f"[{style}]{method}[/{style}]"
