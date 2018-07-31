import os

from pathlib import Path
from subprocess import call

from charms.reactive import (
    when,
    when_not,
    set_flag,
)
from charmhelpers.core.templating import render
from charmhelpers.core import unitdata
from charmhelpers.core.hookenv import log, status_set, config, charm_dir, open_port
from charmhelpers.core.host import (
    service_stop,
    service_start,
    service_restart,
    service_running,
)
FLASK_APP = Path('/srv/flask_app')

config = config()

@when_not('config.set.git-repo')
def set_blocked():
    """git repo needed"""

    status_set('blocked', "please set 'git-repo' in the charm config")


@when_not('flask.installed')
def flask_install():
    """setup virtualenv,dirs,gunicorn,flask"""

    status_set('maintenance', 'installing flask')

    call(['git', 'clone', config.get('git-repo'), '/home/ubuntu/flask'])
    call(['apt-get', 'install', 'python3-pip'])
    call(['pip3', 'install', 'virtualenv'])
    call(['virtualenv','-p', '/usr/bin/python3.6', '/home/ubuntu/flask/.venv'])
    call(['/home/ubuntu/flask/.venv/bin/pip3', 'install', 'flask'])
    call(['/home/ubuntu/flask/.venv/bin/pip3', 'install', 'gunicorn'])

    log('flask installed and git project cloned')
    status_set('active', 'flask installed')
    set_flag('flask.installed')


@when_not('gunicorn.config')
@when('flask.installed',
      'config.set.git-repo')
def gunicorn_run():
    """Configure Gunicorn"""

    status_set('maintenance', 'setting up gunicorn')

    render('gunicorn.tmpl', '/etc/systemd/system/meflask.service', context={})
    call(['systemctl', 'meflask'])
    call(['systemctl', 'enable', 'meflask.service'])

    service_start('meflask')
    open_port(5000)

    log('gunicorn configured')
    status_set('active', 'gunicorn is configured')
    set_flag('gunicorn.config')

