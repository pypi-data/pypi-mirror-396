import cv2 as cv
import numpy as np
from typing import Tuple, List, Dict, Any


def resize_image(image, size: Tuple, keep_aspect_ratio: bool=False):
    """
    Resize the input image.

    Args:
        image (np.ndarray): input image
        size (Tuple): (height, width)
        keep_aspect_ratio (bool, optional): maintain the aspect ratio of the image. Defaults to False.

    Returns:
        np.ndarray: resized image
    """
    h, w, c = image.shape
    portrait = w > h

    if keep_aspect_ratio:
        if portrait:
            new_height = size[-1]
            new_width = int(new_height *(w/h))
        else:
            new_width = size[0]
            new_height = int(new_width * (h/w))
    else:
        new_height, new_width = size[-1], size[0]
    
    return cv.resize(image, (new_width, new_height))

def pad_image(image, padding: Tuple=(0, 0, 0, 0), pad_color: Tuple=(0, 0, 0)):
    """
    pad the input image.

    Args:
        image (_type_): input image
        padding (Tuple, optional): (top, bottom, left, right) padding values. Defaults to (0, 0, 0, 0).
        pad_color (Tuple, optional): BGR color tuple. Defaults to (0, 0, 0).

    Returns:
        np.ndarray: padded image
    """
    top, bottom, left, right = padding
    padded_image = cv.copyMakeBorder(image, top, bottom, left, right, cv.BORDER_CONSTANT, value=pad_color)

    return padded_image

def make_square_image(image: np.ndarray, pad_color: Tuple=(0, 0, 0)):
    """
    make the input image square by padding the shorter side.

    Args:
        image (np.ndarray): input image
        pad_color (Tuple, optional): BGR color tuple. Defaults to (0, 0, 0).

    Returns:
        np.ndarray: square image
    """
    h, w, c = image.shape
    if h == w:
        return image
    elif h > w:
        diff = h - w
        left_pad = diff // 2
        right_pad = diff - left_pad
        padding = (0, 0, left_pad, right_pad)
    else:
        diff = w - h
        top_pad = diff // 2
        bottom_pad = diff - top_pad
        padding = (top_pad, bottom_pad, 0, 0)
    
    square_image = pad_image(image, padding=padding, pad_color=pad_color)
    return square_image


def put_text(
        image,
        text: str,
        text_color: Tuple = (0, 255, 0),
        text_location: Tuple = (0, 0),
        text_position: Tuple = "left",
        background: bool = False,
        background_color: Tuple = (0, 0, 0),
):
    """_summary_

    Args:
        image (nd.array): input image.
        text (str): Text to be put on the image.
        text_color (Tuple, optional): BGR color tuple. Defaults to (0, 255, 0).
        text_location (Tuple, optional): top left corner, default is (0, 0) which is slight low and left from the default value. Defaults to (0, 0).
        text_position (Tuple, optional): left or centre. Defaults to "left".
        background (bool, optional): put text upon the background rectangle. Defaults to False.
        background_color (Tuple, optional): BGR color of the background. Defaults to (0, 0, 0).

    Returns:
        _type_: image as nd.array
    """

    cloned_image = np.copy(image)
    h, w, c = cloned_image.shape

    fontFace = cv.FONT_HERSHEY_COMPLEX
    fontScale = max(0.50, 0.002*h)
    thickness = max(1, int(0.002*w))

    size, size_int = cv.getTextSize(text, fontFace, fontScale, thickness)
    text_width, text_height = size

    text_location_left = (text_location[0]+int(w/55), text_location[1]+text_height)
    text_location_center = (text_location[0]+int(w//2) - (text_width//2), text_location[1]+text_height)

    updated_text_location = text_location_left if text_position == "left" else text_location_center

    if background:
        cloned_image = cv.rectangle(
            cloned_image, 
            (updated_text_location[0], updated_text_location[1]-text_height), 
            (updated_text_location[0]+text_width, updated_text_location[1] + int(0.01*h)), 
            background_color, 
            -1,
            cv.LINE_4
        )
    
    cloned_image = cv.putText(
        cloned_image,
        text=text,
        org=updated_text_location,
        fontFace=cv.FONT_HERSHEY_COMPLEX,
        fontScale=fontScale,
        color=text_color,
        thickness=thickness,
        lineType=cv.LINE_4
    )

    return cloned_image


def draw_label(
        image,
        text: str,
        text_color: Tuple = (0, 255, 0),
        bbox_color: Tuple = (0, 0, 0),
        point1: Tuple = (0, 0),
        point2: Tuple = (0, 0),
        background: bool = False,
        background_color: Tuple = (0, 0, 0),
):
    """_summary_

    Args:
        image (_type_): input image
        text (str): Text to be put on the image.
        text_color (Tuple, optional): BGR color tuple. Defaults to (0, 255, 0).
        bbox_color (Tuple, optional): BGR color tuple. Defaults to (0, 0, 0).
        point1 (Tuple, optional): Left-Top corner of the bounding box. Defaults to (0, 0).
        point2 (Tuple, optional): Right-Bottom corner of the bounding box. Defaults to (0, 0).
        background (bool, optional): Draw text background rectangle. Defaults to False.
        background_color (Tuple, optional): Label background rectangle color. Defaults to (0, 0, 0).

    Returns:
        _type_: _description_
    """
    cloned_image = np.copy(image)
    h, w, c = cloned_image.shape

    fontFace = cv.FONT_HERSHEY_COMPLEX
    fontScale = max(0.50, 0.002*h)
    thickness = max(1, int(0.002*w))

    size, size_int = cv.getTextSize(text, fontFace, fontScale, thickness)
    text_width, text_height = size

    cloned_image = cv.rectangle(
        cloned_image, 
        point1, 
        point2,
        background_color, 
        thickness,
        cv.LINE_4
    )

    updated_text_location = point1

    if background:
        cloned_image = cv.rectangle(
            cloned_image, 
            (updated_text_location[0], updated_text_location[1]-text_height - int(0.01*h)), 
            (updated_text_location[0]+text_width, updated_text_location[1]), 
            bbox_color, 
            -1,
            cv.LINE_4
        )

    updated_text_location = (point1[0], point1[1]- int(0.01*h))

    cloned_image = cv.putText(
        cloned_image,
        text=text,
        org=updated_text_location,
        fontFace=cv.FONT_HERSHEY_COMPLEX,
        fontScale=fontScale,
        color=text_color,
        thickness=thickness,
        lineType=cv.LINE_4
    )

    return cloned_image    
    

if __name__ == "__main__":
    pass
