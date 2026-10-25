import os
import unittest

# bot.py validates its token at import time; tests use a dummy value and never connect to Telegram.
os.environ.setdefault("BOT_TOKEN", "test-token")

from bot import safe_calculate


class SafeCalculatorTests(unittest.TestCase):
    def test_operator_precedence(self):
        self.assertEqual(safe_calculate("1 + 2 * 3"), 7)

    def test_parentheses_and_unary_operators(self):
        self.assertEqual(safe_calculate("-(4 + 2)"), -6)

    def test_rejects_power_operator(self):
        with self.assertRaises(ValueError):
            safe_calculate("2 ** 100")

    def test_rejects_names_and_calls(self):
        with self.assertRaises(ValueError):
            safe_calculate("__import__('os').system('id')")

    def test_rejects_long_input(self):
        with self.assertRaises(ValueError):
            safe_calculate("1" * 101)


if __name__ == "__main__":
    unittest.main()
