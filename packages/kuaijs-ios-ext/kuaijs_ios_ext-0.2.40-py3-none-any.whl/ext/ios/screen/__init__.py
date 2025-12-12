import typing
from typing import Union, Literal
from ext.ios.screen.image import KuaiJSImage
from kuaijs import image as image_api, device, paddleocr


def capture(rect=None) -> KuaiJSImage:
    if rect:
        image_id = image_api.captureRect(rect[0], rect[1], rect[2], rect[3])
    else:
        image_id = image_api.captureFullScreen()
    if image_id:
        return KuaiJSImage(image_id)
    return None


def size() -> typing.Tuple[int, int]:
    width, height = device.getScreenRealSize()
    return width, height


def ori() -> Literal["PORTRAIT", "LANDSCAPE"]:
    return device.getOrientation()


# 图片操作


def image_to_base64(
    image: KuaiJSImage = None,
    image_file: str = None,
    image_format="jpg",
    decode: str = "utf-8",
):
    """
    将KuaiJSImage对象转换为Base64编码的字符串

    :param image: KuaiJSImage对象
    :param image_format: 图片格式，默认为'jpg'
    :param image_file: 图片文件
    :param decode: base64 编码格式
    :return: 图片的Base64编码字符串
    """

    if image is None and image_file is None:
        image = capture()

    if image_file:
        image = image_file

    if image and isinstance(image, KuaiJSImage):
        return image_api.toBase64Format(image.id, image_format)
    else:
        return image_api.toBase64Format(image, image_format)


def image_read(file_path: str):
    image_id = image_api.readImage(file_path)
    if image_id:
        return KuaiJSImage(image_id)
    return None


def image_save(image: KuaiJSImage, path: str):
    return image_api.saveTo(image.id, path)


def image_crop(image: KuaiJSImage, rect: tuple):
    image_id = image_api.clip(image.id, rect[0], rect[1], rect[2], rect[3])
    if image_id:
        return KuaiJSImage(image_id)
    return None


def image_pixel(image: KuaiJSImage, x: int, y: int):
    value = image_api.pixel(image.id, x, y)
    strRGB = image_api.argb(value)
    hexv = strRGB[1:] if strRGB.startswith("#") else strRGB
    rgb = [int(hexv[0:2], 16), int(hexv[2:4], 16), int(hexv[4:6], 16)]
    return rgb


def image_rotate(image: KuaiJSImage, angle: int, expand: bool = True):
    image_id = image_api.rotateImage(image.id, angle, expand)
    if image_id:
        return KuaiJSImage(image_id)
    return None


def image_compress(image: KuaiJSImage, quality=50, _format="jpg"):
    base64_str = image_api.toBase64Format(image.id, _format, quality)
    image_id = image_api.base64ToImage(base64_str)
    if image_id:
        return KuaiJSImage(image_id)
    return None


class FindColors:
    def __init__(
        self,
        colors: str,
        rect: list = None,
        space: int = 5,
        ori: int = 2,
        diff: list = (5, 5, 5),
        image: KuaiJSImage = None,
        image_file=None,
    ):
        self.colors = colors
        self.rect = rect
        self.space = space
        self.ori = ori
        self.diff = diff
        self.image = image
        self.image_file = image_file
        self.first_color, self.points_str, self._is_single = (
            self._to_multi_color_params(colors, diff)
        )

    def find_all(self):
        img_id = None
        if isinstance(self.image, KuaiJSImage):
            img_id = self.image.id
        elif self.image_file:
            img_id = self.image_file
        else:
            img_id = "screen"
        x = 0
        y = 0
        ex = 0
        ey = 0
        if self.rect and len(self.rect) == 4:
            x, y, ex, ey = self.rect
        if not self.first_color:
            return None
        if self._is_single:
            return image_api.findColor(
                img_id,
                self.first_color,
                0.9,
                x,
                y,
                ex,
                ey,
                100,
                self.ori,
            )
        else:
            return image_api.findMultiColor(
                img_id,
                self.first_color,
                0.9,
                self.points_str,
                x,
                y,
                ex,
                ey,
                100,
                self.ori,
            )

    def find(self):
        img_id = None
        if isinstance(self.image, KuaiJSImage):
            img_id = self.image.id
        elif self.image_file:
            img_id = self.image_file
        else:
            img_id = "screen"
        x = 0
        y = 0
        ex = 0
        ey = 0
        if self.rect and len(self.rect) == 4:
            x, y, ex, ey = self.rect
        if not self.first_color:
            return None
        if self._is_single:
            res = image_api.findColor(
                img_id,
                self.first_color,
                0.9,
                x,
                y,
                ex,
                ey,
                1,
                self.ori,
            )
        else:
            res = image_api.findMultiColor(
                img_id,
                self.first_color,
                0.9,
                self.points_str,
                x,
                y,
                ex,
                ey,
                1,
                self.ori,
            )
        if res and len(res) > 0:
            return res[0]
        return None

    def _to_multi_color_params(self, colors: str, diff: typing.Iterable[int]):
        parts = [p for p in str(colors).split("|") if p]
        if len(parts) < 1:
            return None, None, False

        def parse_item(item: str):
            seg = item.split(",")
            if len(seg) != 3:
                return None
            try:
                x = int(seg[0].strip())
                y = int(seg[1].strip())
            except Exception:
                return None
            c = seg[2].strip()
            if c.startswith("#"):
                hexpart = c[1:]
            elif c.lower().startswith("0x"):
                hexpart = c[2:]
            else:
                hexpart = c
            c = "0x" + hexpart.upper()
            return x, y, c

        items = []
        for p in parts:
            it = parse_item(p)
            if it:
                items.append(it)
        if len(items) == 1:
            base_x, base_y, base_c = items[0]
            r = max(0, min(255, int(diff[0] if diff else 16)))
            g = max(0, min(255, int(diff[1] if diff else 16)))
            b = max(0, min(255, int(diff[2] if diff else 16)))
            shift = f"0x{r:02X}{g:02X}{b:02X}"
            first_color = f"{base_c}-{shift}"
            return first_color, None, True
        if len(items) < 2:
            return None, None, False
        base_x, base_y, base_c = items[0]
        r = max(0, min(255, int(diff[0] if diff else 16)))
        g = max(0, min(255, int(diff[1] if diff else 16)))
        b = max(0, min(255, int(diff[2] if diff else 16)))
        shift = f"0x{r:02X}{g:02X}{b:02X}"
        first_color = f"{base_c}-{shift}"
        rel = []
        for x, y, c in items[1:]:
            dx = x - base_x
            dy = y - base_y
            rel.append(f"{dx}|{dy}|{c}-{shift}")
        points_str = ",".join(rel)
        return first_color, points_str, False


class CompareColors:
    def __init__(
        self,
        colors: str,
        diff: tuple = (5, 5, 5),
        image: KuaiJSImage = None,
        image_file=None,
    ):
        self.colors = colors
        self.diff = diff
        self.image = image
        self.image_file = image_file
        self.cache_img = None

    def run(self) -> bool:
        if isinstance(self.image, KuaiJSImage):
            img_id = self.image.id
        elif self.image_file:
            img_id = self.image_file
        else:
            img_id = "screen"
        points_str = self._colors_to_points_str(self.colors, self.diff)
        return image_api.cmpColor(img_id, points_str, 0.9)

    def compare(self):
        return self.run()

    def _colors_to_points_str(self, colors: str, diff: typing.Iterable[int]):
        parts = [p for p in str(colors).split("|") if p]

        def parse_item(item: str):
            seg = item.split(",")
            if len(seg) != 3:
                return None
            try:
                x = int(seg[0].strip())
                y = int(seg[1].strip())
            except Exception:
                return None
            c = seg[2].strip()
            if c.startswith("#"):
                hexpart = c[1:]
            elif c.lower().startswith("0x"):
                hexpart = c[2:]
            else:
                hexpart = c
            c = "0x" + hexpart.upper()
            return x, y, c

        items = []
        for p in parts:
            it = parse_item(p)
            if it:
                items.append(it)
        r = max(0, min(255, int(diff[0] if diff else 16)))
        g = max(0, min(255, int(diff[1] if diff else 16)))
        b = max(0, min(255, int(diff[2] if diff else 16)))
        shift = f"0x{r:02X}{g:02X}{b:02X}"
        rel = []
        for x, y, c in items:
            rel.append(f"{x}|{y}|{c}-{shift}")
        return ",".join(rel)


class CountingColor:
    def __init__(
        self,
        colors: str,
        rect: tuple = None,
        diff: tuple = (5, 5, 5),
        image: KuaiJSImage = None,
        image_file=None,
    ):
        self.colors = colors
        self.rect = rect
        self.diff = diff
        self.image = image
        self.image_file = image_file

    def find(self):
        if isinstance(self.image, KuaiJSImage):
            img_id = self.image.id
        elif self.image_file:
            img_id = self.image_file
        else:
            img_id = "screen"
        x = 0
        y = 0
        ex = 0
        ey = 0
        if self.rect and len(self.rect) == 4:
            x, y, ex, ey = self.rect
        return image_api.countColor(img_id, self.colors, 0.99, x, y, ex, ey)


class FindImages:
    M_TEMPLATE = 5
    M_SIFT = 0

    def __init__(
        self,
        part_image: Union[str, list],
        rect: tuple = None,
        confidence=0.9,
        rgb: bool = False,
        mode=M_TEMPLATE,
        num=0,
        image: KuaiJSImage = None,
        image_file: str = None,
    ):
        self.part_image = part_image
        self.rect = rect
        self.confidence = confidence
        self.mode = mode
        self.num = num
        self.rgb = rgb
        self.image = image
        self.image_file = image_file

    def _search(self, method: int, limit: int):
        templates = (
            self.part_image if isinstance(self.part_image, list) else [self.part_image]
        )
        x = 0
        y = 0
        ex = 0
        ey = 0
        if self.rect and len(self.rect) == 4:
            x, y, ex, ey = self.rect
        if isinstance(self.image, KuaiJSImage):
            img_id = self.image.id
        elif self.image_file:
            img_id = self.image_file
        else:
            img_id = "screen"
        out = []
        for t in templates:
            res = image_api.findImage(
                img_id,
                t,
                x,
                y,
                ex,
                ey,
                self.confidence,
                limit,
                method,
                self.rgb,
            )
            if res:
                out.extend(res)
        return out

    def _run_mixed(self, limit: int):
        data = self._search(FindImages.M_TEMPLATE, limit)
        if not data:
            data = self._search(FindImages.M_SIFT, limit)
        return data

    def find(self):
        data = self._run_mixed(1)
        if data and len(data) > 0:
            return data[0]
        return None

    def find_all(self):
        data = self.find_all_template()
        if data is None or len(data) < 1:
            data = self.find_all_sift()

        return data

    def find_template(self):
        res = self._search(FindImages.M_TEMPLATE, 1)
        if res and len(res) > 0:
            return res[0]
        return None

    def find_all_template(self):
        return self._search(FindImages.M_TEMPLATE, -1)

    def find_sift(self):
        res = self._search(FindImages.M_SIFT, 1)
        if res and len(res) > 0:
            return res[0]
        return None

    def find_all_sift(self):
        return self._search(FindImages.M_SIFT, -1)


class Ocr:

    def __init__(
        self,
        rect=None,
        confidence: float = 0.6,
        max_side_len: int = 640,
        image: KuaiJSImage = None,
        image_file: str = None,
    ):
        self.confidence = confidence
        if rect:
            self.x = rect[0]
            self.y = rect[1]
            self.ex = rect[2]
            self.ey = rect[3]
        else:
            self.x = 0
            self.y = 0
            self.ex = 0
            self.ey = 0

        if image is None and image_file is None:
            self.image = "screen"
        else:
            self.image = image_file
        paddleocr.loadV5(max_side_len)

    def __del__(self):
        paddleocr.free()

    def paddleocr_v3(self):
        if isinstance(self.image, KuaiJSImage):
            input = self.image.id
        else:
            input = self.image
        res = paddleocr.recognize(
            input,
            self.x,
            self.y,
            self.ex,
            self.ey,
            self.confidence,
        )
        out = []
        if not res:
            return out
        for item in res:
            text = item.text
            conf = item.confidence
            x = item.x
            y = item.y
            ex = item.ex
            ey = item.ey
            cx = item.centerX
            cy = item.centerY
            out.append(
                {
                    "text": text,
                    "rect": [x, y, ex, ey],
                    "center_x": cx,
                    "center_y": cy,
                    "confidence": conf,
                }
            )
        return out


class CodeScanner:

    def __init__(
        self,
        rect: tuple = None,
        image: KuaiJSImage = None,
        image_file: str = None,
    ):
        self.rect = rect
        self.image = image
        self.image_file = image_file

    def scan(self):
        if isinstance(self.image, KuaiJSImage):
            img_id = self.image.id
        elif self.image_file:
            img_id = self.image_file
        else:
            img_id = "screen"

        if self.rect:
            x, y, ex, ey = self.rect
            input = image_api.clip(img_id, x, y, ex, ey)
            res = image_api.scanCode(input)
            image_api.release(input)
        else:
            res = image_api.scanCode(img_id)
        return res
