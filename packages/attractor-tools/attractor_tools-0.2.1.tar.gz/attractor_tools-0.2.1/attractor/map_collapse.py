import enum
from json import tool
import os
import matplotlib.pyplot as plt
import multiprocessing
from time import sleep
import numpy as np

from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent

from .terminal import TerminalCounter
from .render_class import Performance_Renderer
from .frame import Frame, SimonFrame
from .utils import apply_colormap
from .colormap import ColorMap


def render_frames_collapse(frames: list[tuple[Frame, tuple[int, int]]], shape: tuple[int, int], use_counter: bool = True, threads = 10, chunksize=10):
    if use_counter:
        counter = TerminalCounter(len(frames))
        counter.start()

    collapseMap = np.zeros(dtype=np.float16, shape=shape)

    # Multiproccessing
    with multiprocessing.Pool(threads) as pool:
        return_value: tuple[int, tuple]
        for return_value in pool.imap(_render_frame_collapse, frames, chunksize=chunksize):
            is_collapsed: int = return_value[0]
            x, y = return_value[1]

            if use_counter and counter is not None:
                counter.count_up()
                
            collapseMap[y, x] = is_collapsed
            # collapseMap[xy[1], xy[0]] = 0 if frame.collapsed else 1
    return (collapseMap - collapseMap.min()) / (collapseMap.max() - collapseMap.min())


def _render_frame_collapse(args: tuple[Frame, tuple[int, int]]):
    frame, (x, y) = args
    frame.render(only_raw=True)
    is_collapsed = frame.is_collapsed()
    frame.clear()
    return is_collapsed, (x, y)


def collapse_map(a_bounds: tuple[float, float], b_bounds: tuple[float, float], delta: float=0.01):
    a_diff = abs(a_bounds[0] - a_bounds[1])
    b_diff = abs(b_bounds[0] - b_bounds[1])
    na: int = round(a_diff / delta)
    nb: int = round(b_diff / delta)
    A = np.linspace(a_bounds[0], a_bounds[1], na)
    B = np.linspace(b_bounds[0], b_bounds[1], nb)

    print(f"{len(A)}x{len(B)}   frames: {len(A)*len(B)}")
    sleep(1.5)
    # input("press Enter to continue")

    # collapseMap = np.zeros(dtype=np.float16, shape=(len(A), len(B)))
    frames: list[tuple[Frame, tuple]] = []
    colomap = ColorMap("viridis")
    for x, a in enumerate(A):
        for y, b in enumerate(B):
            frame = SimonFrame(
                a=a,
                b=b,
                colors=colomap,
                n=3_000,
                resolution=150
            )
            frames.append((frame, (x, y)))

    collapseMap = Performance_Renderer.render_frames_collapse(frames, shape=(len(B), len(A)), threads=14, chunksize=12)
    img = apply_colormap(collapseMap, ColorMap("viridis"))
    show_image_matplotlib(img, A, B) # type: ignore

def show_image_matplotlib(img: np.ndarray, A: list[float], B: list[float], pathMode: bool = False):
    """
    Display an RGB image using matplotlib with hover coordinates, 
    and show the SimonFrame-rendered image in a second panel on click.

    Args:
        img (np.ndarray): RGB image as a NumPy array.
        A (list[float]): Values corresponding to x-axis.
        B (list[float]): Values corresponding to y-axis.
    """
    from .frame import SimonFrame
    if not isinstance(img, np.ndarray):
        raise TypeError("Input must be a NumPy ndarray.")
    if img.ndim != 3 or img.shape[2] not in (3, 4):
        raise ValueError("Input image must be RGB or RGBA (HxWx3 or HxWx4).")

    currentPath: list[tuple[float, float]] = []
    # Create two subplots side by side
    ax1: Axes
    ax2: Axes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.tight_layout()

    # First image
    im1 = ax1.imshow(img, origin='lower')
    ax1.set_title("Original Image")

    # Text box for coordinates on hover
    coord_text = ax1.text(0.02, 0.98, '', color='white', transform=ax1.transAxes, verticalalignment='top', bbox=dict(facecolor='black', alpha=0.5, pad=2))

    # Placeholder for second image
    im2 = ax2.imshow(np.zeros_like(img), origin='lower')
    ax2.set_title("Rendered Frame")

    # Mouse hover event for first image
    def on_mouse_move(event: MouseEvent):
        if event.inaxes != ax1:
            return
        
        assert event.xdata
        assert event.ydata
        x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)
        try:
            x_val = A[x]
            y_val = B[y]
            coord_text.set_text(f"a: {x_val:.4f}, b: {y_val:.4f}")
            fig.canvas.draw_idle()
        except IndexError:
            return

        # Render SimonFrame
        frame = SimonFrame(
            a=x_val,
            b=y_val,
            n=500_000,
            resolution=500,
            colors=ColorMap("viridis", True)
        )
        frame.render()
        im2.set_data(frame.img)
        im2.set_extent((0, frame.img.shape[1], 0, frame.img.shape[0]))
        ax2.set_aspect('auto')
        ax2.set_title(f"Rendered Frame (a={x_val:.4f}, b={y_val:.4f})")
        ax2.set_xlim(0, frame.img.shape[1])
        ax2.set_ylim(0, frame.img.shape[0])
        fig.canvas.draw_idle()

    # Click event to render SimonFrame and update second panel
    def on_click(event: MouseEvent):
        toolbar = plt.get_current_fig_manager()
        if toolbar is not None:
            toolbar = toolbar.toolbar
            if toolbar.mode != '': # type: ignore
                return

        if event.inaxes == ax1:
            assert event.xdata
            assert event.ydata
            x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)
            try:
                x_val = A[x]
                y_val = B[y]
            except IndexError:
                return

            img[y, x] = [255, 0, 0, 255]
            im1.set_data(img)
            fig.canvas.draw_idle()
            currentPath.append((round(float(x_val), 4), round(float(y_val), 4)))

            os.system("cls")
            for i, (x, y) in enumerate(currentPath):
                print(f"{i:02d}: {x:2f}, {y:2f}")
            print(currentPath)


    def on_key(event: MouseEvent):
        assert event.xdata
        assert event.ydata
        x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)
        try:
            x_val = A[x]
            y_val = B[y]
        except IndexError:
            return

        if event.key == "enter":
            frame = SimonFrame(
                a=x_val,
                b=y_val,
                n=3_000_000,
                resolution=1000,
                colors=ColorMap("viridis")
            )
            frame.render()
            frame.show()

    # Connect events
    fig.canvas.mpl_connect('motion_notify_event', on_mouse_move) # type: ignore
    fig.canvas.mpl_connect('button_press_event', on_click) # type: ignore
    fig.canvas.mpl_connect('key_press_event', on_key) # type: ignore

    # Hide axes
    ax1.axis('off')
    ax2.axis('off')

    plt.show()