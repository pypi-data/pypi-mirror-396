import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("gradio"), "gradio not installed")
class TestUI(unittest.TestCase):
    def test_gradio_available(self):
        import gradio  # noqa: F401

        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
