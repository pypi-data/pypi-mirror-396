import unittest
from get_snirh import Snirh, Parameters

class TestSnirhStructure(unittest.TestCase):
    def test_imports(self):
        """Test that we can import the main classes."""
        snirh = Snirh()
        self.assertIsNotNone(snirh.client)
        self.assertIsNotNone(snirh.stations)
        self.assertIsNotNone(snirh.data)

    def test_parameters(self):
        """Test that parameters are available."""
        self.assertEqual(Parameters.PRECIPITATION_DAILY.value, '413026594')

if __name__ == '__main__':
    unittest.main()
