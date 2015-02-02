import mock
import subprocess
import sys
import tempfile
import time
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import uuid

import rabbitpy
import rabbitstew


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
        self.input = b'\n'.join(self.INPUT) + b'\n'

    def _eval_message(self, start_time, iteration, msg):
        if not msg:
            assert False, 'Message not retrieved from queue'
        self.assertEqual(msg.body, self.INPUT[iteration])
        self.assertEqual(msg.properties['app_id'], b'rabbitstew')
        self.assertAlmostEqual(self.get_epoch(msg.properties['timestamp']),
                               start_time)

    def get_command(self):
        return ['python', 'rabbitstew.py', '-r', self.queue.name]

    def get_epoch(self, value):
        return float(int(value.strftime('%s')) / 100)

    def test_publishing_messages(self):
        start_time = float(int(time.time()) / 100)
        process = subprocess.Popen(self.get_command(), stdin=subprocess.PIPE)
        process.communicate(input=self.input)
        process.wait()
        self.assertEqual(0, process.returncode)
        for iteration in range(0, len(self.INPUT)):
            self._eval_message(start_time, iteration, self.queue.get(False))


class TestConfirmedPublishing(TestBasicPublishing):

    def _get_command(self):
        return ['python', 'rabbitstew.py', '-c', '-r', self.queue.name]


class TestPublishingWithProperties(TestBasicPublishing):

    def get_command(self):
        return ['python', 'rabbitstew.py', '-r', self.queue.name, '--auto-id',
                '--app-id', 'test', '--content-type', 'text/plain', '--type',
                'test', '--add-user']

    def _eval_message(self, start_time, iteration, msg):
        if not msg:
            assert False, 'Message not retrieved from queue'
        self.assertEqual(msg.body, self.INPUT[iteration])
        self.assertEqual(msg.properties['app_id'], b'test')
        self.assertEqual(msg.properties['content_type'], b'text/plain')
        self.assertIsNotNone(msg.properties['message_id'])
        self.assertEqual(msg.properties['message_type'], b'test')
        self.assertAlmostEqual(self.get_epoch(msg.properties['timestamp']),
                               start_time)
        self.assertEqual(msg.properties['user_id'], b'guest')


class TestURLCreation(unittest.TestCase):

    def test_default_values(self):
        sys.argv = ['rabbitstew']
        obj = rabbitstew.RabbitStew()
        self.assertEqual(obj.url, 'amqp://guest:guest@localhost:5672/%2F')

    def test_url_values(self):
        sys.argv = ['rabbitstew', '-H', 'test-rabbit', '-p', '5673', '-v',
                    'test', '-u', 'python', '-P', 'pass', '-s']
        obj = rabbitstew.RabbitStew()
        self.assertEqual(obj.url, 'amqps://python:pass@test-rabbit:5673/test')

    def test_password_file(self):
        pwd = str(uuid.uuid4())
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(pwd.encode('ascii') + b'\n')
        tmp.flush()
        tmp.seek(0)
        sys.argv = ['rabbitstew', '-u', 'test', '-f', tmp.name]
        obj = rabbitstew.RabbitStew()
        url = b''.join([b'amqp://test:', pwd.encode('ascii'),
                        b'@localhost:5672/%2F'])
        self.assertEqual(obj.url.encode('ascii'), url)

    def test_getpass_option(self):
        pwd = str(uuid.uuid4())
        sys.argv = ['rabbitstew', '-u', 'test', '-W']
        with mock.patch('getpass.getpass') as getpass:
            getpass.return_value = pwd
            obj = rabbitstew.RabbitStew()
            url = b''.join([b'amqp://test:', pwd.encode('ascii'),
                            b'@localhost:5672/%2F'])
            self.assertEqual(obj.url.encode('ascii'), url)
