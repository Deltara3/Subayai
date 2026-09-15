import struct
from typing import Self
from dataclasses import dataclass

@dataclass
class Config:
    MAX_KEYS = 16
    MAX_KEY_CODE = 255
    MAX_THRESHOLD = 1000
    MAX_DISCHARGE_DELAY = 5000
    MAX_DEBOUNCE = 50000
    FORMAT = f"<{MAX_KEYS}B{MAX_KEYS}H{MAX_KEYS}HH"
    SIZE = struct.calcsize(FORMAT)

    key_codes: list[int]
    key_thresholds: list[int]
    discharge_delays: list[int]
    debounce_delay: int

    @classmethod
    def from_bytes(cls, raw: bytes) -> Self:
        data = struct.unpack(cls.FORMAT, raw)

        return cls(
            key_codes = list(data[0 : cls.MAX_KEYS]),
            key_thresholds = list(data[cls.MAX_KEYS : cls.MAX_KEYS * 2]),
            discharge_delays = list(data[cls.MAX_KEYS * 2 : cls.MAX_KEYS * 3]),
            debounce_delay = data[cls.MAX_KEYS * 3]
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.FORMAT,
            *self.key_codes,
            *self.key_thresholds,
            *self.discharge_delays,
            self.debounce_delay
        )
