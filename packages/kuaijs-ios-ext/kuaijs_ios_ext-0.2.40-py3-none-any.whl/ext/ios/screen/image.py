import base64
from kuaijs import image


class KuaiJSImage:
    def __init__(self, image_id: str):
        self.id = image_id

    # 释放图片资源
    def __del__(self):
        image.release(self.id)

    def tobytes(self):
        image_base64 = image.toBase64Format(self.id, "jpg", 100)
        return base64.b64decode(image_base64)

    def size(self):
        return image.getSize(self.id)

    def toBase64(self, format: str = "jpg", quality: int = 100):
        return image.toBase64Format(self.id, format, quality)
