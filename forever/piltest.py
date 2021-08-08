from PIL import Image, ImageFilter
# jonkinlaista kuvaedittiä, idk
class PILImage():
    def __init__(self, filename : str, mask=False) -> None:
        try:
            self._im = Image.open(filename)
            if mask:
                self._im = self._im.convert('L')
        except FileNotFoundError:
            raise Exception(f"File Not found, {filename}")
    def image(self) -> Image:
        return self._im
    def rotate(self, rotation : int) -> None:
        self._im = self._im.rotate(rotation)
    def filter(self, filter : ImageFilter) -> None:
        self._im = self._im.filter(filter)
    def resize(self, width : int, height : int) -> None:
        self._im = self._im.resize((width, height))
    def __str__(self) -> str:
        return f"Format:{self._im.format}, Size: {self._im.size}, Mode: {self._im.mode}"
    def size(self) -> tuple(int, int):
        return self._im.size
    def width(self) -> int:
        return self._im.width
    def height(self) -> int:
        return self._im.height
    def save(self, filename : str) -> bool:
        self._im.save(filename)
        return True
    def paste(self, im : Image, coords : tuple[int, int]=(0, 0), mask_im : Image=None) -> None:
        if mask_im is not None:
            self._im.paste(im, coords, mask_im)
        else:
            self._im.paste(im, coords)
    def resize_percentage(self, percent : float) -> None:
        new_height = int(self.height() * percent)
        new_width = int(self.width() * percent)
        self.resize(new_width, new_height)
    
class Mask(PILImage):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    def resize(self, image : PILImage) -> None:
        super().resize(*image.size())
im = PILImage("imgs_test/1.jpg")
im2 = PILImage("imgs_test/2.jpg")
im3 = PILImage("imgs_test/3.png")
im3.resize_percentage(2)
mask_heart = Mask("masks/circle_blur.jpg")
mask_heart.resize(im2)
im.paste(im2.image(), (60, 50), mask_heart.image())
mask_heart.resize(im3)
im.paste(im3.image(), (2300, 1300), mask_heart.image())
print(str(im),"\n", str(im2),"\n", str(mask_heart))
im.save("imgs_test/test.png")
