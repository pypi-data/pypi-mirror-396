from signal import SIGTERM, SIGKILL
from typing import Any
from nkv import NKVManager
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from os import kill


class MineServerManager:
    def __init__(self, servers_path: str = './servers', data_path: str = './data') -> None:
        self.servers_path = servers_path
        self.data_path = data_path

        Path(self.servers_path).mkdir(parents=True, exist_ok=True)
        Path(self.data_path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.replace('.nkv', '').lower().replace('-', '_')

    def _server_config(self, name: str) -> NKVManager:
        return NKVManager(
            name=self._normalize_name(name),
            path=self.servers_path
        )

    def _server_state(self, name: str) -> NKVManager:
        return NKVManager(
            name=self._normalize_name(name),
            path=self.data_path
        )

    def create_server(
            self,
            server_name: str,
            server_path: str,
            jar_name: str = 'paper-*.jar',
            proxy_name: str | None = None,
            proxy_path: str | None = None
    ) -> None:
        nkv = self._server_config(server_name)
        nkv.write_batch(
            {
                'name': server_name,
                'server_path': server_path,
                'jar_name': jar_name,
                'proxy_name': proxy_name,
                'proxy_path': proxy_path
            },
            beauty=True
        )

    def list_servers(self) -> list[str]:
        return [
            file.stem
            for file in Path(self.servers_path).iterdir()
            if file.suffix == '.nkv'
        ]

    def load_server(self, server_name: str) -> dict[str, Any] | None:
        nkv = self._server_config(server_name)
        try:
            return nkv.read()
        except:
            return None

    def start_server(self, server_name: str) -> None:
        state = self._server_state(server_name)

        try:
            info = state.read()
            if info.get('status') == 'started':
                print('❌ Servidor já está rodando')
                return
        except:
            pass

        server = self.load_server(server_name)
        if not server:
            raise Exception(f'Servidor "{server_name}" não encontrado')

        server_path = str(Path(server['server_path']).expanduser())
        jar = server.get('jar_name', 'paper-*.jar')
        proxy = server.get('proxy_name')
        proxy_path = server.get('proxy_path')

        server_process = Popen(
            ['java', '-Xmx4096M', '-jar', jar, 'nogui'],
            cwd=server_path,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            bufsize=1
        )

        Thread(
            target=self._stream_output,
            args=(server_process, server_name),
            daemon=True
        ).start()

        state.write_batch({
            'status': 'started',
            'server_pid': server_process.pid
        })

        if proxy and proxy_path:
            proxy_process = Popen(
                [f'./{proxy}'],
                cwd=str(Path(proxy_path).expanduser()),
                stdout=PIPE,
                stderr=STDOUT,
                text=True,
                bufsize=1
            )
            state.write('proxy_pid', proxy_process.pid)

    def stop_server(self, server_name: str) -> None:
        state = self._server_state(server_name)
        info = state.read()

        for key in ('server_pid', 'proxy_pid'):
            pid = info.get(key)
            if pid:
                try:
                    kill(pid, SIGTERM)
                    kill(pid, SIGKILL)
                except:
                    pass

        state.update_batch({
            'status': 'stopped',
            'server_pid': None,
            'proxy_pid': None
        })

    @staticmethod
    def _stream_output(process, server_name: str):
        for line in process.stdout:
            print(f"[{server_name}] {line.strip()}")
