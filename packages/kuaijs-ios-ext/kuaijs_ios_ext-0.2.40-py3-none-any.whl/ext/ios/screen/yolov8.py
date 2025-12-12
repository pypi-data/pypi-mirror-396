from typing import Union

from kuaijs import yolo
from ext.ios.screen.image import KuaiJSImage


model_id = None


def load(param_path: str, bin_path: str, nc: int, use_gpu: bool = False):
    free()
    global model_id
    model_id = yolo.loadV11(
        param_path,
        bin_path,
        nc,
    )
    return model_id != None


def detect(
    img: Union[KuaiJSImage, str] = None,
    target_size: int = 640,
    threshold=0.4,
    nms_threshold=0.5,
):
    if img is None:
        img = "screen"

    global model_id
    return yolo.detect(model_id, img, target_size, threshold, nms_threshold)


def free():
    global model_id
    yolo.free(model_id)
    model_id = None
