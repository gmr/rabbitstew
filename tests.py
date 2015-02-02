import io
import subprocess
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import rabbitpy


class TestBasicPublishing(unittest.TestCase):

    INPUT = [b'CODE SIGNING: cs_invalid_page(0x10fa17000): p=85310[python]',
             b'CODE SIGNING: cs_invalid_page(0x1061ca000): p=85314[python]']

    def setUp(self):
        self.connection = rabbitpy.Connection()
        self.channel = self.connection.channel()
        self.queue = rabbitpy.Queue(self.channel,
                                    exclusive=True,
                                    auto_delete=True)
        self.queue.declare()

    def test_publishing_messages(self):
        cmd = ['python', 'rabbitstew.py', '-r', self.queue.name]
        input = b'\n'.join(self.INPUT) + b'\n'
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        process.communicate(input=input)
        process.wait()
        self.assertEqual(0, process.returncode)
        msg = self.queue.get(False)
        if not msg:
            assert False, 'Message not retrieved from queue'
        self.assertEqual(msg.body, self.INPUT[0])
        msg = self.queue.get(False)
        if not msg:
            assert False, 'Message not retrieved from queue'
        self.assertEqual(msg.body, self.INPUT[1])
