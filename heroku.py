"""Tasks that deal with Heroku."""

import os
from contextlib import contextmanager
from fabric.api import hide, lcd, local, settings, task

from settings import PROJECT_ROOT
from utils import lines_in_file

ADDONS_FILENAME = 'heroku-addons.txt'


@task
def install_addons(addons_filename=ADDONS_FILENAME, ignored_addons=None):
    """Install Heroku addons listed in the specified file."""
    if ignored_addons is None:
        ignored_addons = []
    with lcd(PROJECT_ROOT), hide('running'):
        for addon in lines_in_file(addons_filename, skip_prefixes=('#', '=')):
            # There might be addon-specific parameters after the addon name.
            addon = addon.split()[0]
            if not addon in ignored_addons:
                with settings(warn_only=True):
                    local('heroku addons:add %s' % addon)


@task
def sync_addons(addons_filename=ADDONS_FILENAME):
    """Sync installed Heroku addons with the specified file."""
    addons = get_addons()
    install_addons(addons_filename, ignored_addons=addons)


def get_addons():
    addons = []
    with lcd(PROJECT_ROOT), hide('commands'):
        result = local('heroku addons', capture=True)
        if result.succeeded and result.find('has no add-ons') == -1:
            for addon in result.split('\n'):
                # Remove any addon-specific parameters and trailing whitespace.
                addon = addon.split()[0]
                if not addon.startswith('='):
                    addons.append(addon)
    return addons


def get_config(key, set_environ=True):
    with hide('running'):
        result = local('heroku config:get %s' % key, capture=True).strip()
    if set_environ:
        os.environ[key] = result
    return result


@contextmanager
def maintenance():
    with hide('running'):
        local('heroku maintenance:on')
    try:
        yield
    finally:
        with hide('running'):
            # Always take the app out of maintenance mode.
            local('heroku maintenance:off')
