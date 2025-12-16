from signal import SIGTERM, SIGKILL
from typing import Any
from nkv import NKVManager
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from os import kill


class MineServerManager:
    def __init__(self, servers_path: str = './servers', ) -> None:
        self.servers_path = servers_path

    def create_server(self, server_name: str, server_path: str, jar_name: str = 'paper-*.jar',
                      proxy_name: str | None = None, proxy_path: str | None = None) -> None:
        nkv: NKVManager = NKVManager(name=self._normalize_name(server_name=server_name), path=self.servers_path)
        nkv.write_batch(
            data={
                'name': server_name,
                'server_path': server_path,
                'proxy_name': proxy_name,
                'proxy_path': proxy_path,
                'jar_name': jar_name
            },
            beauty=True
        )

    def list_servers(self) -> list[str]:
        path = Path(self.servers_path).expanduser()
        servers: list[str] = []

        for file in path.iterdir():
            if file.suffix == '.nkv':
                servers.append(self._normalize_name(file.name))

        return servers

    def load_server(self, server_name: str) -> dict[str, Any] | None:
        path = Path(self.servers_path).expanduser()

        for file in path.iterdir():
            if self._normalize_name(file.name) == self._normalize_name(server_name):
                nkv = NKVManager(name=file.name, path=str(path))
                return nkv.read()

        return None

    def start_server(self, server_name: str) -> None:
        try:
            info = self.load_server_info(server_name=server_name)
            if info['status'] == 'started':
                print('\033[1;31mERRO! \033[1;34mServidor já rodando!')
                return
        except:
            pass

        server = self.load_server(server_name=server_name)
        nkv = NKVManager(name=self._data_name(server_name), path='./data')

        if not server:
            raise Exception(f'\033[1;31mServidor "{server_name}" não encontrado')

        server_path = str(Path(server['server_path']).expanduser())
        proxy = server['proxy_name']
        proxy_path = str(Path(server['proxy_path']).expanduser())
        jar = server.get('jar_name', 'paper-*.jar')

        server_process = Popen(
            ['java', '-Xmx4096M', '-jar', jar, 'nogui'],
            cwd=server_path,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            bufsize=1
        )
        output_thread = Thread(
            target=self._stream_output,
            args=(server_process, server_name),
            daemon=True
        )
        output_thread.start()

        nkv.write('status', 'started')
        nkv.write('server_name', server_name)
        nkv.write('server_pid', server_process.pid)

        if proxy is not None:
            proxy_process = Popen(
                [f'./{proxy}'],
                cwd=proxy_path,
                stdin=PIPE,
                stdout=PIPE,
                stderr=STDOUT,
                text=True,
                bufsize=1
            )
            nkv.write('proxy_name', proxy)
            nkv.write('proxy_pid', proxy_process.pid)

    def stop_server(self, server_name: str) -> None:
        server = self.load_server_info(server_name=server_name)
        server_pid: int = server['server_pid']

        try:
            kill(server_pid, SIGTERM)
            try:
                kill(server_pid, SIGKILL)
            except:
                pass
        except:
            pass

        proxy_pid: int = server['proxy_pid']

        if server_pid:
            try:
                kill(proxy_pid, SIGTERM)
                try:
                    kill(proxy_pid, SIGKILL)
                except:
                    pass
            except:
                pass

        nkv = NKVManager(name=self._data_name(server_name), path='./data')
        nkv.update('status', 'stopped')
        nkv.update('server_pid', None)
        nkv.update('proxy_pid', None)

    def load_server_info(self, server_name: str) -> dict[str, Any]:
        nkv = NKVManager(name=self._data_name(server_name), path='./data')
        return nkv.read()

    @staticmethod
    def _normalize_name(server_name: str) -> str:
        return server_name.replace('.nkv', '').lower()

    @staticmethod
    def _stream_output(process, server_name):
        for line in process.stdout:
            print(f"[{server_name}] {line.strip()}")

    def _data_name(self, name: str) -> str:
        name = self._normalize_name(name)
        return f'{name}_data'
