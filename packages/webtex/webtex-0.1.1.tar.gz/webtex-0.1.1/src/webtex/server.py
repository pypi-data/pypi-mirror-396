import asyncio
import os
import time
import threading
from contextlib import asynccontextmanager

import fastapi
import uvicorn


class WebTexServer:
    _STATIC_FILES = ["index.html", "main.css", "display.js", "math.js"]


    def __init__(
        self,
        *,
        title: str = "WebTex",
        darkmode: bool | None = True,
        verbose: bool | None = False,
    ):
        self.title = title
        self.darkmode = darkmode
        self.verbose = verbose
        self._app = fastapi.FastAPI(lifespan=self._lifespan)
        self._static = self._load_static()
        self._server = None
        self._running: bool = True
        self._port: int | None = None
        self._wsconnections: list[fastapi.WebSocket] = []
        self._current_display = {}
        self._setup_routes()
        self._loop = None
        self._id_state = 0


    @property
    def is_running(self) -> bool:
        return self._running
    

    @property
    def port(self) -> int:
        if not self.is_running:
            raise RuntimeError("Server not running.")
        return self._port


    @asynccontextmanager
    async def _lifespan(self, app: fastapi.FastAPI):
        self._loop = asyncio.get_running_loop()
        yield


    def _setup_routes(self) -> None:
        @self._app.get("/", response_class=fastapi.responses.HTMLResponse)
        async def get_index():
            return self._static["index.html"]
        
        @self._app.get("/main.css")
        async def get_main_css():
            return fastapi.responses.Response(self._static["main.css"], media_type="text/css")

        @self._app.get("/display.js")
        async def get_display_js():
            return fastapi.responses.Response(self._static["display.js"], media_type="application/javascript")
        
        @self._app.get("/math.js")
        async def get_math_js():
            return fastapi.responses.Response(self._static["math.js"], media_type="application/javascript")
        
        @self._app.get("/config.js")
        async def get_config_js():
            return fastapi.responses.Response(self._get_config(), media_type="application/javascript")

        @self._app.websocket("/websocket")
        async def websocket_endpoint(websocket: fastapi.WebSocket):
            await websocket.accept()
            await websocket.send_json(self._current_display)
            self._wsconnections.append(websocket)
            try:
                while True:
                    await websocket.receive_text()
            except fastapi.WebSocketDisconnect:
                pass
            finally:
                if websocket in self._wsconnections:
                    self._wsconnections.remove(websocket)


    def _load_static(self) -> dict[str, str]:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        static_path = os.path.join(current_directory, "static/")
        output = {}
        for filename in self._STATIC_FILES:
            with open(os.path.join(static_path, filename), 'r') as file:
                output[filename] = file.read()
        return output
    

    def _get_config(self) -> str:
        mode = 'dark' if self.darkmode else 'light'
        return f'const webTexConfig = {{"mode": "{mode}", "title": "{self.title}"}}'


    async def _update(self) -> None:     
        data = self._current_display
        dead: list[fastapi.WebSocket] = []

        for ws in self._wsconnections:
            try:
                await ws.send_json(data)
            except fastapi.WebSocketDisconnect:
                dead.append(ws)

        for ws in dead:
            if ws in self._wsconnections:
                self._wsconnections.remove(ws)


    def _run_in_loop(self, func, *args, **kwargs) -> None:
        check_count = 30
        while self._loop is None and check_count > 0:
            time.sleep(0.1)
            check_count -= 1
        if check_count == 0:
            return
        asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self._loop)


    def _make_unnamed_keyname(self) -> str:
        id_state = self._id_state
        self._id_state += 1
        return f"__unnamed_{id_state}"


    def update(self) -> None:
        self._run_in_loop(self._update)


    def display(self, data: dict, *, _bypass_check: bool = False) -> None:
        if not _bypass_check:
            if callable(getattr(data, "keys", None)):
                for key in data.keys():
                    if key.startswith("__unnamed_"):
                        raise KeyError(f"Invalid key {key} is reverved name")
            else:
                return self.display({self._make_unnamed_keyname(): data}, _bypass_check=True)

        self._current_display = {
            key: value
            for key, value in data.items()
        }

        self.update()


    def add(
        self, 
        data: dict, 
        replace: bool = False,
        *, _bypass_check: bool = False,
    ) -> None:
        if not _bypass_check:
            if callable(getattr(data, "keys", None)):
                for key in data.keys():
                    if key.startswith("__unnamed_"):
                        raise KeyError(f"Invalid key \"{key}\" is reverved name")
            else:
                return self.add({self._make_unnamed_keyname(): data}, _bypass_check=True)
        
        for key in data.keys():
            if not replace and key in self._current_display:
                raise KeyError(f"Key \"{key}\" already displayed")
            self._current_display[key] = data[key]

        self.update()


    def clear(self) -> None:
        self._current_display = {}
        self.update()


    def _run(self, host: str, port: int) -> None:
        config = uvicorn.Config(
            self._app, 
            host=host, 
            port=port, 
            log_level=('info' if self.verbose else 'critical')
        )
        self._server = uvicorn.Server(config)
        self._server.run()
        self._running = True
        self._port = port


    def stop(self) -> None:
        if not self.is_running:
            raise RuntimeError("Server not running.")
        
        self._server.should_exit = True

        if self._loop is not None:
            server = self._server

            def _exit():
                server.should_exit = True

            try:
                self._loop.call_soon_threadsafe(_exit)
            except RuntimeError:
                pass

        self._running = False
        self._port = None


    def listen(
        self, 
        port: int = 80, 
        *, 
        host: str | None = "0.0.0.0",
        daemon: bool | None = True
    ) -> None:
        if daemon:
            server_thread = threading.Thread(target=self._run, args=(host, port), daemon=True)
            server_thread.start()
        else:
            self._run(host, port)