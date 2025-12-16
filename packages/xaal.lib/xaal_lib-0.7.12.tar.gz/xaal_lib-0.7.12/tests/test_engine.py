import time
import unittest
from xaal.lib import Engine, Device, MessageType, CallbackError
from xaal.lib import engine, tools
from xaal.lib.messages import Message

TEST_PORT = 6666


def new_engine():
    engine = Engine(port=TEST_PORT)
    return engine

class TestEngine(unittest.TestCase):

    def test_devices(self):
        dev = Device("test.basic", tools.get_random_uuid())
        eng = Engine(port=TEST_PORT)
        eng.add_device(dev)
        self.assertEqual(eng.devices,[dev,])
        eng.remove_device(dev)
        self.assertEqual(eng.devices,[])
        eng.add_devices([dev,])
        self.assertEqual(eng.devices,[dev,])

    def test_start_stop(self):
        eng = Engine(port=TEST_PORT)
        dev = Device("test.basic", tools.get_random_uuid())
        eng.add_device(dev)
        eng.start()
        eng.start()  # second start
        self.assertEqual(engine.EngineState.started, eng.state)
        eng.loop()
        eng.stop()
        self.assertEqual(engine.EngineState.halted, eng.state)

    def test_timer(self):
        eng = Engine(port=TEST_PORT)
        t0 = time.time()
        def _exit():
            eng.shutdown()
        eng.add_timer(_exit, 1, 1)
        eng.run()
        t = time.time() - t0
        self.assertTrue(t > 1)
        self.assertTrue(t < 2)

    def test_timer_error(self):
        eng = Engine(port=TEST_PORT)
        eng.start()
        def _error():
            raise CallbackError(500,"test error")
        eng.add_timer(_error,0,1)
        eng.loop()  
        eng.stop()
        self.assertEqual(engine.EngineState.halted, eng.state)

    def test_run_action(self):
        target = Device("test.basic", tools.get_random_uuid())

        def action_1():
            return {"value":"action_1"}

        def action_2(_value=None):
            return {"value":"action_%s" % _value}

        def action_3():
            raise Exception

        target.add_method("action_1", action_1)
        target.add_method("action_2", action_2)
        target.add_method("action_3", action_3)

        msg = Message()
        msg.msg_type = MessageType.REQUEST
        msg.targets = [target.address]
        # simple test method
        msg.action = "action_1"
        result = engine.run_action(msg, target)
        self.assertEqual(result, {"value":"action_1"})
        # test with value
        msg.action = "action_2"
        msg.body = {"value": "2"}
        result = engine.run_action(msg, target)
        self.assertEqual(result, {"value":"action_2"})
        # Exception in method
        msg.action = "action_3"
        with self.assertRaises(engine.XAALError):
            result = engine.run_action(msg, target)
        # unknown method
        msg.action = "missing"
        with self.assertRaises(engine.XAALError):
            result = engine.run_action(msg, target)


if __name__ == "__main__":
    unittest.main()
