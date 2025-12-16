import unittest
import importlib


class TestImports(unittest.TestCase):
    def test_package_imports(self):
        # Verify the package and modules import without initializing a display
        importlib.import_module('earthplus')
        importlib.import_module('earthplus.window')
        importlib.import_module('earthplus.objects')
        importlib.import_module('earthplus.renderer')

    def test_external_dependencies(self):
        # Verify external dependencies can be imported (if installed)
        importlib.import_module('pygame')
        importlib.import_module('OpenGL')


if __name__ == '__main__':
    unittest.main()
