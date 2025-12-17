import logging
from collections import deque

import bleak
import bleak.backends.characteristic

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


class BLEIOConnector:
    def __init__(self, address: str):
        self.address = address
        self._ble = bleak.BleakClient(
            address,
            services=[UART_SERVICE_UUID],
            use_cached_services=True,
            timeout=30,
        )
        self._packet = b""
        self._packet_handlers = {}
        self._error_handler = self._async_print
        self._pending_packets = deque()

    async def connect(self):
        await self._ble.connect()
        await self._ble.start_notify(UART_RX_CHAR_UUID.lower(), self._handle_rx)

    async def disconnect(self):
        await self._ble.stop_notify(UART_RX_CHAR_UUID.lower())
        await self._ble.disconnect()

    async def _async_print(self, data: bytes):
        logging.warning("Invalid Packet", data)

    def get_packet(self):
        if self._pending_packets:
            return self._pending_packets.popleft()
        return None

    async def _handle_rx(
        self,
        _: bleak.backends.characteristic.BleakGATTCharacteristic,
        data: bytearray,
    ):
        self._packet += data
        if b"\x1a" in self._packet:
            if len(self._packet) > 1:
                packet = self._packet[: self._packet.index(b"\x1a")]
                packet_id = packet[:1]
                arguments = packet[1:]
                if packet_id == b"P":
                    ...  # Report print: arguments.decode(errors="replace")
                elif packet_id == b"E":
                    ...  # Report error (user): arguments.decode(errors="replace")
                elif packet_id == b"!":
                    ...  # Report error (critical): arguments.decode(errors="replace")
                else:
                    self._pending_packets.append((packet_id, arguments))
            self._packet = b""

    async def send_packet(self, packet_id: int | bytes, data: bytes | None = None):
        if isinstance(packet_id, int):
            packet_id = packet_id.to_bytes()
        if not isinstance(packet_id, bytes):
            packet_id = bytes(packet_id)
        if data is None:
            data = b""
        await self._ble.write_gatt_char(
            UART_TX_CHAR_UUID.lower(),
            packet_id + data + b"\x1a",
        )
