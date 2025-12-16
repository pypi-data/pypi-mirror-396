from ._panel import PanelFinder
from .pixels import PixelGrid

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from asyncio import run, sleep

class PanelClient(BleakClient):
    CHARACTERISTIC_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"
                          #^ magic value from mi-led-display toolkit
    device: BLEDevice = None
    # whatever this means?

    def __init__(self):
        return
    
    async def __connect_for_them(self):
        succeeded = await self.pair_to_panel()
        assert succeeded, "Panel not found or advertised. Do you have Bluetooth enabled, or have it connected to something already?"
        await self.connect_to_panel()

    async def pair_to_panel(self, timeout_seconds: int | float = 20.) -> bool:
        """
        Pair to an unpaired Merkury Innovations Multicolor Matrix LED Display.
        Returned bool is if it was paired successfully.
        """
        panel_finder = PanelFinder(timeout_seconds)
        try:
            self.device = await panel_finder.use_scanner_to_find_device()
        except AssertionError:
            return False
        assert isinstance(self.device, BLEDevice), "Supplied device does not appear to be a bleak.backends.device.BLEDevice."
        super().__init__(self.device)
        return True

    def unpair_from_panel(self) -> bool:
        """
        Unpair from a Merkury Innovations Multicolor Matrix LED Display.
        Returned bool is if it was unpaired successfully.
        """

        if self.device:
            self.device = None
            return True
        return False

    async def connect_to_panel(self):
        if not self.device: raise RuntimeError("No device provided! Did you forget to pair me to a panel?")

        if not self.is_connected:
            await self.connect()
        return self

    async def disconnect_from_panel(self):
        if not self.device: raise RuntimeError("No device provided! Did you forget to pair me to a panel?")

        if self.is_connected:
            await self.disconnect()
        return self

    async def draw_to_panel(self, pixel_grid: PixelGrid | list[PixelGrid]):
        if not self.device:
            await self.__connect_for_them()
        await self.write_gatt_char(self.CHARACTERISTIC_UUID, bytes.fromhex("bc0ff1080855"))
                                                                            # ^ picture mode is basically all we need
        _list = pixel_grid
        if isinstance(_list, list) is False:
            _list = [pixel_grid]
        assert isinstance(_list, list)
        # doing a while loop here is a very bad, no good, terrible idea, and will block everything else
        # if this is being called, and not by show_image, then hopefully, the developer using this knows what they're doing

        # for joe schmoe drooling building a Discord bot, show_image should be plenty
        # anyone else with enough brain cells should loop this function, not have this function loop itself
        for pg in _list:
            batched_data = pg.render()
            for data in batched_data:
                await self.write_gatt_char(self.CHARACTERISTIC_UUID, data)
                await sleep(0.1)
                data = 0

    def show_image(self, pixel_grid: PixelGrid | list[PixelGrid], loop: bool = False):
        if not self.device:
            run(self.__connect_for_them())
        if isinstance(pixel_grid, list) is False: loop = False
        while loop:
            run(self.draw_to_panel(pixel_grid))