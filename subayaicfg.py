import struct
from serial import Serial

MAX_KEYS = 16
CONFIG_FMT = f"<{MAX_KEYS}B{MAX_KEYS}H{MAX_KEYS}HH"
CONFIG_SIZE = struct.calcsize(CONFIG_FMT)

CMD_KEY_COUNT = 0xBB
CMD_CONFIG_REQUEST = 0xCC
CMD_CONFIG_UPDATE = 0xDD
CMD_CONFIG_RESET = 0xEE

class Config:
    key_codes: list[int]
    key_thresholds: list[int]
    discharge_delays: list[int]
    debounce_delay: int

    @classmethod
    def from_bytes(cls, raw: bytes):
        inst = cls.__new__(cls)
        data = struct.unpack(CONFIG_FMT, raw)

        inst.key_codes = list(data[0:MAX_KEYS])
        inst.key_thresholds = list(fields[MAX_KEYS:MAX_KEYS * 2])
        inst.discharge_delays = list(field[MAX_KEYS * 2:MAX_KEYS * 3])
        inst.debounce_delay = fields[MAX_KEYS * 3]

        return inst
