import unittest
from xaal.lib import bindings


class TestUUID(unittest.TestCase):


    def test_add_sub(self):
        uuid = bindings.UUID("12345678-1234-1234-1234-123456789012")
        uuid += 1
        self.assertEqual(uuid,bindings.UUID("12345678-1234-1234-1234-123456789013"))
        uuid -= 1
        self.assertEqual(uuid,bindings.UUID("12345678-1234-1234-1234-123456789012"))

    def test_random(self):
        uuid = bindings.UUID.random()
        self.assertIsInstance(uuid,bindings.UUID)

        uuid = bindings.UUID.random_base()
        self.assertIsInstance(uuid,bindings.UUID)

        with self.assertRaises(bindings.UUIDError):
            uuid = bindings.UUID.random_base(0)

    def test_get_set(self):
        uuid1 = bindings.UUID("12345678-1234-1234-1234-123456789012")
        data = uuid1.get()
        uuid2 = bindings.UUID.random()
        uuid2.set(data)
        self.assertEqual(uuid1,uuid2)

    def test_str(self):
        uuid = bindings.UUID("12345678-1234-1234-1234-123456789012")
        self.assertEqual(str(uuid),"12345678-1234-1234-1234-123456789012")
        self.assertEqual(uuid.str,"12345678-1234-1234-1234-123456789012")

    def test_bytes(self):
        uuid = bindings.UUID("12345678-1234-1234-1234-123456789012")
        self.assertEqual(uuid.bytes,b'\x124Vx\x124\x124\x124\x124Vx\x90\x12')


class TestURL(unittest.TestCase):

    def test_url(self):
        url = bindings.URL("http://bar.com")
        self.assertEqual(str(url), "http://bar.com")
        url.set("http://foo.com")
        print(url)
        self.assertEqual(str(url), "http://foo.com")
        self.assertEqual(url.str, "http://foo.com")
        self.assertEqual(url.get(), "http://foo.com")
        self.assertEqual(url.bytes, "http://foo.com")


if __name__ == '__main__':
    unittest.main()