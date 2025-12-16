import unittest
from xaal.lib import messages
from xaal.lib import Message,MessageError,MessageType,MessageFactory
from xaal.lib import Device
from xaal.lib import tools,cbor
from xaal.lib.exceptions import MessageParserError  


def fake_message():
    msg = Message()
    msg.msg_type = MessageType.REQUEST
    msg.source = tools.get_random_uuid()
    msg.dev_type= "test.basic"
    msg.action = 'test'
    msg.body = {"foo":"bar"}
    msg.timestamp = messages.build_timestamp()
    return msg

def fake_factory():
    # create the factory
    cypher = tools.pass2key('test')
    mf = MessageFactory(cypher)
    return mf


class TestMessage(unittest.TestCase):

    def test_targets(self):
        msg = Message()
        addr = tools.get_random_uuid()
        # target are stored
        msg.targets = [addr]
        self.assertEqual(msg.targets, [addr,])
        # target is list
        with self.assertRaises(MessageError):
            msg.targets = addr
        # target contains invalid uuid
        with self.assertRaises(MessageError):
            msg.targets = ["foo"]

    def test_display(self):
        msg = fake_message()
        print()
        # dump
        msg.dump()
        print(msg)

    def test_targets_as_string(self):
        msg = fake_message()
        addr = tools.get_random_uuid()
        msg.targets = [addr]
        self.assertEqual(msg.targets_as_string(), [str(addr),] )

    def test_is_request(self):
        msg = fake_message()
        msg.msg_type = 1
        self.assertTrue(msg.is_request())
        msg.msg_type = 2
        self.assertFalse(msg.is_request())


    def test_is_reply(self):
        msg = fake_message()
        msg.msg_type = 2
        self.assertTrue(msg.is_reply())
        msg.msg_type = 1
        self.assertFalse(msg.is_reply()) 

    def test_is_notify(self):
        msg = fake_message()
        msg.msg_type = 0
        self.assertTrue(msg.is_notify())
        msg.msg_type = 1
        self.assertFalse(msg.is_notify())

    def test_is_alive(self):
        msg = fake_message()
        msg.msg_type = 0
        msg.action = 'alive'
        self.assertTrue(msg.is_alive())
        msg.action = 'foo'
        self.assertFalse(msg.is_alive())

    def test_is_request_isalive(self):
        msg = fake_message()
        msg.msg_type = 1
        msg.action = 'is_alive'
        self.assertTrue(msg.is_request_isalive())
        msg.action = 'foo'
        self.assertFalse(msg.is_request_isalive())

    def test_is_attributes_change(self):
        msg = fake_message()
        msg.msg_type = 0
        msg.action = 'attributes_change'
        self.assertTrue(msg.is_attributes_change())
        msg.action = 'foo'
        self.assertFalse(msg.is_attributes_change())

    def test_is_get_attribute_reply(self):
        msg = fake_message()
        msg.msg_type = 2
        msg.action = 'get_attributes'
        self.assertTrue(msg.is_get_attribute_reply())
        msg.action = 'foo'
        self.assertFalse(msg.is_get_attribute_reply())
    
    def test_is_get_description_reply(self):
        msg = fake_message()
        msg.msg_type = 2
        msg.action = 'get_description'
        self.assertTrue(msg.is_get_description_reply())
        msg.action = 'foo'
        self.assertFalse(msg.is_get_description_reply())


class TestMessageFactory(unittest.TestCase):

    def test_encode_decode(self):
        msg1 = fake_message()

        mf = fake_factory()
        data = mf.encode_msg(msg1)
        msg2 = mf.decode_msg(data)

        self.assertEqual(msg1.targets, msg2.targets)
        self.assertEqual(msg1.timestamp, msg2.timestamp)
        self.assertEqual(msg1.source, msg2.source)
        self.assertEqual(msg1.dev_type, msg2.dev_type)
        #FIXME decoded msg_type should be a MessageType
        self.assertEqual(msg1.msg_type.value, msg2.msg_type)
        self.assertEqual(msg1.action, msg2.action)
        self.assertEqual(msg1.body, msg2.body)

    def test_build_alive_for(self):
        dev = Device("test.basic",tools.get_random_uuid())
        mf  = fake_factory()
        data = mf.build_alive_for(dev)
        msg  = mf.decode_msg(data)
        self.assertTrue(msg.is_alive())

    def test_build_error_msg(self):
        dev = Device("test.basic",tools.get_random_uuid())
        mf  = fake_factory()
        data = mf.build_error_msg(dev, 500,"Internal Error")
        msg  = mf.decode_msg(data)
        self.assertTrue(msg.is_notify())
        self.assertEqual(msg.action, 'error')
        self.assertEqual(msg.body['code'], 500)

    def test_decode_cbor_parse_error(self):
        mf = fake_factory()
        with self.assertRaises(MessageParserError):
            mf.decode_msg("not_cbor")

    def test_decode_cbor_fields(self):
        # test missing fields
        mf = fake_factory()
        l = [7,12346.5,[]]
        data=cbor.dumps(l)
        # IndexError
        with self.assertRaises(MessageParserError):
            mf.decode_msg(data)

    def test_decode_filter_func(self):
        msg1 = fake_message()
        filter = lambda msg: False
        mf = fake_factory()
        data = mf.encode_msg(msg1)
        msg2 = mf.decode_msg(data,filter_func=filter)
        self.assertEqual(msg2, None)

    def test_replay_error(self):
        mf = fake_factory()
        # too young
        msg = fake_message()
        target = (msg.timestamp[0] + 60*5, msg.timestamp[1])
        msg.timestamp = target
        data = mf.encode_msg(msg)
        with self.assertRaises(MessageParserError):
            mf.decode_msg(data)
        # too old
        msg.timestamp = messages.build_timestamp()
        target = (msg.timestamp[0] - 60*5, msg.timestamp[1])
        msg.timestamp = target
        data = mf.encode_msg(msg)
        with self.assertRaises(MessageParserError):
            mf.decode_msg(data)

    def test_decode_sanity_check(self):
        mf = fake_factory()
        msg = fake_message()
        # WARNING: Only testing dev_type because alterring source is impossible
        # without rewriting a big chunk of encoding here
        msg.dev_type = "test"
        data = mf.encode_msg(msg)
        with self.assertRaises(MessageParserError):
            mf.decode_msg(data)

    def test_decode_nopayload(self):
        mf = fake_factory()
        msg = fake_message()
        data = mf.encode_msg(msg)
        l=cbor.loads(data)
        l.pop()
        data = cbor.dumps(l)
        with self.assertRaises(MessageParserError):
            mf.decode_msg(data)

    def test_decode_decrypt_error(self):
        mf = fake_factory()
        msg = fake_message()
        data = mf.encode_msg(msg)
        mf.cipher_key = tools.pass2key('bar')
        with self.assertRaises(MessageParserError):
            mf.decode_msg(data)

if __name__ == '__main__':
    unittest.main()
