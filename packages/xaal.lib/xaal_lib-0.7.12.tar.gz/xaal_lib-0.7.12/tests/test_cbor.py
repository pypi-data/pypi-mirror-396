import unittest
from xaal.lib import cbor
from xaal.lib import bindings
import binascii


class TestCbor(unittest.TestCase):
    def test_encode(self):
        value = cbor.dumps(42)
        self.assertEqual(value, b"\x18*")  # 0x18 0x2a

    def test_decode(self):
        value = cbor.loads(b"\x18*")
        self.assertEqual(value, 42)

    def test_list(self):
        value = []
        value.append(7)
        value.append(1234567890)
        data = cbor.dumps(value)
        print(data)
        self.assertEqual(data, binascii.unhexlify(b"82071a499602d2"))

    def test_uuid(self):
        uuid = bindings.UUID.random()
        cbor_value = cbor.dumps(uuid)
        value = cbor.loads(cbor_value)
        self.assertEqual(value, uuid)
        self.assertEqual(type(value), bindings.UUID)

    def test_url(self):
        url = bindings.URL("http://www.example.com")
        cbor_value = cbor.dumps(url)
        value = cbor.loads(cbor_value)
        self.assertEqual(value, url)
        self.assertEqual(type(value), bindings.URL)

    def test_cleanup(self):
        data = [
            7,
            "hello",
            bindings.UUID("12345678-1234-1234-1234-123456789012"),
            bindings.URL("http://www.example.com"),
            {"hello": "world"},
        ]
        cbor_value = cbor.dumps(data)
        value = cbor.loads(cbor_value)
        cbor.cleanup(value)
        self.assertEqual(
            value,
            [
                7,
                "hello",
                "12345678-1234-1234-1234-123456789012",
                "http://www.example.com",
                {"hello": "world"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
