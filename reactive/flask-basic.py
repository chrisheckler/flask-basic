import os

from pathlib import Path
from subprocess import call, Popen

from charms.reactive import (
    when,
    when_not,
    set_flag,
)

from charmhelpers.core import unitdata
from charmhelpers.core.hookenv import log, status_set, config
from charmhelpers.core.host import (
    service_stop,
    service_start,
    service_restart,
)

config = config()


@when_not('config.set.git-repo')
def set_blocked():
    """Git repo needed"""

    status_set('blocked', 'Please include git repo')


@when_not('flask.installed')
def flask_install():
    """Setup virtualenv,dirs,gunicorn,flask"""

    status_set('maintenance', 'Installing Flask')

    call(['git', 'clone', config.get('git-repo'), '/home/ubuntu/flask'])
    call(['apt-get', 'install', 'python3-pip'])
    call(['pip3', 'install', 'virtualenv'])
    call(['virtualenv','-p', '/usr/bin/python3.6', '/home/ubuntu/flask/.venv'])
    call(['/home/ubuntu/flask/.venv/bin/pip3', 'install', 'Flask'])
    call(['/home/ubuntu/flask/.venv/bin/pip3', 'install', 'gunicorn'])

    log('Flask Installed and Git project cloned')
    status_set('active', 'flask installed')
    set_flag('flask.installed')


