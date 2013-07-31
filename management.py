"""Tasks that deal with project management."""

import os
from fabric.api import hide, lcd, local, puts, settings, task, warn
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.core.management import call_command

from settings import django_settings, IS_WINDOWS, PROJECT_ROOT, SITE_NAME, SITE_ROOT
from utils import msg

vendor_modules = None
has_south = 'south' in django_settings.INSTALLED_APPS


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
        _syncdb(interactive=False)
        _migrate(interactive=False)


@task
def startapp(app, directory=None):
    """Create an app in the SITE_ROOT apps/ directory."""
    if directory is None:
        directory = app

    apps_dir = os.path.join(SITE_ROOT, 'apps')
    target_dir = os.path.join(apps_dir, directory)
    apps_module = os.path.join(apps_dir, '__init__.py')

    puts("Creating application %s...\n" % app)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    if not os.path.exists(apps_module):
        # Touch the __init__.py file under the apps/ directory.
        open(apps_module, 'a').close()

    _startapp(app_name=app, target=target_dir)

    # The app's name was given, but it lives in the apps module so compose the full name.
    app_name = 'apps.' + app

    # Any other configuration tasks require that the app is in INSTALLED_APPS.
    if not app_name in django_settings.INSTALLED_APPS:
        django_settings.INSTALLED_APPS += (app_name,)

    # Prepare South.
    _schemamigration(app=app_name, initial=True)

    puts("\nCreated %s. Add '%s' to settings.INSTALLED_APPS." % (app, app_name))


@task
def update_schema(app):
    """Update the schema of the specified app."""
    if not has_south:
        warn('South was not found in INSTALLED_APPS. Skipping schema update for %s' % app)
        return

    # Automatically generate a schema migration. Run a migration of the app if the schema
    # migration is successful; if there's no work to do the auto migration wil exit, but we absorb
    # any exit (so only the migrate is skipped).
    try:
        _schemamigration(app=app, auto=True)
        _migrate(app=app, interactive=False)
    except SystemExit:
        pass


@task
def test(verbosity=0):
    """Run tests."""
    _test(verbosity=verbosity)


def _syncdb(**options):
    return call_command('syncdb', **options)


def _migrate(*args, **options):
    if has_south:
        return call_command('migrate', *args, **options)


def _schemamigration(*args, **options):
    if has_south:
        return call_command('schemamigration', *args, **options)


def _startapp(*args, **options):
    return call_command('startapp', *args, **options)


def _test(*args, **options):
    return call_command('test', *args, **options)
