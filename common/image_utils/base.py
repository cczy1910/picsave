import numpy as np

import cv2
import os

from PIL import Image

from common.logging import get_logger

HASH_SIZE = 8
MAX_SIZE = 2 ** 32
LOGGER = get_logger()


def __binary_array_to_hex(arr):
    bit_string = ''.join(str(b) for b in 1 * arr.flatten())
    width = int(np.ceil(len(bit_string) / 4))
    return '{:0>{width}x}'.format(int(bit_string, 2), width=width)


def __tmp_file_writer(func):
    def wrapper(image_blob: bytes, *args, **kwargs):
        with open('tmp.jpg', 'wb') as f:
            f.write(image_blob)

        result = func(image_blob, *args, **kwargs)

        try:
            os.remove('tmp.jpg')
        except Exception:
            pass

        return result

    return wrapper


def __average_hash(image):
    image = image.convert("L").resize((HASH_SIZE, HASH_SIZE), Image.ANTIALIAS)

    # finding average pixel value
    pixels = np.asarray(image)
    avg = np.mean(pixels)

    diff = pixels > avg

    return __binary_array_to_hex(diff.flatten())


def __phash(image):
    import scipy.fftpack

    img_size = HASH_SIZE * 4
    image = image.convert("L").resize((img_size, img_size), Image.ANTIALIAS)

    pixels = np.asarray(image)
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:HASH_SIZE, :HASH_SIZE]
    med = np.median(dctlowfreq)

    diff = dctlowfreq > med

    return __binary_array_to_hex(diff.flatten())


@__tmp_file_writer
def p_hash(image_blob: bytes):
    return str(__phash(Image.open('tmp.jpg')))


@__tmp_file_writer
def avg_hash(image_blob: bytes):
    return str(__average_hash(Image.open('tmp.jpg')))


@__tmp_file_writer
def scale_image(image_blob: bytes, scale: float):
    try:
        image = cv2.imread('tmp.jpg', 1)
        h, w = image.shape[:2]
        h, w = h * scale, w * scale

        if h * w > MAX_SIZE:
            LOGGER.info(f'{h * w} exceeds {MAX_SIZE} and will not be scaled')
            return None

        scaled_image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        cv2.imwrite('tmp.jpg', scaled_image)

        return open('tmp.jpg', 'rb').read()
    except Exception as e:
        LOGGER.error(str(e))
        return None


@__tmp_file_writer
def image_sizes(image_blob: bytes):
    return cv2.imread('tmp.jpg', 1).shape[:2]


def process_image_headers(image_blob: bytes):
    trash_start = image_blob.find(b'image/jpeg')
    image_blob = image_blob[trash_start + len(b'image/jpeg') + 4:]

    trash_end = image_blob.find(b'WebKitFormBoundary')
    image_blob = image_blob[:trash_end - 8]

    return image_blob
