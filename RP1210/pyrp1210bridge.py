import time
from collections import deque
from typing import Any, Optional

import can
from can import Message, CanProtocol, CanOperationError

import RP1210


class PyRP1210Bridge(can.bus.BusABC):
    def __init__(
            self,
            channel: Any,
            bitrate: int = 500_000,
            poll_interval: float = 0.01,
            **kwargs: object,
    ):
        """
        :param channel: String in format "DLL_NAME[:DEVICE_ID[:CHANNEL]]"
                        e.g., "PEAKRP32", "PEAKRP32:1", "PEAKRP32:1:2"
        """
        self._rx_buffer = deque()
        self.poll_interval = poll_interval
        self.bitrate = bitrate

        parts = channel.split(":")
        if len(parts) > 3 or len(parts) < 1:
            raise ValueError(f"Invalid channel format '{channel}'. Expected 'DLL[:ID[:CH]]'")

        raw_dll = parts[0]
        raw_id = parts[1] if len(parts) > 1 else "0"
        raw_ch = parts[2] if len(parts) > 2 else "1"
        if not raw_dll.isalnum():
            raise ValueError(f"Invalid RP1210 Driver Name '{raw_dll}'. Must be alphanumeric.")
        self.dll_name = raw_dll

        try:
            self.device_id = int(raw_id)
            self.device_channel = int(raw_ch)
        except ValueError:
            raise ValueError(f"Device ID and Channel must be integers. Got ID='{raw_id}', CH='{raw_ch}'")

        if not (0 <= self.device_id <= 255):
            raise ValueError(f"Device ID {self.device_id} out of range (0-255)")

        if not (0 <= self.device_channel <= 255):
            raise ValueError(f"Device Channel {self.device_channel} out of range (0-255)")

        self.channel_info = f"RP1210:{channel}"
        self._can_protocol = CanProtocol.CAN_20

        self.interface = RP1210.RP1210Client()
        self.interface.setVendor(self.dll_name)
        self.interface.setDevice(self.device_id)

        conn_str = f"CAN:Baud={self.bitrate},Channel={self.device_channel}"
        self.interface.connect(conn_str.encode("utf-8"))

        self.interface.setAllFiltersToPass()

        super().__init__(
            channel=channel,
            bitrate=bitrate,
            poll_interval=poll_interval,
            **kwargs,
        )

    def send(self, msg: Message, timeout: Optional[float] = None) -> None:
        arb_id = msg.arbitration_id
        self.interface.tx(b"\x01" + arb_id.to_bytes(4, "big") + msg.data)

    def _recv_internal(self, timeout: Optional[float] = None):
        if self._rx_buffer:
            return self._rx_buffer.popleft(), False

        start = time.monotonic()

        while True:
            while True:
                res = self.interface.rx(buffer_size=256 + 5, blocking=False)

                if res is None or len(res) == 0:
                    break  # Hardware queue is empty

                timestamp = int.from_bytes(res[0:4], "big")
                flags = res[4]
                arbitration_id = int.from_bytes(res[5: 5 + 4], "big")
                dlc = len(res) - 4 - 5
                if dlc > 0:
                    data = res[9:]
                else:
                    data = b""

                if flags != 0xFF:
                    is_extended = bool(flags & 0x01)
                    is_remote = bool((flags >> 1) & 0x01)
                    is_error = bool((flags >> 2) & 0x01)
                else:
                    is_extended = True
                    is_remote = False
                    is_error = False

                if is_error:
                    raise CanOperationError("RP1210 error reported")

                msg = Message(
                    arbitration_id=arbitration_id,
                    is_extended_id=is_extended,
                    timestamp=timestamp,
                    is_remote_frame=is_remote,
                    dlc=dlc,
                    data=data,
                    channel=self.channel_info,
                    is_rx=True,
                )
                self._rx_buffer.append(msg)

            if self._rx_buffer:
                return self._rx_buffer.popleft(), False

            if timeout == 0:
                return None, False

            if timeout is not None:
                if (time.monotonic() - start) >= timeout:
                    return None, False

            time.sleep(self.poll_interval)

    def shutdown(self) -> None:
        super().shutdown()
        self.interface.disconnect()
