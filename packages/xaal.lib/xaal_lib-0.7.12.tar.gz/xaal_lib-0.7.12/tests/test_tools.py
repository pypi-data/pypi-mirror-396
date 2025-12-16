import unittest
from xaal.lib import tools
from xaal.lib import bindings


class TestTools(unittest.TestCase):


    def test_random(self):
        value = tools.get_random_uuid()
        self.assertIsInstance(value, bindings.UUID)

        value = tools.get_random_base_uuid()
        self.assertIsInstance(value, bindings.UUID)

    def test_get_uuid(self):
        uuid = bindings.UUID.random()
        addr = tools.get_uuid(uuid)
        self.assertEqual(addr, uuid)

        addr = tools.get_uuid("12345678-1234-1234-1234-123456789012")
        self.assertEqual(addr, bindings.UUID("12345678-1234-1234-1234-123456789012"))
        self.assertEqual(None, tools.get_uuid(12))

    def test_str_to_uuid(self):
        addr = tools.get_uuid("12345678-1234-1234-1234-123456789012")
        self.assertEqual(tools.str_to_uuid("12345678-1234-1234-1234-123456789012"), addr)
        self.assertEqual(tools.str_to_uuid("0"),None)

    def test_bytes_to_uuid(self):
        addr = bindings.UUID("12345678-1234-1234-1234-123456789012")
        value = tools.bytes_to_uuid(addr.bytes)
        self.assertEqual(value, addr)
        self.assertEqual(tools.bytes_to_uuid(b'0000'), None)

    def test_pass2key(self):
        key = "test"
        value = tools.pass2key(key)
        self.assertEqual(value, b'q\xc1\xc8]\x8ey\xd5\x8cC\xf5CF\xe67\xab\x1c\xd0\xfa\x82\r\x0br6a\xca]\\\xb2@6\xaf\xcf')

    def test_is_valid_dev_type(self):
        self.assertTrue(tools.is_valid_dev_type("light.basic"))
        self.assertFalse(tools.is_valid_dev_type("light"))
        self.assertFalse(tools.is_valid_dev_type(42))

    def test_reduce_addr(self):
        addr = bindings.UUID("12345678-1234-1234-1234-123456789012")
        value = tools.reduce_addr(addr)
        self.assertEqual(value, '12345..89012')


if __name__ == '__main__':
    unittest.main()