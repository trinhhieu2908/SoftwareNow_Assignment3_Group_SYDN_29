# image_processor.py
# Handles everything to do with loading and modifying images.
# The GUI never touches OpenCV directly — it just calls methods on this class.

import random

import cv2
import numpy as np
from PIL import Image, ImageTk

from constants import (
    NUM_DIFFERENCES, PATCH_W, PATCH_H,
    EDGE_MARGIN, CANVAS_MAX_W, CANVAS_MAX_H,
)
from difference import (
    DifferenceRegion,
    ColourShiftDifference,
    BlurDifference,
    BrightnessDifference,
    NoiseDifference,
    PixelateDifference,
)


class ImageProcessor:
    """
    Loads images from disk, creates a modified copy with hidden differences,
    and handles scaling and format conversion for the GUI.
    """

    # All the alteration types we can randomly pick from.
    # Want to add a new one? Just create the subclass in difference.py and drop it here.
    _ALTERATION_CLASSES = [
        ColourShiftDifference,
        BlurDifference,
        BrightnessDifference,
        NoiseDifference,
        PixelateDifference,
    ]

    def __init__(self) -> None:
        self._original = None   # the image as loaded from disk
        self._modified = None   # the copy we've added differences to

    # Keep the raw arrays private so nothing outside can overwrite them by accident
    @property
    def original(self):
        return self._original

    @property
    def modified(self):
        return self._modified

    def load_image(self, filepath: str) -> np.ndarray:
        """
        Load an image from disk. Supports JPG, PNG and BMP.
        Raises ValueError if OpenCV can't read the file.
        """
        img = cv2.imread(filepath)
        if img is None:
            raise ValueError(f"Could not read image:\n{filepath}")
        self._original = img
        self._modified = None   # reset so stale data doesn't linger
        return self._original

    def generate_differences(self) -> list:
        """
        Make a copy of the original and randomly inject NUM_DIFFERENCES patches
        into it. Patches are placed so they never overlap each other.

        Returns the list of DifferenceRegion objects so GameState can track them.
        """
        if self._original is None:
            raise RuntimeError("Load an image first before generating differences.")

        self._modified = self._original.copy()
        differences    = []
        img_h, img_w   = self._original.shape[:2]
        max_attempts   = 3_000   # safety cap so we don't loop forever on tiny images

        for _ in range(max_attempts):
            if len(differences) == NUM_DIFFERENCES:
                break

            # Pick a random spot that's not too close to the edge
            x = random.randint(EDGE_MARGIN, img_w - PATCH_W - EDGE_MARGIN)
            y = random.randint(EDGE_MARGIN, img_h - PATCH_H - EDGE_MARGIN)

            # Pick a random alteration type and create the patch object
            cls       = random.choice(self._ALTERATION_CLASSES)
            candidate = cls(x, y)

            # Skip if it would overlap an already-placed patch
            if any(candidate.overlaps(placed) for placed in differences):
                continue

            # Apply the alteration to our modified copy (polymorphic — each subclass does its own thing)
            candidate.apply(self._modified)
            differences.append(candidate)

        return differences

    def scale_to_fit(self, image: np.ndarray,
                     max_w: int = CANVAS_MAX_W,
                     max_h: int = CANVAS_MAX_H) -> tuple:
        """
        Shrink the image so it fits inside the canvas without stretching it.
        We never upscale — if the image is already smaller it stays as-is.
        Returns (scaled_image, scale_factor).
        """
        img_h, img_w = image.shape[:2]
        scale  = min(max_w / img_w, max_h / img_h, 1.0)
        new_w  = max(1, int(img_w * scale))
        new_h  = max(1, int(img_h * scale))
        scaled = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return scaled, scale

    @staticmethod
    def to_photoimage(cv2_image: np.ndarray) -> ImageTk.PhotoImage:
        """
        Convert an OpenCV image (BGR) into something Tkinter can actually display.
        OpenCV uses BGR order, Tkinter wants RGB, so we flip the channels first.
        """
        rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return ImageTk.PhotoImage(Image.fromarray(rgb))