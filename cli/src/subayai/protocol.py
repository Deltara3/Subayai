import struct
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
    KEY_COUNT = 0x10,
    CONFIG_REQUEST = 0x20,
    CONFIG_UPDATE = 0x21,
    CONFIG_RESET = 0x22,
    SENSE_START = 0x31,
    SENSE_STOP = 0x32,
    SENSE_REQUEST = 0x33,
    SENSE_STATE = 0x34

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
                raise RuntimeError(f"Device rejected command {context} - was it a bad connection?")
            case _:
                raise RuntimeError(f"Unexpected response byte during command {context}: {response!r}")

    @requires_connection
    def request_config(self) -> Config:
        self._conn.write(bytes([Command.CONFIG_REQUEST]))
        payload = self._read_response(Command.CONFIG_UPDATE, Config.SIZE)
        return Config.from_bytes(payload)

    @requires_connection
    def update_config(self, config: Config) -> None:
        self._conn.write(bytes([Command.CONFIG_UPDATE]) + config.to_bytes())
        self._expect_ack("CONFIG_UPDATE")

    @requires_connection
    def reset_config(self) -> None:
        self._conn.write(bytes([Command.CONFIG_RESET]))
        self._expect_ack("CONFIG_RESET")

    @requires_connection
    def enter_sense(self) -> None:
        self._conn.write(bytes([Command.SENSE_START]))
        self._expect_ack("SENSE_START")

    @requires_connection
    def leave_sense(self) -> None:
        self._conn.write(bytes([Command.SENSE_STOP]))
        self._expect_ack("SENSE_STOP")

    @requires_connection
    def request_sense(self) -> list[int]:
        self._conn.write(bytes([Command.SENSE_REQUEST]))
        payload = self._read_response(Command.SENSE_STATE, 2 * Config.MAX_KEYS)
        return list(struct.unpack(f"<{Config.MAX_KEYS}H", payload))

    def close(self) -> None:
        if self._conn:
            self._conn.close()
