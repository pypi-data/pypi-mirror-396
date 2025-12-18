# tests/test_img.py

import sys
sys.path.append("/data/tianzhen/my_packages/cobra-color/src")

from cobra_color import safe_print
from cobra_color.render import imgfile_to_ansi
from pathlib import Path
import time


def _fmt_image(mode):
    data_path = Path(__file__).parent / "assets" / "eagle.jpg"
    result = imgfile_to_ansi(
        str(data_path),
        mode=mode,
        height=20,
        display=True
    )
    assert isinstance(result, str)
    # safe_print(result)
    # Console().print(result, end="", markup=False, highlight=False)


def test_fmt_image():
    _fmt_image("half-color")
    _fmt_image("half-gray")
    _fmt_image("color")
    _fmt_image("gray")
    test_fmt_image_ascii()

    try:
        from rich.progress import Progress
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing...", total=50)
            for i in range(50):
                time.sleep(0.1)
                progress.update(task, advance=1)
                if i % 10 == 0:
                    _fmt_image("half-color")
    except ImportError:
        pass

    try:
        from tqdm import tqdm
        for i in tqdm(range(50)):
            time.sleep(0.1)
            if i % 10 == 0:
                _fmt_image("half-color")
    except ImportError:
        pass


def test_fmt_image_ascii():
    data_path = Path(__file__).parent / "assets" / "eagle.jpg"
    result = imgfile_to_ansi(
        str(data_path),
        mode="ascii",
        charset="@%#*+=-:. ",
        height=30,
        display=True
    )
    assert isinstance(result, str)
    # print(result)


if __name__ == "__main__":

    for i in range(10):
        safe_print(f"progress: {i}/1012", end="\r", flush=False)
        time.sleep(0.5)

    try:
        from tqdm import tqdm
        for i in tqdm(range(50)):
            time.sleep(0.1)
            if i % 10 == 0:
                safe_print(f"progress: {i}/1012", end="\r\n")
    except ImportError:
        pass

    s = time.time()
    test_fmt_image()
    print("Elapsed time:", time.time() - s)
