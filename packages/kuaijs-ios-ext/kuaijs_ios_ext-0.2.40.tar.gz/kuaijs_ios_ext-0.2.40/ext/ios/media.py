import threading
import time
from kuaijs import media


def audio_play(path: str, callback=None, volume: float = -1):
    def work():
        media.playMp3(path, False)
        if callback is None:
            return
        while media.isMp3Playing():
            time.sleep(0.2)
        callback()

    threading.Thread(target=work, daemon=True).start()


def audio_stop(a_id):
    media.stopMp3()


def save_pic2photo(address: str):
    return media.saveImageToAlbum(address)


def save_video2photo(address: str):
    return media.saveVideoToAlbumPath(address)
