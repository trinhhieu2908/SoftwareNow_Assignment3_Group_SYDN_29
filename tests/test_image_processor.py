import random
import tempfile
import unittest
from pathlib import Path

import numpy as np

try:
    import cv2
except ModuleNotFoundError:
    raise unittest.SkipTest("OpenCV is not installed")


class ImageProcessorTests(unittest.TestCase):
    def setUp(self):
        from src.constants import NUM_DIFFERENCES
        from src.difference import BrightnessDifference
        from src.image_processor import ImageProcessor

        self.BrightnessDifference = BrightnessDifference
        self.ImageProcessor = ImageProcessor
        self.NUM_DIFFERENCES = NUM_DIFFERENCES

    def test_load_image_reads_valid_image_file(self):
        image = np.full((30, 40, 3), 120, dtype=np.uint8)

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sample.png"
            cv2.imwrite(str(path), image)

            processor = self.ImageProcessor()
            loaded = processor.load_image(str(path))

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.shape, image.shape)
        self.assertIs(processor.original, loaded)
        self.assertIsNone(processor.modified)

    def test_load_image_rejects_missing_file(self):
        processor = self.ImageProcessor()

        with self.assertRaises(ValueError):
            processor.load_image("does-not-exist.png")

    def test_scale_to_fit_shrinks_large_image_without_upscaling_small_image(self):
        processor = self.ImageProcessor()
        large = np.zeros((100, 200, 3), dtype=np.uint8)
        small = np.zeros((20, 30, 3), dtype=np.uint8)

        scaled_large, large_scale = processor.scale_to_fit(large, max_w=100, max_h=100)
        scaled_small, small_scale = processor.scale_to_fit(small, max_w=100, max_h=100)

        self.assertEqual(scaled_large.shape[:2], (50, 100))
        self.assertEqual(large_scale, 0.5)
        self.assertEqual(scaled_small.shape[:2], (20, 30))
        self.assertEqual(small_scale, 1.0)

    def test_generate_differences_creates_expected_count_and_modifies_copy(self):
        processor = self.ImageProcessor()
        processor._original = np.full((500, 500, 3), 100, dtype=np.uint8)

        original_classes = self.ImageProcessor._ALTERATION_CLASSES
        try:
            self.ImageProcessor._ALTERATION_CLASSES = [self.BrightnessDifference]
            random.seed(1)

            differences = processor.generate_differences()
        finally:
            self.ImageProcessor._ALTERATION_CLASSES = original_classes

        self.assertEqual(len(differences), self.NUM_DIFFERENCES)
        self.assertIsNotNone(processor.modified)
        self.assertFalse(np.array_equal(processor.original, processor.modified))
        self.assertTrue(
            all(isinstance(diff, self.BrightnessDifference) for diff in differences)
        )

    def test_generate_differences_requires_loaded_image(self):
        processor = self.ImageProcessor()

        with self.assertRaises(RuntimeError):
            processor.generate_differences()


if __name__ == "__main__":
    unittest.main()
