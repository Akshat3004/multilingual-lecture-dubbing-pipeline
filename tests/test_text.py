import unittest
from lecture_dubber.text import chunk_text, require_language, translate_text

class TextUtilitiesTests(unittest.TestCase):
    def test_preserves_words_across_chunks(self):
        original = "This is an example of lecture translation and segmentation."
        segments = chunk_text(original, max_characters=18)
        self.assertGreater(len(segments), 1)
        self.assertEqual(" ".join(segments), original)
        self.assertTrue(all(len(s) <= 18 for s in segments))

    def test_empty_input(self):
        self.assertEqual(chunk_text("  \n  "), [])
        with self.assertRaises(ValueError):
            translate_text("  ", lambda text: text)

    def test_rejects_overlong_single_word(self):
        with self.assertRaises(ValueError):
            chunk_text("supercalifragilisticexpialidocious", 5)

    def test_translation_callback(self):
        seen = []
        def fake_provider(text):
            seen.append(text)
            return text.upper()
        translation = translate_text("one two three four", fake_provider, max_characters=8)
        self.assertEqual(translation, "ONE TWO THREE FOUR")
        self.assertGreater(len(seen), 1)

    def test_unavailable_language(self):
        self.assertEqual(require_language("hi"), "hi")
        self.assertEqual(require_language("ta"), "ta")
        with self.assertRaises(ValueError):
            require_language("fr")

if __name__ == "__main__":
    unittest.main()
