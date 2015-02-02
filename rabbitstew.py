"""
Rabbit Stew
===========

A CLI application for piping delimited input to RabbitMQ as messages.

Example Use
-----------

.. code:: bash

    cat /var/log/messages | rabbitstew -H rabbit-server -r syslog.messages

"""
import argparse
import copy
import getpass
import sys
import time
try:
    import urllib.parse as urllib
except ImportError:
    import urllib

import rabbitpy
from rabbitpy import exceptions

__version__ = '0.1.0'

DESC = "RabbitMQ message publisher"

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5672
DEFAULT_VHOST = '/'
DEFAULT_USER = 'guest'
DEFAULT_PASSWORD = 'guest'


class RabbitStew(object):

    def __init__(self):
        self.channel = None
        self.connection = None
        self.counter = 0
        self.properties = {}

        self.parser = self.build_argparser()
        self.args = self.parser.parse_args()
        self.password = self.get_password()

    def build_argparser(self):
        formatter = argparse.ArgumentDefaultsHelpFormatter
        parser = argparse.ArgumentParser(prog='rabbitstew',
                                         description=DESC,
                                         formatter_class=formatter)

        parser.add_argument('-H',
                            dest='host',
                            help='Server hostname',
                            default=DEFAULT_HOST)
        parser.add_argument('-p',
                            dest='port',
                            type=int,
                            help='Server port',
                            default=DEFAULT_PORT)
        parser.add_argument('-s',
                            dest='ssl',
                            action='store_true',
                            help='Use SSL to connect')
        parser.add_argument('-v',
                            dest='vhost',
                            help='Server virtual host',
                            default=DEFAULT_VHOST)
        parser.add_argument('-u',
                            dest='user',
                            help='Server username',
                            default=DEFAULT_USER)
        parser.add_argument('-P',
                            dest='password',
                            help='Server password',
                            default=DEFAULT_PASSWORD)
        parser.add_argument('-W',
                            dest='prompt',
                            action='store_true',
                            help='Prompt for password')
        parser.add_argument('-f',
                            dest='password_file',
                            metavar='PATH',
                            help='Read password from a file')

        parser.add_argument('-e',
                            dest='exchange',
                            help='Exchange to publish to')
        parser.add_argument('-r',
                            dest='routing_key',
                            help='Routing Key to use')

        parser.add_argument('-c',
                            dest='confirm',
                            action='store_true',
                            help='Confirm delivery of each message, exiting if '
                                 'a message delivery could not be confirmed')

        parser.add_argument('--add-user',
                            action='store_true',
                            help='Include the user in the message properties')
        parser.add_argument('--app-id',
                            help='Specify the app-id property of the message',
                            default='rabbitstew')
        parser.add_argument('--auto-id',
                            action='store_true',
                            help='Create a unique message ID for each message')
        parser.add_argument('--content-type',
                            metavar='VALUE',
                            help='Specify the content type of the message')
        parser.add_argument('--type',
                            help='Specify the message type')

        parser.add_argument('-V',
                            dest='verbose',
                            help='Verbose output',
                            action='store_true')
        parser.add_argument('--version',
                            action='version',
                            version='%(prog)s ' + __version__)
        return parser

    def close(self):
        self.connection.close()
        self.log('Closed RabbitMQ connection')

    def connect(self):
        self.log('Connecting to RabbitMQ')

        try:
            self.connection = rabbitpy.Connection(self.url)
        except (exceptions.ConnectionException,
                exceptions.AMQPAccessRefused) as err:
            self.error('Connection error: {0}'.format(str(err)))

        self.channel = self.connection.channel()

        if self.args.confirm:
            self.channel.enable_publisher_confirms()
            self.log('Publisher confirmation enabled')

        self.log('Connected')

    def default_properties(self):
        properties = {'app_id': self.args.app_id}
        if self.args.content_type:
            properties['content_type'] = self.args.content_type
        if self.args.type:
            properties['message_type'] = self.args.type
        if self.args.add_user:
            properties['user_id'] = self.args.user
        return properties

    @staticmethod
    def error(message, *args):
        sys.stderr.write(message % args + '\n')
        sys.exit(1)

    def get_password(self):
        if self.args.prompt:
            return getpass.getpass('RabbitMQ password: ')
        if self.args.password_file:
            return open(self.args.password_file, 'r').read().strip()
        return self.args.password

    def get_properties(self):
        properties = copy.copy(self.properties)
        properties['timestamp'] = int(time.time())
        return properties

    def log(self, message, *args):
        if self.args.verbose:
            sys.stdout.write(message % args + '\n')

    def publish(self, line):
        msg = rabbitpy.Message(self.channel,
                               line.rstrip('\r\n'),
                               self.get_properties(),
                               opinionated=self.args.auto_id)
        if self.args.confirm:
            try:
                if not msg.publish(self.args.exchange, self.args.routing_key):
                    self.error('Could not confirm delivery of last message')
            except exceptions.AMQPNotFound as error:
                self.error('Error publishing message: %s', error.message)
        else:
            msg.publish(self.args.exchange, self.args.routing_key)
        self.counter += 1
        self.log('Message #{0} published'.format(self.counter))

    def run(self):
        self.connect()

        # Is better to show argparser default as None and replace with ''
        if not self.args.exchange:
            self.args.exchange = ''

        if not self.args.routing_key:
            self.args.routing_key = ''

        # Dict that will get copied for each message
        self.properties = self.default_properties()

        # Iterate through stdin and publish the message
        for line in sys.stdin:
            self.publish(line)

        self.close()
        self.log('Published {0} messages'.format(self.counter))

    @property
    def url(self):
        """Return the AMQP URI from the parameters

        :return str: The PostgreSQL connection URI

        """
        scheme = 'amqps' if self.args.ssl else 'amqp'
        virtual_host = urllib.quote(self.args.vhost, '')
        return '{0}://{1}:{2}@{3}:{4}/{5}'.format(scheme,
                                                  self.args.user,
                                                  self.password,
                                                  self.args.host,
                                                  self.args.port,
                                                  virtual_host)


def main():
    stew = RabbitStew()
    stew.run()


if __name__ == '__main__':
    main()
