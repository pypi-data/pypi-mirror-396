from .pixels import PixelGrid, Pixel
from .client import PanelClient
from asyncio import run
from time import time
from math import floor

def binary_representation(number: int):
    if isinstance(number, int) is False: return "0"*256
    string = bin(number).split("0b")[-1]
    if len(string) >= 256: return "0"*256
    iterations = 256 - len(string)
    returned_string = ""
    for _ in range(iterations):
        returned_string += "0"
    returned_string += string
    return returned_string

async def __main():
    print("Finding Merkury Innovations panel...")
    
    panel_client = PanelClient()
    
    succeeded = await panel_client.pair_to_panel()
    for _ in range(9):
        if succeeded: break
        print("Failed to pair. Trying again...")
        succeeded = await panel_client.pair_to_panel()
    if succeeded is False: print("Failed to connect 10 times. Is it nearby, powered on, and not already connected to something?"); exit()

    await panel_client.connect_to_panel()
    
    print("Found!")
    while True:
        pixel_grid = PixelGrid()
        b_r = binary_representation(floor(time()))
        for index, i in enumerate(b_r):
            pixel_grid.set_pixel(index%16, index//16, Pixel.from_bool(int(i)))
        await panel_client.draw_to_panel(pixel_grid)

run(__main())