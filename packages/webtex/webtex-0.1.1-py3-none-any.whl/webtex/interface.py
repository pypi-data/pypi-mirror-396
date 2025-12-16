from webtex.server import WebTexServer


_SERVER: WebTexServer | None = None


def run(
    port: int = 80,
    darkmode: bool = True,
    verbose: bool = False,
    host: str = "0.0.0.0",
    title: str = "WebTex",
) -> None:
    global _SERVER

    if _SERVER is not None and _SERVER.is_running:
        raise RuntimeError(f"Server is already runnning on port {_SERVER.port}")
    else:
        _SERVER = WebTexServer(title=title, darkmode=darkmode, verbose=verbose)
        _SERVER.listen(port, host=host, daemon=True)


def stop() -> None:
    if _SERVER is None or not _SERVER.is_running:
        raise RuntimeError("Server not running")
    
    _SERVER.stop()


def update() -> None:
    if _SERVER is None or not _SERVER.is_running:
        raise RuntimeError("Server not running")
    
    _SERVER.update()


def display(data: dict) -> None:
    if _SERVER is None or not _SERVER.is_running:
        raise RuntimeError("Server not running")
    
    _SERVER.display(data)


def clear() -> None:
    if _SERVER is None or not _SERVER.is_running:
        raise RuntimeError("Server not running")
    
    _SERVER.clear()


def add(data: dict) -> None:
    if _SERVER is None or not _SERVER.is_running:
        raise RuntimeError("Server not running")
    
    _SERVER.add(data) 