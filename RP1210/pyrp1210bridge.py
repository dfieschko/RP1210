import time
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

        self.poll_interval = poll_interval
        self.bitrate = bitrate
        self.dll_name, self.device_id = channel.split(":")
        self.device_id = int(self.device_id)
        self.channel_info = f"RP1210:{channel}"
        self._can_protocol = CanProtocol.CAN_20

        self.interface = RP1210.RP1210Client()
        self.interface.setVendor(self.dll_name)
        self.interface.setDevice(self.device_id)

        self.interface.connect(b"CAN:Baud=" + str(self.bitrate).encode("utf-8"))
        self.interface.setAllFiltersToPass()

        super().__init__(
            channel=channel,
            bitrate=bitrate,
            poll_interval=poll_interval,
            **kwargs,
        )

    def send(self, msg: Message, timeout: Optional[float] = None) -> None:
        arbitration_id = msg.arbitration_id.to_bytes(length=4, byteorder="big")
        frame_bytes = b"\x01" + arbitration_id + msg.data
        self.interface.tx(frame_bytes)
        pass

    def _recv_internal(self, timeout: Optional[float] = None):
        start = time.monotonic()
        msg = None

        while msg is None:
            res = self.interface.rx(buffer_size=256 + 5, blocking=False)

            if res is None or len(res) == 0:
                if timeout is not None and (time.monotonic() - start) >= timeout:
                    return None, False
                else:
                    time.sleep(self.poll_interval)
                    continue
            else:
                msg = res

        if msg is None:
            return None, False

        timestamp = int.from_bytes(msg[0:4], "big")
        flags = msg[4]

        arbitration_id = int.from_bytes(msg[5 : 5 + 4], "big")

        dlc = len(msg) - 4 - 5
        if dlc > 0:
            data = msg[9:]
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

        return msg, False

    def shutdown(self) -> None:
        super().shutdown()
        self.interface.disconnect()
