

import xaal.lib
from xaal.lib import tools


import logging


ADDR='b8bec7ca-f955-11e6-9031-82ed25e6aaaa'
ADDR=tools.get_random_uuid()

def dump_hex(name,data):
    print("%s : " % name,end='=')
    for k in data:
        if type(k) == int:
            print("%x"%k,end=' ')
        else:
            print("%x"%ord(k),end=' ')
    print()

def test_pysodium():
    from xaal.lib import messages
    import pysodium

    payload = 'FooBar'.encode("utf-8")
    ad = '[]'

    data  = messages.build_timestamp()
    nonce = messages.build_nonce(data)
    key = tools.pass2key("My Friend Goo")

    dump_hex('Payload',payload)
    dump_hex('Key',key)

    ciph  = pysodium.crypto_aead_chacha20poly1305_encrypt(payload, ad, nonce, key)
    dump_hex('Ciph',ciph)

    pjson = pysodium.crypto_aead_chacha20poly1305_decrypt(ciph, ad, nonce, key)
    print(pjson)


def test_device():
    from xaal.lib.devices import Device
    addr = ADDR
    dev = Device("foo.basic",addr)
    dev.vendor_id = 'ACME'
    dev.url="http://acmefactory.blogspot.fr/"
    dev.hw_id = '0x201'
    print(dev.getDescription())
    return dev

def test_msg():
    from xaal.lib.messages import Message
    msg = Message()
    addr = ADDR
    msg.targets = [addr,]
    msg.dump()

def test_encode():
    from xaal.lib.messages import MessageFactory
    key = tools.pass2key('FooBar')
    factory = MessageFactory(key)
    m2 = factory.build_msg()
    print(factory.decode_msg(m2))

def test_log():
    logger = logging.getLogger(__name__)
    logger.info("This is an INFO msg")
    logger.debug("This is an DEBUG msg")


def test_engine():
    from xaal.lib.engine import Engine
    engine = Engine()
    engine.run()

def test_alive():
    addr = ADDR
    dev = xaal.lib.Device("test.basic",addr)
    eng = xaal.lib.Engine()
    eng.add_devices([dev,])
    eng.run()

def test_crypto_decoding_error():
    addr = ADDR
    dev = xaal.lib.Device("test.basic",addr)
    eng = xaal.lib.Engine()
    eng.add_devices([dev,])
    eng.msg_factory.cipher_key = tools.pass2key('FakeKey')
    eng.start()
    eng.loop()


def test_attr():
    dev = xaal.lib.Device("test.basic",ADDR)
    dev.url = "http://linux.org"
    dev.vendor_id = 'ACME'
    dev.product_id = "Full Fake Device"
    dev.info = 'FooBar'
    dev.hw_id = 'ffd0001'
    #dev.alive_period = 100

    attr0 = dev.new_attribute('attr0',10)
    attr1 = dev.new_attribute('attr1',False)

    eng = xaal.lib.Engine()
    eng.add_devices([dev,])

    def update():
        attr0.value = attr0.value + 1

    eng.add_timer(update,60)

    #eng.loop()
    eng.run()



def run():

    logger = tools.get_logger(__name__,logging.DEBUG,"%s.log" % __name__)
    #test_pysodium()
    #test_device()
    #test_msg()
    #test_encode()
    #test_log()
    #test_alive()
    #test_crypto_decoding_error()
    test_attr()



if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print("Bye bye...")
