"""Django project fabfile."""

import os
from fabric.api import puts, task
from fabric.utils import indent

from deploy import deploy_to_heroku, prepare_to_deploy, tag_project
from management import update_vendors, runserver, startapp, syncdb, test, update_schema
from publish import update_staticfiles, upload_staticfiles
from settings import PROJECT_ENVIRONMENT, PROJECT_ROOT, SITE_NAME, STATIC_ROOT


@task(default=True)
def info():
    """Display information about the project configuration."""
    puts("Django project for site '%s' located at '%s':" % (SITE_NAME, PROJECT_ROOT))
    puts(indent('PROJECT_ENVIRONMENT = %s' % PROJECT_ENVIRONMENT, 4))
    puts(indent('DJANGO_SETTINGS_MODULE = %s'
         % os.environ.get('DJANGO_SETTINGS_MODULE', ''), 4))
    puts(indent('STATIC_ROOT = %s' % STATIC_ROOT, 4))


@task
def publish():
    """Publish assets to Amazon S3."""
    update_staticfiles()
    upload_staticfiles()


@task
def deploy(skip_publish=False, skip_clean_check=False):
    """Publish and deploy the site."""
    prepare_to_deploy(skip_clean_check=skip_clean_check)
    syncdb()

    if not STATIC_ROOT:
        skip_publish = True
    if not skip_publish:
        publish()

    # TODO: Add support for other environments.
    tag_project('production')
    deploy_to_heroku()
