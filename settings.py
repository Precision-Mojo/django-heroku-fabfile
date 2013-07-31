"""Settings used throughout the fabfile."""

import os
import platform
from fabric.api import abort, cd, env
from fabric.contrib import django

IS_WINDOWS = platform.system() == 'Windows'

_fabfile_root = os.path.dirname(os.path.abspath(__file__))


def _find_site_root(project_root):
    for entry in os.listdir(project_root):
        site_root = os.path.join(project_root, entry)
        if _fabfile_root != site_root and os.path.isdir(site_root):
            for site_entry in os.listdir(site_root):
                site_entry_path = os.path.join(site_root, site_entry)
                if site_entry == 'settings' and os.path.isdir(site_entry_path):
                    if os.path.exists(os.path.join(site_entry_path, '__init__.py')):
                        return site_root
                elif site_entry == 'settings.py':
                    return site_root
    return None


def _module_to_filename(module_name):
    items = module_name.split('.')
    return os.path.join(*items) + '.py'


def _get_test_settings_module(project_root, site_name):
    settings_module = None

    if 'test' in "\n".join(env.tasks):
        test_settings = '%s.settings.test' % site_name
        if os.path.exists(os.path.join(project_root, _module_to_filename(test_settings))):
            settings_module = test_settings

    return settings_module


# TODO: Default to development, but provide a task that initializes the
# production environment.
PROJECT_ENVIRONMENT = 'development'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = _find_site_root(PROJECT_ROOT)

if SITE_ROOT is None:
    abort("Couldn't find site root in project root '%s'!" % PROJECT_ROOT)

SITE_NAME = os.path.basename(SITE_ROOT)

with cd(PROJECT_ROOT):
    # Locate the settings module in use.
    settings_module = _get_test_settings_module(PROJECT_ROOT, SITE_NAME)

    if not settings_module:
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '%s.settings' % SITE_NAME)

    if not os.path.exists(os.path.join(PROJECT_ROOT, _module_to_filename(settings_module))):
        settings_module = '%s.settings.%s' % (SITE_NAME, PROJECT_ENVIRONMENT)

    try:
        from django.conf import settings as django_settings
        django.settings_module(settings_module)
        STATIC_ROOT = django_settings.STATIC_ROOT
    except:
        abort("Couldn't load project settings module '%s'!" % settings_module)
