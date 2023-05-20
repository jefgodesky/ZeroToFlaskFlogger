import unittest
loader = unittest.TestLoader()
tests = loader.discover('.')
runner = unittest.runner.TextTestRunner()

if __name__ == '__main__':
    runner.run(tests)
