import sys
from types import SimpleNamespace
import unittest

import numpy as np

try:
    import cv2 as _real_cv2
    HAS_CV2 = True
except ModuleNotFoundError as exc:
    if exc.name == "cv2":
        HAS_CV2 = False
    else:
        raise

_missing_cv2 = object()
_previous_cv2 = sys.modules.get("cv2", _missing_cv2)
if not HAS_CV2:
    sys.modules["cv2"] = SimpleNamespace()

try:
    from src.difference import (
        BlurDifference,
        BrightnessDifference,
        ColourShiftDifference,
        NoiseDifference,
        PixelateDifference,
    )
finally:
    if not HAS_CV2:
        if _previous_cv2 is _missing_cv2:
            sys.modules.pop("cv2", None)
        else:
            sys.modules["cv2"] = _previous_cv2


def needs_cv2(test):
    return unittest.skipUnless(HAS_CV2, "OpenCV is not installed")(test)


class DifferenceRegionTests(unittest.TestCase):
    def assert_only_patch_changes(self, diff):
        rng = np.random.default_rng(7)
        image = rng.integers(0, 256, size=(100, 100, 3), dtype=np.uint8)
        original = image.copy()

        diff.apply(image)

        x1, y1 = diff.x, diff.y
        x2, y2 = diff.x + diff.width, diff.y + diff.height
        self.assertTrue(np.any(image[y1:y2, x1:x2] != original[y1:y2, x1:x2]))
        self.assertTrue(np.array_equal(image[:y1], original[:y1]))
        self.assertTrue(np.array_equal(image[y2:], original[y2:]))
        self.assertTrue(np.array_equal(image[y1:y2, :x1], original[y1:y2, :x1]))
        self.assertTrue(np.array_equal(image[y1:y2, x2:], original[y1:y2, x2:]))

    def test_position_size_and_centre_properties(self):
        diff = BrightnessDifference(12, 18, width=40, height=24)

        self.assertEqual(diff.x, 12)
        self.assertEqual(diff.y, 18)
        self.assertEqual(diff.width, 40)
        self.assertEqual(diff.height, 24)
        self.assertEqual(diff.centre(), (32, 30))

    def test_hit_test_accepts_click_near_centre(self):
        diff = BrightnessDifference(10, 20, width=40, height=30)

        self.assertTrue(diff.hit_test(30, 35, tolerance=0))
        self.assertTrue(diff.hit_test(35, 40, tolerance=5))

    def test_hit_test_rejects_click_outside_tolerance(self):
        diff = BrightnessDifference(10, 20, width=40, height=30)

        self.assertFalse(diff.hit_test(36, 40, tolerance=5))
        self.assertFalse(diff.hit_test(35, 41, tolerance=5))

    def test_overlaps_detects_regions_that_are_too_close(self):
        first = BrightnessDifference(10, 10, width=20, height=20)
        second = BrightnessDifference(25, 25, width=20, height=20)

        self.assertTrue(first.overlaps(second, margin=0))

    def test_overlaps_rejects_regions_with_enough_gap(self):
        first = BrightnessDifference(10, 10, width=20, height=20)
        second = BrightnessDifference(40, 10, width=20, height=20)

        self.assertFalse(first.overlaps(second, margin=10))

    def test_overlaps_uses_margin_when_regions_are_nearby(self):
        first = BrightnessDifference(10, 10, width=20, height=20)
        second = BrightnessDifference(35, 10, width=20, height=20)

        self.assertFalse(first.overlaps(second, margin=5))
        self.assertTrue(first.overlaps(second, margin=6))

    @needs_cv2
    def test_apply_only_changes_the_target_patch(self):
        image = np.full((80, 80, 3), 100, dtype=np.uint8)
        original = image.copy()
        diff = BrightnessDifference(20, 30, width=10, height=10)

        diff.apply(image)

        self.assertTrue(np.any(image[30:40, 20:30] != original[30:40, 20:30]))
        self.assertTrue(np.array_equal(image[:30], original[:30]))
        self.assertTrue(np.array_equal(image[40:], original[40:]))
        self.assertTrue(np.array_equal(image[30:40, :20], original[30:40, :20]))
        self.assertTrue(np.array_equal(image[30:40, 30:], original[30:40, 30:]))

    @needs_cv2
    def test_colour_shift_only_changes_target_patch(self):
        image = np.zeros((80, 80, 3), dtype=np.uint8)
        image[:, :] = [20, 80, 200]
        original = image.copy()
        diff = ColourShiftDifference(15, 25, width=12, height=12)

        diff.apply(image)

        self.assertTrue(np.any(image[25:37, 15:27] != original[25:37, 15:27]))
        self.assertTrue(np.array_equal(image[:25], original[:25]))
        self.assertTrue(np.array_equal(image[37:], original[37:]))
        self.assertTrue(np.array_equal(image[25:37, :15], original[25:37, :15]))
        self.assertTrue(np.array_equal(image[25:37, 27:], original[25:37, 27:]))

    @needs_cv2
    def test_blur_only_changes_target_patch(self):
        self.assert_only_patch_changes(BlurDifference(20, 20, width=30, height=30))

    @needs_cv2
    def test_noise_only_changes_target_patch(self):
        np.random.seed(3)
        self.assert_only_patch_changes(NoiseDifference(20, 20, width=30, height=30))

    @needs_cv2
    def test_pixelate_only_changes_target_patch(self):
        self.assert_only_patch_changes(PixelateDifference(20, 20, width=30, height=30))

    def test_found_property_can_be_updated(self):
        diff = PixelateDifference(0, 0)

        self.assertFalse(diff.found)
        diff.found = True
        self.assertTrue(diff.found)

    def test_repr_includes_class_position_and_found_state(self):
        diff = BrightnessDifference(4, 9, width=10, height=10)

        self.assertEqual(repr(diff), "BrightnessDifference(x=4, y=9, found=False)")


if __name__ == "__main__":
    unittest.main()
