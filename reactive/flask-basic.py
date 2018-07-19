import os
from subprocess import call

from charms.reactive import (
    when,
    when_not,
    set_flag,
)

from charmhelpers.core.hookenv import log, status_set

from charmhelpers.core.hookenv import (
    service_stop,
    service_start,
    service_restart,
)


@when_not('config.git-repo')
def set_broken():
    status_set('broken', 'Please include git repo')
