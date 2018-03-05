import setuptools
import sys

requirements = ['rabbitpy>=0.25.0']
if sys.version_info < (2, 7, 0):
    requirements.append('argparse')

classifiers = ['Development Status :: 3 - Alpha',
               'Environment :: Console',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: BSD License',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: Implementation :: CPython',
               'Programming Language :: Python :: Implementation :: PyPy',
               'Topic :: Communications',
               'Topic :: Internet',
               'Topic :: System']

console_scripts = ['rabbitstew=rabbitstew:main']

desc = 'A command-line tool for publishing messages to RabbitMQ'

setuptools.setup(name='rabbitstew',
                 version='0.1.0',
                 description=desc,
                 long_description=open('README.rst').read(),
                 author='Gavin M. Roy',
                 author_email='gavinr@aweber.com',
                 url='https://github.com/gmr/rabbitstew',
                 py_modules=['rabbitstew'],
                 package_data={'': ['LICENSE', 'README.rst']},
                 include_package_data=True,
                 install_requires=requirements,
                 license=open('LICENSE').read(),
                 classifiers=classifiers,
                 entry_points=dict(console_scripts=console_scripts),
                 zip_safe=True)
