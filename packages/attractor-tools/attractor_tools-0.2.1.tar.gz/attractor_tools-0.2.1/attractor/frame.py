from dataclasses import dataclass
from numpy.typing import NDArray
from typing import Optional
from time import time
import numpy as np
import os

from .utils import apply_color, get_new_png_path
from .view import show_frame, show_image
from .colormap import ColorMap
from .png import save_to_greyscale , loadpng, normalize_array, save


@dataclass
class DeltaTime():
    elapsedTime: float

    def __repr__(self) -> str:
        return f"{self.elapsedTime:.2f}s"


@dataclass(kw_only=True)
class Frame:
    """
    This Class Represents one render instance
    Identifiers like, a, b, c, ... are initial value for the strange attractors
    """
    resolution: int = 1000
    percentile: float | list[float] = 99.4
    colors: ColorMap
    n: int

    def __post_init__(self):
        # attributes only available after render
        self.img_: Optional[NDArray] = None
        self.raw_: Optional[NDArray] = None
        self.points_per_pixel = None
        self.collapsed: bool = False
        self._t_start: float = 0

    def clear(self):
        self.img_ = None
        self.raw_ = None
        self.points_per_pixel = None

    @property
    def img(self) -> NDArray:
        if self.img_ is not None:
            return self.img_

        if self.raw is None:
            raise RuntimeError("Frame isn't rendered yet!")

        if isinstance(self.colors, list):
            raise Exception()
        self.img_ = apply_color(self.raw, self.colors.get())
        return self.img_


    @img.setter
    def img(self, value: NDArray):
        self.img_ = value

    @property
    def raw(self) -> Optional[NDArray]:
        return self.raw_

    @raw.setter
    def raw(self, new_raw):
        self.raw_ = new_raw
        self.is_collapsed()

    def render(self, only_raw = False) -> DeltaTime:
        # apply color
        if not only_raw and self.raw is not None:
            if isinstance(self.colors, list):
                raise Exception()
            self.img = apply_color(self.raw, self.colors.get())
        
        return DeltaTime(time() - self._t_start)

    def scatter_to_normalized(self, x_raw, y_raw):
        points_per_pixel = np.histogram2d(x_raw, y_raw, bins=self.resolution)[0]
        return points_per_pixel

    def normalize(self, points_per_pixel: NDArray) -> NDArray:
        # clip outliers
        max_value = np.percentile(points_per_pixel, self.percentile)
        max_value = max_value if np.isfinite(max_value) and max_value > 0 else 1.0
        points_per_pixel = np.clip(points_per_pixel, 0, max_value)

        # normalize to [0,1]
        return (points_per_pixel / np.max(points_per_pixel)).astype(np.float32)

    def is_collapsed(self):
        assert self.raw is not None, "first render"
        assert not isinstance(self.resolution, list)
        non_zero = np.count_nonzero(self.raw)
        thresh = self.resolution ** 2 * 0.05
        self.collapsed = non_zero < thresh
        return non_zero
    
    def show(self):
        assert self.img is not None, "Render the frame before displaying it!"
        show_image(self.img)

    def add_colors(self, colormap: Optional[ColorMap] = None):
        assert self.raw is not None, "Render Frame before adding color to it"

        if colormap is not None:
            self.colors = colormap
        self.img = apply_color(self.raw, self.colors.get())

    def saveAsGeneric(self, path: str):
        """
        Save image as Png with 16-bit Quality
        """
        # TODO maybe manully render as greyscale here

        assert self.img is not None, "render before saving!"
        if ".png" not in path:
            path += ".png"

        # Path
        i = 0
        path_ = path.replace(".png", "")
        while os.path.exists(f"{path_}.png"):
            i += 1
            path_ = f"{path.replace('.png', '')}({i})"
        path = f"{path_}.png"

        save_to_greyscale(self.img, filename=path)
    


    def save(self, path: str):
        assert self.img is not None, "render before saving!"
        if ".png" not in path:
            path += ".png"

        # Path
        i = 0
        path_ = path.replace(".png", "")
        while os.path.exists(f"{path_}.png"):
            i += 1
            path_ = f"{path.replace('.png', '')}({i})"
        path = f"{path_}.png"

        save(self.img, filename=path)


@dataclass
class SimonFrame(Frame):
    a: float
    b: float

    def render(self, only_raw = False) -> DeltaTime:
        from .attractor import simon

        if isinstance(self.a, list) or isinstance(self.b, list):
            raise ValueError("a or b are a list, when using lists for assignment call .toFrames() first")

        if not isinstance(self.n, int):
            self.n = int(self.n) # type: ignore

        self._t_start = time()

        x, y = simon(self.a, self.b, self.n)
        self.points_per_pixel = self.scatter_to_normalized(x, y)
        self.raw = self.normalize(self.points_per_pixel)
        return super().render(only_raw=only_raw)
        
    @staticmethod
    def loadFromGeneric(path: str) -> "SimonFrame":
        # shell Frame
        frame = SimonFrame(
            resolution=0,
            percentile=0,
            colors=None, # type: ignore
            n=0,
            a=0,
            b=0
        )
        frame.raw = normalize_array(loadpng(path))
        return frame
    
    def show(self):
        show_frame(self)


    def __repr__(self) -> str:
        a = float(self.a)
        b = float(self.b)
        return f"SimonFrame[{a=}, {b=}] {self.n=} {self.collapsed=}"


    def save_with_dialogue(self):
        path = get_new_png_path()
        
        if not path:
            return
        
        save(self.img, filename=path)

        if not os.path.basename(path).startswith("_"):
            self.saveMetadata(path)

        print(f"save to: {path}")
        return
    
    def saveMetadata(self, pngPath: str):
        """This method relies on the fact that the png path is unique so this has not to exist yet"""
        txtPath = pngPath.removesuffix("png") + "txt"
            
        with open(txtPath, "w") as f:
            f.write(f"a: {self.a:4f}\n")
            f.write(f"b: {self.b:4f}\n")
            f.write(f"colormap: {self.colors.name} ({self.colors.inverted})\n")
            f.write(f"percentile: {self.percentile:3f}\n")
        


# @dataclass
# class CliffordFrame(Frame):
#     a: float
#     b: float
#     c: float
#     d: float

#     def init_args(self) -> tuple:
#         return (self.a, self.b, self.c, self.d)

#     def render(self, only_raw = False):
#         from .attractor import clifford

#         self.check_multiple()
#         x, y = clifford(self.a, self.b, self.c, self.d, self.n)
#         self.raw = self.scatter_to_normalized(x, y)
#         super().render(only_raw=only_raw)

