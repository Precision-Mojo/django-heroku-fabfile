"""Tasks that deal with project management."""

import os
from fabric.api import hide, lcd, local, settings, task
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from settings import django_settings, IS_WINDOWS, PROJECT_ROOT
from utils import msg

vendor_modules = None


@task
def update_vendors():
    """Update vendor modules."""
    for module in get_vendor_modules():
        submodules = getattr(module, 'submodules')
        if submodules is not None:
            vendor_root = os.path.dirname(module.__file__)
            for name, params in submodules.iteritems():
                vendor_path = os.path.join(vendor_root, name)
                if os.path.isdir(vendor_path):
                    tag = params.get('tag', '')
                    with lcd(vendor_path), msg("Updating vendor submodule %s" % name):
                        local('git checkout %s' % tag)
                        sources = params.get('sources', [])
                        destination = params.get('destination')
                        if destination is not None:
                            destination = \
                                os.path.normpath(os.path.join(vendor_root, destination))
                            with settings(warn_only=True):
                                local('mkdir -p %s' % destination)
                            for source in sources:
                                local('cp -R %s %s' % (source, destination))


def get_vendor_modules():
    global vendor_modules
    if not vendor_modules:
        vendor_modules = []
        for app in django_settings.INSTALLED_APPS:
            module = import_module(app)
            try:
                vendor_module = import_module('%s.vendor' % app)
                vendor_modules.append(vendor_module)
            except:
                if module_has_submodule(module, 'vendor'):
                    raise
    return vendor_modules


@task
def runserver():
    """Run a local development server."""
    # If executing on Windows, prefix with "start" to invoke python in a detached window.
    start_prefix = ''
    if IS_WINDOWS:
        start_prefix = 'start '

    with lcd(PROJECT_ROOT), hide('running'):
        local('%spython manage.py runserver' % start_prefix)


@task
def syncdb():
    """Synchronize database tables and run migrations for all installed apps."""
    with lcd(PROJECT_ROOT), hide('running'):
        local('python manage.py syncdb --noinput')
        local('python manage.py migrate --noinput')
