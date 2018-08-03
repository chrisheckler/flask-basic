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
from charmhelpers.core.hookenv import (
    log,
    status_set,
    config,
    charm_dir,
    open_port
)
from charmhelpers.core.host import (
    service_stop,
    service_start,
    service_restart,
    service_running,
)

FLASK_APP = Path('/srv/flask_app')
PIP = Path('/usr/bin/pip3')
FLASK_APP_DEPS = Path(FLASK_APP / 'bucketlist' / 'requirements.txt')

@when_not('config.set.git-repo')
def set_blocked():
    """git repo needed"""

    status_set('blocked', "please set 'git-repo' in the charm config")


@when_not('flask.app.installed')
@when('apt.installed.python3-pip')
def flask_app_install():
    """setup virtualenv,dirs,gunicorn,flask"""
    conf = config()

    status_set('maintenance', 'installing flask app from github')
    if FLASK_APP.exists():
        call(['rm', '-rf', str(FLASK_APP)])
    call(['git', 'clone', conf.get('git-repo'), str(FLASK_APP)])
    call([str(PIP), 'install', '-r', str(FLASK_APP_DEPS)])
    call([str(PIP), 'install', 'gunicorn'])

    log('flask installed and git project cloned')
    status_set('active', 'Flask app and deps installed')
    set_flag('flask.app.installed')


@when('flask.app.installed')
@when_not('flask.app.running')
def systemd_service_start():
    """Establish systemd and run gunicorn"""

    render('flask.service.tmpl', '/etc/systemd/system/flask.service', context={})

    call(['systemctl', 'flask'])
    call(['systemctl', 'enable', 'flask.service'])

    if not service_running('flask'):
        service_start('flask')
    else:
        service_restart('flask')

    open_port(5000)

    log('gunicorn configured')
    set_flag('flask.app.running')


@when('flask.app.running')
def set_avail_status():
    status_set('active', 'Flask application available')


@when('pgsql.connected')
@when_not('flask.pgsql.requested')
def request_database():
    """When connection established to postgres,
       request databse.
    """

    status_set('maintenance', 'Requesting PostgreSQL database')

    pgsql = endpoint('pgsql.connected')
    pgsql.set_database('flask')

    log('Database Available')
    status_set('active', 'pgsql.requested')
    set_flag('flask.pgsql.requested')

