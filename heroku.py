"""Tasks that deal with Heroku."""

import os
from contextlib import contextmanager
from fabric.api import hide, local


def get_config(key, set_environ=True):
    with hide('running'):
        result = local('heroku config:get %s' % key, capture=True).strip()
    if set_environ:
        os.environ[key] = result
    return result


@contextmanager
def maintenance():
    pass
