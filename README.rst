rabbitstew
==========
A small command-line tool that adheres to the Unix philospohy for publishing
messages to RabbitMQ.

Usage Example
-------------

.. code:: bash

    cat /var/log/messages | rabbitstew -H rabbit-server -r syslog.messages

CLI Options
-----------

.. code::

    usage: rabbitstew [-h] [-H HOST] [-p PORT] [-s] [-v VHOST] [-u USER]
                      [-P PASSWORD] [-W] [-e EXCHANGE] [-r ROUTING_KEY] [-c]
                      [--add-user] [--app-id APP_ID] [--auto-id]
                      [--content-type VALUE] [--type TYPE] [-V] [--version]

    RabbitMQ message publisher

    optional arguments:
      -h, --help            show this help message and exit
      -H HOST               Server hostname (default: localhost)
      -p PORT               Server port (default: 5672)
      -s                    Use SSL to connect (default: False)
      -v VHOST              Server virtual host (default: /)
      -u USER               Server username (default: guest)
      -P PASSWORD           Server password (default: guest)
      -W                    Prompt for password (default: False)
      -f PATH               Read password from a file (default: None)
      -e EXCHANGE           Exchange to publish to (default: None)
      -r ROUTING_KEY        Routing Key to use (default: None)
      -c                    Confirm delivery of each message, exiting if a message
                            delivery could not be confirmed (default: False)
      --add-user            Include the user in the message properties (default: False)
      --app-id APP_ID       Specify the app-id property of the message (default: rabbitstew)
      --auto-id             Create a unique message ID for each message (default: False)
      --content-type VALUE  Specify the content type of the message (default: None)
      --type TYPE           Specify the message type (default: None)
      -V                    Verbose output (default: False)
      --version             show program's version number and exit


Version History
---------------

 - 0.1.0 - released *2015-02-02*
  - Initial Release

.. |Version| image:: https://badge.fury.io/py/rabbitstew.svg?
   :target: http://badge.fury.io/py/rabbitstew

.. |Status| image:: https://travis-ci.org/AWeber/rabbitstew.svg?branch=master
   :target: https://travis-ci.org/AWeber/rabbitstew

.. |Coverage| image:: https://codecov.io/github/AWeber/rabbitstew/coverage.svg?branch=master
   :target: https://codecov.io/github/AWeber/rabbitstew?branch=master

.. |Downloads| image:: https://pypip.in/d/rabbitstew/badge.svg?
   :target: https://pypi.python.org/pypi/rabbitstew

.. |License| image:: https://pypip.in/license/rabbitstew/badge.svg?
   :target: https://rabbitstew.readthedocs.org
