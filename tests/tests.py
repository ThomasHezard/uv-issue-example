import unittest
import example

class TestExample(unittest.TestCase):
    def test_tomli(self):
        import tomli
        print(f"Hello with tomli {tomli.__version__}")
    def test_example(self):
        print(example.hello())

if __name__ == '__main__':
    unittest.main()
