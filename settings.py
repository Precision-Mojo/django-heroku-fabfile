"""Settings used throughout the fabfile."""

import os
from fabric.api import abort, cd
from fabric.contrib import django

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


# TODO: Default to development, but provide a task that initializes the
# production environment.
PROJECT_ENVIRONMENT = 'development'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = _find_site_root(PROJECT_ROOT)

if SITE_ROOT is None:
    abort("Couldn't find site root in project root '%s'!" % PROJECT_ROOT)

SITE_NAME = os.path.basename(SITE_ROOT)

with cd(PROJECT_ROOT):
    settings_module = '%s.settings.%s' % (SITE_NAME, PROJECT_ENVIRONMENT)
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', settings_module)
    try:
        from django.conf import settings as django_settings
        django.settings_module(settings_module)
        STATIC_ROOT = django_settings.STATIC_ROOT
    except:
        abort("Couldn't load project settings module '%s'!" % settings_module)
