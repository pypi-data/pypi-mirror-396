import unittest
from anki_card_cleaner import clean_card_text

class TestCleanCardText(unittest.TestCase):
    def test_basic_string(self):
        self.assertEqual(clean_card_text("Hello World"), "hello world")

    def test_non_string_input(self):
        self.assertEqual(clean_card_text(None), "")
        self.assertEqual(clean_card_text(123), "")
        self.assertEqual(clean_card_text(float('nan')), "")

    def test_non_breaking_spaces(self):
        self.assertEqual(clean_card_text("Hello\xa0World"), "hello world")

    def test_cloze_deletion_basic(self):
        # {{c1::Answer}} -> answer
        self.assertEqual(clean_card_text("The capital of France is {{c1::Paris}}."), "the capital of france is paris.")

    def test_cloze_deletion_with_hint(self):
        # {{c1::Answer::Hint}} -> answer (hint)
        self.assertEqual(clean_card_text("The capital of France is {{c1::Paris::City}}."), "the capital of france is paris (city).")

    def test_single_bracket_cloze(self):
         # {c1::Answer} -> answer
        self.assertEqual(clean_card_text("The capital of France is {c1::Paris}."), "the capital of france is paris.")

    def test_question_mark_spacing(self):
        self.assertEqual(clean_card_text("What is it?It is a cat."), "what is it? it is a cat.")
        self.assertEqual(clean_card_text("What is it?  It is a cat."), "what is it? it is a cat.")

    def test_whitespace_normalization(self):
        self.assertEqual(clean_card_text("  Much   Space \n Here "), "much space here")

if __name__ == '__main__':
    unittest.main()
