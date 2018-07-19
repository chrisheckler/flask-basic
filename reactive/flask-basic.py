import os

from pathlib import Path
from subprocess import call

from charms.reactive import (
    when,
    when_not,
    set_flag,
)

from charmhelpers.core.hookenv import log, status_set, unitdata

from charmhelpers.core.hookenv import (
    service_stop,
    service_start,
    service_restart,
)


@when_not('config.git-repo')
def set_broken():
    """Git repo needed"""

    status_set('broken', 'Please include git repo')


@when_not('flask.installed')
def flask_install():
    """Setup virtualenv,dirs,gunicorn,flask"""

    status_set('maintenance', 'Installing Flask')

    # Create app dir
    flask = Path('flask').mkdir()

    # Installing pip,virtualenv,gunicorn,flask
    call(['apt-get', 'install', 'python3-pip'])
    call(['pip', 'install', 'virtualenv'])
    call(['cd', 'flask', 'virtualenv', '-p', 'python3', 'venv'])
    call(['pip', 'install', '-r', 'requirements.txt'])
    call(['cd', 'flask', 'git', 'clone',
          'https://github.com/chrisheckler/flask_apps.git' )
    call(['pip', 'install', 'gunicorn'])
    call(['pip', 'install', 'Flask'])

