import unittest

import numpy as np

try:
    from src.difference import BrightnessDifference, PixelateDifference
except ModuleNotFoundError as exc:
    if exc.name == "cv2":
        raise unittest.SkipTest("OpenCV is not installed") from exc
    raise


class DifferenceRegionTests(unittest.TestCase):
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

    def test_found_property_can_be_updated(self):
        diff = PixelateDifference(0, 0)

        self.assertFalse(diff.found)
        diff.found = True
        self.assertTrue(diff.found)


if __name__ == "__main__":
    unittest.main()
