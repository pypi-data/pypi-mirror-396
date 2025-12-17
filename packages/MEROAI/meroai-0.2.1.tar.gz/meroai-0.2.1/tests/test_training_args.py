import os
import tempfile
import unittest
from MEROAI import TrainingArguments
class TestTrainingArguments(unittest.TestCase):
    def test_default_output_dir(self):
        args = TrainingArguments(output_dir=None)
        self.assertEqual(args.output_dir, "trainer_output")
    def test_custom_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            args = TrainingArguments(output_dir=tmp_dir)
            self.assertEqual(args.output_dir, tmp_dir)
    def test_output_dir_creation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = os.path.join(tmp_dir, "test_output")
            self.assertFalse(os.path.exists(output_dir))
            args = TrainingArguments(
                output_dir=output_dir,
                do_train=True,
                save_strategy="no",
                report_to=None,
            )
            self.assertFalse(os.path.exists(output_dir))
            args.save_strategy = "steps"
            args.save_steps = 1
            self.assertFalse(os.path.exists(output_dir))
    def test_torch_empty_cache_steps_requirements(self):
        args = TrainingArguments(torch_empty_cache_steps=None)
        self.assertIsNone(args.torch_empty_cache_steps)
        with self.assertRaises(ValueError):
            TrainingArguments(torch_empty_cache_steps=1.0)
        with self.assertRaises(ValueError):
            TrainingArguments(torch_empty_cache_steps="none")
        with self.assertRaises(ValueError):
            TrainingArguments(torch_empty_cache_steps=-1)
        with self.assertRaises(ValueError):
            TrainingArguments(torch_empty_cache_steps=0)
        args = TrainingArguments(torch_empty_cache_steps=1)
        self.assertEqual(args.torch_empty_cache_steps, 1)