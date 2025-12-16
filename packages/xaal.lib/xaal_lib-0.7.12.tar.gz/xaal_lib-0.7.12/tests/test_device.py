import unittest
from xaal.lib import tools
from xaal.lib import Device,DeviceError,Attribute,Engine
from xaal.lib.devices import Attributes


def new_dev() -> Device:
    addr = tools.get_random_uuid()
    dev = Device("light.basic",addr=addr)
    return dev

class TestAttribute(unittest.TestCase):

    def test_default(self):
        attr = Attribute("foo",dev=new_dev(),default=1)
        self.assertEqual(attr.value,1)
        attr.value = 12
        self.assertEqual(attr.value,12)

    def test_with_engine(self):
        dev = new_dev()
        dev.engine = Engine()
        attr = Attribute("foo",dev=dev,default=1,)
        attr.value = 12
        self.assertEqual(attr.value,12)

class TestAttributes(unittest.TestCase):

    def test_default(self):
        dev = new_dev()
        attr = Attribute("foo",dev=dev,default=1)
        attrs = Attributes()
        attrs.append(attr)
        self.assertEqual(attrs[0].value,1)
        self.assertEqual(attrs["foo"],1)

        with self.assertRaises(KeyError):
            attrs["bar"]

        attrs[0] = Attribute("bar",dev=dev,default=2)
        self.assertEqual(attrs[0].value,2)

        attrs["bar"] = 12
        self.assertEqual(attrs["bar"],12)

        with self.assertRaises(KeyError):
            attrs["nop"]=12


class TestDevice(unittest.TestCase):

    def test_init(self):
        dev_type="light.basic"
        addr = tools.get_random_uuid()
        dev = Device(dev_type=dev_type,addr=addr)
        self.assertEqual(dev.dev_type, dev_type)
        self.assertEqual(dev.address, addr)

    def test_address(self):
        dev = new_dev()
        # address
        addr = tools.get_random_uuid()
        dev.address = addr
        self.assertEqual(dev.address, addr)
        # none address
        dev.address = None
        self.assertEqual(dev.address, None)
        # invalid address
        with self.assertRaises(DeviceError):
            dev.address = "foo"

    def test_dev_type(self):
        dev = new_dev()
        dev.dev_type = "foo.basic"
        self.assertEqual(dev.dev_type, "foo.basic")
        with self.assertRaises(DeviceError):
            dev.dev_type = "foo"

    def test_version(self):
        dev = new_dev()
        # version 
        dev.version = 12
        self.assertEqual(dev.version, '12')
        dev.version = None
        self.assertEqual(dev.version, None)

    def test_url(self):
        dev = new_dev()
        dev.url = "http://foo.bar"
        self.assertEqual(dev.url, "http://foo.bar")
        dev.url = None
        self.assertEqual(dev.url, None)

    def test_attributes(self):
        dev = new_dev()
        attr = Attribute("foo",dev=dev,default=1)
        # add
        dev.add_attribute(attr)
        self.assertEqual(len(dev.attributes),1)
        self.assertEqual(dev.attributes[0],attr)
        # del
        dev.del_attribute(attr)
        self.assertEqual(len(dev.attributes),0)
        # new
        dev.new_attribute("foo",default=2)
        self.assertEqual(len(dev.attributes),1)
        self.assertEqual(dev.attributes[0].value,2)
        # get
        self.assertEqual(dev.get_attribute("foo").value,2)
        self.assertEqual(dev.get_attribute("bar"),None)
        
        # set
        attr = Attribute("bar",dev=dev,default=3)
        dev.attributes =Attributes([attr,])
        self.assertEqual(len(dev.attributes),1)
        self.assertEqual(dev.attributes[0].value,3)
        # only accepts Attributes not list 
        with self.assertRaises(DeviceError):
            dev.attributes = [attr,]

    def test_get_attributes(self):
        dev = new_dev()
        dev.new_attribute("foo",default=1)
        # _get_attributes
        self.assertEqual(dev._get_attributes()["foo"],1)
        data = dev._get_attributes(["foo","bar"])
        self.assertEqual(len(data),1)
        self.assertEqual(data["foo"],1)

    def test_get_description(self):
        dev = new_dev()

        dev.vendor_id = 0x1234
        dev.product_id = 0x1234
        dev.version = '2f'
        dev.url = "http://foo.bar"
        dev.schema = "http://schemas.foo.bar/schema.json"
        dev.info = "FooBar"
        dev.hw_id = 0xf12
        group = tools.get_random_uuid()
        dev.group_id = group

        dev.unsupported_methods = ["foo_func"]
        dev.unsupported_attributes = ["foo_attr"]
        dev.unsupported_notifications = ["foo_notif"]

        data = dev._get_description()
        self.assertEqual(data["vendor_id"], 0x1234)
        self.assertEqual(data["product_id"], 0x1234)
        self.assertEqual(data["version"], '2f')
        self.assertEqual(data["url"], "http://foo.bar")
        self.assertEqual(data["schema"], "http://schemas.foo.bar/schema.json")
        self.assertEqual(data["info"], "FooBar")
        self.assertEqual(data["hw_id"],0xf12)
        self.assertEqual(data["group_id"],group)

        self.assertEqual(data["unsupported_methods"],["foo_func"])
        self.assertEqual(data["unsupported_notifications"],["foo_notif"])
        self.assertEqual(data["unsupported_attributes"],["foo_attr"])

    def test_methods(self):
        dev = new_dev()
        # device has two methods by default
        self.assertEqual(len(dev.methods),2)
        self.assertEqual(len(dev.get_methods()),2)
        def func():pass
        dev.add_method("foo",func)
        self.assertEqual(dev.methods["foo"],func)

    def test_dump(self):
        dev = new_dev()
        dev.info = 'FooBar'
        dev.new_attribute("foo",default=1)
        dev.dump()

    def test_alive(self):
        import time
        now = time.time()
        dev = new_dev()
        dev.alive_period = 2 
        dev.update_alive()
        self.assertTrue(dev.next_alive > now)
        self.assertTrue(dev.next_alive < now+3)
        self.assertEqual(dev.get_timeout(),4)

    def test_send_notification(self):
        # not really a test here, just to check if the method is called
        # check engine unittest for futher tests
        dev = new_dev()
        dev.engine = Engine()
        dev.send_notification("foo")
        

if __name__ == '__main__':
    unittest.main()