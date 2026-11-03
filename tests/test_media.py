import unittest
from pathlib import Path
from unittest.mock import patch
from lecture_dubber.media import mismatch_ratio, mux_video

class MediaTests(unittest.TestCase):
    def test_media_duration_guard(self):
        self.assertAlmostEqual(mismatch_ratio(88.2, 134.16), 0.52108843537, places=7)
        self.assertAlmostEqual(mismatch_ratio(100, 100), 0)
        with self.assertRaises(ValueError):
            mismatch_ratio(0, 1)

    @patch("lecture_dubber.media.duration_seconds", side_effect=[88.2, 134.16])
    @patch("lecture_dubber.media.subprocess.run")
    def test_mismatched_audio_cannot_mux(self, mocked_run, mocked_probe):
        with self.assertRaisesRegex(ValueError, "Perform sentence-level timing alignment"):
            mux_video(Path("source.mp4"), Path("dub.mp3"), Path("output.mp4"))
        mocked_run.assert_not_called()

    def test_mux_output_must_differ_from_input(self):
        with self.assertRaises(ValueError):
            mux_video(Path("lecture.mp4"), Path("dub.mp3"), Path("lecture.mp4"))

if __name__ == "__main__":
    unittest.main()
