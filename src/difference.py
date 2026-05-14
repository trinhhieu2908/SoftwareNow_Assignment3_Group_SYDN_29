# difference.py
# This file holds the base class for a difference patch and all five
# types of visual alterations we can apply to an image.
#
# The idea is simple: DifferenceRegion is the parent that handles all the
# shared stuff (position, hit-testing, overlap checks), and each subclass
# just overrides apply() to do its own thing to the image.
# That way adding a new alteration type later is just adding one new class.

import abc
import random

import cv2
import numpy as np

from .constants import PATCH_W, PATCH_H, OVERLAP_MARGIN, CLICK_TOLERANCE


class DifferenceRegion(abc.ABC):
    """
    Every difference patch in the game is one of these.
    It knows where it lives, whether the player has found it,
    and how to check if a click landed on it.

    apply() is left abstract so each subclass can do its own alteration.
    """

    def __init__(self, x: int, y: int, width: int = PATCH_W, height: int = PATCH_H) -> None:
        # Store position and size as private so nothing outside can mess with them
        self._x      = x
        self._y      = y
        self._width  = width
        self._height = height
        self._found  = False   # starts unfound, obviously

    # Every subclass must implement this with its own visual change
    @abc.abstractmethod
    def apply(self, image: np.ndarray) -> None:
        """Modify the image in-place inside this patch's area."""

    # --- Read-only access to position/size ---

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def found(self) -> bool:
        return self._found

    # found CAN be set from outside (GameState needs to mark it)
    @found.setter
    def found(self, value: bool) -> None:
        self._found = value

    # --- Utility methods all subclasses share ---

    def centre(self) -> tuple:
        """Middle of the patch, used for hit-testing and drawing circles."""
        return (self._x + self._width // 2, self._y + self._height // 2)

    def hit_test(self, px: int, py: int, tolerance: int = CLICK_TOLERANCE) -> bool:
        """Returns True if the click (px, py) is close enough to this patch."""
        cx, cy = self.centre()
        return abs(px - cx) <= tolerance and abs(py - cy) <= tolerance

    def overlaps(self, other: "DifferenceRegion", margin: int = OVERLAP_MARGIN) -> bool:
        """
        Returns True if this patch and another are too close together.
        We use this when placing patches to make sure they never bunch up.
        """
        return not (
            self._x + self._width  + margin <= other._x or
            other._x + other._width  + margin <= self._x or
            self._y + self._height + margin <= other._y or
            other._y + other._height + margin <= self._y
        )

    def _region(self, image: np.ndarray) -> np.ndarray:
        """Grab just the slice of the image this patch covers."""
        return image[self._y : self._y + self._height,
                     self._x : self._x + self._width]

    def _write_region(self, image: np.ndarray, data: np.ndarray) -> None:
        """Write altered pixel data back into the same slice."""
        image[self._y : self._y + self._height,
              self._x : self._x + self._width] = data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self._x}, y={self._y}, found={self._found})"


# --- The five alteration types ---
# Each one just overrides apply() and does its own thing.


class ColourShiftDifference(DifferenceRegion):
    """
    Shifts the hue of the patch by a random amount.
    Subtle enough that you have to look carefully, but noticeable once you see it.
    """

    def __init__(self, x: int, y: int, width: int = PATCH_W, height: int = PATCH_H) -> None:
        super().__init__(x, y, width, height)
        self._hue_shift = random.randint(20, 40)   # different every time

    def apply(self, image: np.ndarray) -> None:
        # Convert to HSV, rotate the hue, convert back
        region = self._region(image)
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[:, :, 0] = (hsv[:, :, 0] + self._hue_shift) % 180
        self._write_region(image, cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR))


class BlurDifference(DifferenceRegion):
    """
    Blurs the patch so the detail is gone but the colours stay similar.
    Easy to spot on a sharp image, trickier on a busy one.
    """

    _KERNEL = (21, 21)

    def apply(self, image: np.ndarray) -> None:
        blurred = cv2.GaussianBlur(self._region(image), self._KERNEL, 0)
        self._write_region(image, blurred)


class BrightnessDifference(DifferenceRegion):
    """
    Makes the patch noticeably brighter without changing the colour.
    Works best on darker areas of the image.
    """

    _BETA = 55   # how much brighter (out of 255)

    def apply(self, image: np.ndarray) -> None:
        brightened = cv2.convertScaleAbs(self._region(image), alpha=1.0, beta=self._BETA)
        self._write_region(image, brightened)


class NoiseDifference(DifferenceRegion):
    """
    Adds random noise to every pixel, giving the patch a grainy look.
    Blends in surprisingly well on textured images.
    """

    _AMPLITUDE = 45   # how noisy (±45 per channel)

    def apply(self, image: np.ndarray) -> None:
        region = self._region(image)
        noise  = np.random.randint(-self._AMPLITUDE, self._AMPLITUDE,
                                   region.shape, dtype=np.int16)
        noisy  = np.clip(region.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        self._write_region(image, noisy)


class PixelateDifference(DifferenceRegion):
    """
    Shrinks the patch down to 8×8 then blows it back up with nearest-neighbour,
    so you get that classic blocky pixelated look.
    """

    _THUMBNAIL = 8

    def apply(self, image: np.ndarray) -> None:
        region    = self._region(image)
        small     = cv2.resize(region, (self._THUMBNAIL, self._THUMBNAIL),
                               interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(small, (self._width, self._height),
                               interpolation=cv2.INTER_NEAREST)
        self._write_region(image, pixelated)
