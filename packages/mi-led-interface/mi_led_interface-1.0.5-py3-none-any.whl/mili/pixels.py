from PIL import Image
from os.path import exists, isdir
import filetype

def _hex(_input: int):
    assert isinstance(_input, int), "Parameter inserted for hex is not an integer."
    return hex(_input).split("0x")[-1]

class Pixel:
    r: int
    g: int
    b: int

    def __init__(self, r: int = None, g: int = None, b: int = None):
        if not isinstance(r, (int, type(None))) or not isinstance(g, (int, type(None))) or not isinstance(b, (int, type(None))):
            raise ValueError(f"RGB should all be integers! Received ({r}, {g}, {b}).")
        
        if r is None: r = 0
        if g is None: g = 0
        if b is None: b = 0
        self.r, self.g, self.b = r, g, b

    def to_hex(self):
        """
        Return pixel as a hexadecimal string.
        """
        r, g, b = self.r, self.g, self.b
        return _hex(r)+_hex(g)+_hex(b)

    def grayscale(self):
        """
        Otherwise known as getting the mean of the pixel's RGB values.
        """
        return sum((self.r, self.g, self.b))//3
    
    @staticmethod
    def from_bool(_input: bool):
        """
        Otherwise known as setting the RGB values to their maximum if True. Leaving them 0 otherwise.
        """
        _input = bool(_input)
        return Pixel(int(_input)*255, int(_input)*255, int(_input)*255)
    
    def values(self):
        return (self.r, self.g, self.b)



class PixelGrid:
    height: int
    width: int
    _pixels: list[Pixel]

    PANEL_WIDTH: int
    PANEL_HEIGHT: int

    def __init__(self, pixel_grid_compatible: list[tuple(int)] = None, panel_width: int = 16, panel_height: int = 16):
        """
        PixelGrid of 16x16, compatible with the Merkury LED panel.
        pixel_grid_compatible is expected to be a list[list[tuple[int]]], i.e.:
        [[(0, 0, 0), (0, 0, 0), (0, 0, 0), ...], [(0, 0, 0), (0, 0, 0), (0, 0, 0), ...], ...]
        ...where the first, second, and third index of the tuple is the associated RGB values of that pixel.
        """
        self._pixels = []
        self.PANEL_WIDTH    = panel_width
        self.PANEL_HEIGHT   = panel_height   
        
        if not pixel_grid_compatible:
            for _ in range(panel_width*panel_height):
                self._pixels.append(Pixel())
        else:
            for y in range(panel_width):
                for x in range(panel_height):
                    r, g, b = pixel_grid_compatible[x][y]
                    self._pixels.append(Pixel(r, g, b))

    def __calculate_position_from_x_y(self, x: int, y: int):
        return y*self.PANEL_HEIGHT+x
    
    # def __calculate_position_from_index(self, pos: int):
    #     return (pos//self.PANEL_HEIGHT, (pos-self.PANEL_HEIGHT*(pos//self.PANEL_HEIGHT))%self.PANEL_WIDTH)
    # likely won't be necessary, considering we use x, y coordinates fundamentally, but. w/e

    # ---------------------------------------------------- #

    def get_pixel(self, x: int, y: int):
        """
        Get a pixel on the grid.
        x: int
        y: int
        """
        assert isinstance(x, int) and isinstance(y, int), f"X or Y is not a number. ({x}, {y})"
        return self._pixels[self.__calculate_position_from_x_y(x, y)]
    
    def set_pixel(self, x: int, y: int, val: Pixel):
        """
        Set a pixel on the grid.
        x:      int
        y:      int
        val:    Pixel
        """
        if isinstance(val, tuple):
            # try anyway
            r, g, b = val[0], val[1], val[2]
            val = Pixel(r, g, b)
        assert isinstance(x, int) and isinstance(y, int) and isinstance(val, Pixel), f"X, Y is not a number, or value provided is not a valid pixel. ({x}, {y}) = {val}"
        self._pixels[self.__calculate_position_from_x_y(x, y)] = val
        return val.grayscale()
    
    # ---------------------------------------------------- #

    
    @staticmethod
    def from_image(fp_or_image: str | Image.Image) -> "PixelGrid" | list["PixelGrid"]:
        """
        Returns a copy of the PixelGrid with the image/image filepath provided filling the pixels,
        or a list of PixelGrids if the image/image filepath is animated.
        """

        image = fp_or_image

        if isinstance(image, str):
            assert exists(fp_or_image), "Filepath to image does not exist."
            assert isdir(fp_or_image) is False, "Filepath provided leads to a directory."

            extension = filetype.guess_extension(fp_or_image)
            valid_pillow_extensions = Image.registered_extensions()
            openable_extensions = [ex.lstrip(".") for ex, f in valid_pillow_extensions.items() if f in Image.OPEN]
            assert extension in openable_extensions, "File is not openable by PILlow."

            fp_or_image = Image.open(fp_or_image)
            image = fp_or_image

        _list_pg = []

        _index = 1
        while True:
            pg = PixelGrid()
            temp_image = image.copy()
            width, height = temp_image.size
            if width != 16 or height != 16:
                temp_image = temp_image.resize((16, 16), Image.Resampling.LANCZOS)
                width, height = temp_image.size

            if image.mode != 'RGB':
                temp_image = temp_image.convert('RGB')

            for y in range(temp_image.width):
                for x in range(temp_image.height):
                    r, g, b = temp_image.getpixel((x, y))
                    pg.set_pixel(x, y, Pixel(r, g, b))

            _list_pg.append(pg)

            try:
                image.seek(_index)
                _index += 1
            except EOFError:
                break
        
        return pg if len(_list_pg) == 1 else _list_pg
    
    def render(self) -> list[bytearray]:
        """
        Returns pixel grid as a list of 8 command packets (bytearray),
        ready to be sent to the display sequentially.
        """
        all_commands = []

        # after refactoring to be on a positional index rather than a row-first list-in-list, this
        # *should* be more performant. hopefully a bit more readable. no guarantees though.
        
        PIXELS_PER_BLOCK = 32
        TOTAL_BLOCKS = 8
        
        for block_index in range(TOTAL_BLOCKS):
            start = block_index * PIXELS_PER_BLOCK
            # eg: 1 * 32 = 32
            end = start + PIXELS_PER_BLOCK
            # 32 + 32 = 64
            
            # pixels 32 thru 64
            block_pixels = self._pixels[start:end]
                                        # funni list comprehension...ish. i guess more accurately index splitting?
            
        
            COMMAND_INITIATOR = 0xBC
            MI_SPECIAL_VALUE = 0x0F # this means something to somebody. i don't quite know what
            # it could be an indicator that this is to be used with "image mode"? we're kind of emulating it and 
            # doing it ourselves in favor of whatever bullshit the app protocol's got going on

            # maybe there's a way to transmit and store images on it? if so, it's gonna take a lot more effort
            # than i'm willing to put in
            TERMINATOR = 0x55
            header = bytearray([COMMAND_INITIATOR, MI_SPECIAL_VALUE, block_index + 1])
            pixel_data = bytearray()
            for pixel in block_pixels:
                # Extend with R, G, B bytes
                assert isinstance(pixel, Pixel), "Received value in PixelGrid is not a Pixel."
                pixel_data.extend([pixel.r, pixel.g, pixel.b])
            terminator = bytearray([TERMINATOR])
            command = header + pixel_data + terminator
            all_commands.append(command)

        return all_commands
    
    def __repr__(self):
        _returned = "" 
        
        for index, pixel in enumerate(self._pixels):
            hex_value = _hex(pixel.grayscale())
            padded_hex = hex_value if len(hex_value) == 2 else f'0{hex_value}'
            
            _returned += f"{padded_hex} "
            if index%16==0 and index!=0: _returned += "\n"
        return _returned
    
if __name__ == "__main__":
    pg = PixelGrid.from_image("./tests/test_anim.webp")
    print(pg)