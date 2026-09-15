import functools
from serial import Serial
from enum import IntEnum
from typing import Self, Optional
from subayai.config import Config

def requires_connection(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._conn is None:
            raise RuntimeError(f"Not connected - did you call connect?")

        return func(self, *args, **kwargs)

    return wrapper

class Command(IntEnum):
    ACK = 0x01,
    NAK = 0x02,
    KEY_COUNT = 0xBB,
    CONFIG_REQUEST = 0xCC,
    CONFIG_UPDATE = 0xDD,
    CONFIG_RESET = 0xEE

class Protocol:
    port: str
    baud: int
    _conn: Optional[Serial]

    def __init__(self, port: str, baud: int) -> None:
        self.port = port
        self.baud = baud
        self._conn = None

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, *args) -> bool:
        self.close()
        return False

    def connect(self) -> None:
        self._conn = Serial(self.port, self.baud)

    def _read_response(self, expected: Command, size: int) -> bytes:
        raw = self._conn.read(1 + size)
        cmd, payload = raw[0], raw[1:]

        if cmd != expected:
            raise RuntimeError(f"Unexpected response command: got {cmd!r}, expected {expected!r}")

        return payload

    def _expect_ack(self, context: str) -> None:
        raw = self._conn.read(1)
        response = raw[0]

        match response:
            case Command.ACK:
                return
            case Command.NAK:
                raise RuntimeError(f"Device rejected config {context} - was it a bad connection?")
            case _:
                raise RuntimeError(f"Unexpected response byte during config {context}: {response!r}")

    @requires_connection
    def request_config(self) -> Config:
        self._conn.write(bytes([Command.CONFIG_REQUEST]))
        payload = self._read_response(Command.CONFIG_UPDATE, Config.SIZE)
        return Config.from_bytes(payload)

    @requires_connection
    def update_config(self, config: Config) -> None:
        self._conn.write(bytes([Command.CONFIG_UPDATE]) + config.to_bytes())
        self._expect_ack("update")

    @requires_connection
    def reset_config(self) -> None:
        self._conn.write(bytes([Command.CONFIG_RESET]))
        self._expect_ack("reset")

    def close(self) -> None:
        if self._conn:
            self._conn.close()
