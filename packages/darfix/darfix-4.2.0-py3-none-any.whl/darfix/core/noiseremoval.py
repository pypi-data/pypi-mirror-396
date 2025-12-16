from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from enum import Enum as _Enum
from typing import Any
from typing import Callable
from typing import TypedDict

import numpy
from tqdm import tqdm

from darfix.core.utils import OperationAborted

from ..dtypes import Dataset
from ..processing import imageOperations
from .state_of_operation import Operation


class BackgroundType(_Enum):
    DATA = "Data"
    UNUSED_DATA = "Unused data (after partition)"
    DARK_DATA = "Dark data"


class NoiseRemovalOperation(TypedDict):
    type: Operation
    parameters: dict[str, Any]


def operation_to_str(op: NoiseRemovalOperation) -> str:
    result = None
    op_type = op["type"]
    if op_type is Operation.BS:
        result = f"Background subtraction {op['parameters']}"

    elif op_type is Operation.HP:
        result = f"Hot pixel removal: {op['parameters']}"

    elif op_type is Operation.THRESHOLD:
        result = f"Threshold removal: {op['parameters']}"

    elif op_type is Operation.MASK:
        result = "Mask removal"
    else:
        raise ValueError(f"Unknown operation type {op_type}")
    return result


def clean_operation_dict(op: NoiseRemovalOperation) -> dict:
    """Just keep `type` and `parameters` in the saved dict"""
    return {
        "type": op["type"],
        "parameters": op["parameters"],
    }


def apply_noise_removal_operation(
    image: numpy.ndarray, operation: NoiseRemovalOperation
) -> None:
    if operation["type"] is Operation.BS:
        apply_background_substraction(image, operation["background"])

    if operation["type"] is Operation.HP:
        apply_hot_pixel_removal(image, **operation["parameters"])

    if operation["type"] is Operation.THRESHOLD:
        apply_threshold_removal(image, **operation["parameters"])

    if operation["type"] is Operation.MASK:
        apply_mask_removal(image, **operation["parameters"])


def add_background_data_into_operation(
    dataset: Dataset,
    operation: NoiseRemovalOperation,
) -> NoiseRemovalOperation:
    """Compute a background image and return a NoiseRemovalOperation with a background parameter"""

    if operation["type"] is not Operation.BS:
        raise ValueError("Operation type should be `Operation.BS`")

    method = operation["parameters"].get("method", imageOperations.Method.MEDIAN)

    background_type = BackgroundType(
        operation["parameters"].get("background_type", BackgroundType.DATA.value)
    )

    if background_type is BackgroundType.DARK_DATA:
        bg = dataset.bg_dataset.as_array3d()
    elif background_type is BackgroundType.UNUSED_DATA:
        bg = dataset.dataset.as_array3d(dataset.bg_indices)
    elif background_type is BackgroundType.DATA:
        bg = dataset.dataset.as_array3d()
    else:
        raise NotImplementedError(
            f"Background type {background_type!r} not implemented yet."
        )

    operation["background"] = imageOperations.compute_background(bg, method)


def apply_background_substraction(
    image: numpy.ndarray, background: numpy.ndarray
) -> None:
    imageOperations.background_subtraction(image, background)


def apply_hot_pixel_removal(
    image: numpy.ndarray, kernel_size: int | None = None
) -> None:
    if kernel_size is None:
        kernel_size = 3

    imageOperations.hot_pixel_removal(image, ksize=kernel_size)


def apply_threshold_removal(
    image: numpy.ndarray, bottom: int | None = None, top: int | None = None
) -> None:
    imageOperations.threshold_removal(image, bottom=bottom, top=top)


def apply_mask_removal(image: numpy.ndarray, mask: numpy.ndarray | None) -> None:
    if mask is None:
        return
    imageOperations.mask_removal(image, mask)


def apply_noise_removal_operations(
    image_stack: numpy.ndarray,
    operations: list[NoiseRemovalOperation],
    is_cancel: Callable[[], bool],
    set_progress: Callable[[int], None],
    max_workers: int | None = None,
) -> None:
    if image_stack.ndim != 3:
        raise ValueError(
            f"image_stack must have ndim == 3 but ndims is {image_stack.ndim}"
        )

    def process_single(img: numpy.ndarray):
        if is_cancel():
            return
        for op in operations:
            try:
                apply_noise_removal_operation(img, operation=op)
            except Exception as e:
                # Return e to re-raise Exception in the parent thread
                return e

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single, img) for img in image_stack]
        len_futures = len(futures)
        for idx_future, future in tqdm(
            enumerate(as_completed(futures)),
            desc="Noise removal operation",
            total=len_futures,
        ):
            exception = future.result()
            if isinstance(exception, Exception):
                raise exception
            if is_cancel():
                raise OperationAborted()
            set_progress(idx_future * 100 // len_futures)
