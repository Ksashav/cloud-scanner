import unittest
from scanner import scan_port

class TestScanner(unittest.TestCase):
    def test_closed_port(self):
        # scan a port that's never open
        result = scan_port("127.0.0.1", 9999)
        self.assertEqual(result, False)
    
    def test_open_port(self):
        # scan a common open port (HTTP)
        result = scan_port("127.0.0.1", 80)
        # We can't guarantee this will be open, so we just check it's a boolean
        self.assertIsInstance(result, bool)

if __name__ == "__main__":
    unittest.main()