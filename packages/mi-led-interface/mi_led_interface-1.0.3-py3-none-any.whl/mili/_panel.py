from time import time
from asyncio import sleep, run
from bleak import BleakScanner
from bleak.backends.device import BLEDevice

class PanelFinder:
    identified_panel: BLEDevice = None
    timeout_seconds: int | float

    def __init__(self, timeout_seconds: int | float = 10.):
        self.timeout_seconds = timeout_seconds
        

    def _find_device(self, device: BLEDevice, _):
        if device.name == "MI Matrix Display":
            self.identified_panel = device

    async def use_scanner_to_find_device(self, timeout_seconds:float = 10.):
        if not isinstance(timeout_seconds, float) and not isinstance(timeout_seconds, int):
            raise ValueError("Timeout is expected to be an integer or float in seconds.")
        scanner = BleakScanner(self._find_device)

        start_time = time()
        await scanner.start()

        while not self.identified_panel:
            await sleep(0.05) # 50ms
            if time() - start_time > timeout_seconds:
                break
            
        await scanner.stop()
        assert self.identified_panel, "Panel not found or advertised. Do you have Bluetooth enabled, or have it connected to something already?"
        return self.identified_panel

if __name__ == "__main__":
    panel_finder = PanelFinder()
    print(run(panel_finder.use_scanner_to_find_device()))