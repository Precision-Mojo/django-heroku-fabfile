"""Tasks that deal with publishing assets and data."""

import os
from fabric.api import hide, lcd, local, task, warn
from django.core.management import call_command

from settings import django_settings, PROJECT_ROOT, STATIC_ROOT

# File that has a list of ignore patterns to pass to collectstatic().
IGNORE_FILE = os.path.join(PROJECT_ROOT, 'static_ignore_patterns.txt')


@task
def update_staticfiles(static_cache='static_cache'):
    """Collect and process static files."""
    with lcd(PROJECT_ROOT), hide('running'):
        local('rm -rf %s' % static_cache)
        collectstatic(interactive=False,
                      ignore_patterns=get_ignore_patterns())
        if os.path.isdir(static_cache):
            local('git add %s' % static_cache)
            local('git commit %s -m "Update the static files cache directory."' % static_cache)
            local('git push origin')


@task
def upload_staticfiles(static_root=STATIC_ROOT, bucket=None):
    """Upload static files to Amazon S3."""
    if bucket is None:
        bucket = getattr(django_settings, 'AWS_STORAGE_BUCKET_NAME',
                         os.environ.get('AWS_STORAGE_BUCKET_NAME'))

        if not bucket:
            warn('The AWS_STORAGE_BUCKET_NAME environment variable is unset or empty. '
                 'Skipping S3 upload.')
            return

    # Use a project-specific .s3cfg if it exists.
    s3cfg = os.path.join(PROJECT_ROOT, '.s3cfg')
    command, config_opt = get_s3cmd_options(s3cfg)

    with lcd(STATIC_ROOT), hide('running'):
        result = local('s3cmd info s3://%s' % bucket, capture=True)

        if not result.succeeded or result.find('does not exist') != -1:
            local('s3cmd mb s3://%s' % bucket)

        local('s3cmd -v %s --acl-public --guess-mime-type %s . s3://%s'
              % (config_opt, command, bucket))


def collectstatic(*args, **options):
    return call_command('collectstatic', *args, **options)


def get_ignore_patterns():
    ignore_patterns = []
    if os.path.exists(IGNORE_FILE):
        for line in open(IGNORE_FILE, 'r').readlines():
            line = line.strip()
            if line and not line.startswith('#'):
                ignore_patterns.append(line)
    return ignore_patterns


def get_s3cmd_options(s3cfg):
    """Determine the command and options to pass to s3cmd."""
    command = 'sync'
    config_opt = ''

    if os.path.exists(s3cfg):
        config_opt = '-c "%s"' % s3cfg

        try:
            from S3.Config import ConfigParser

            config = ConfigParser(s3cfg)
            if config.get('encrypt', default='').tolower() == 'true':
                # If the 'encrypt' option is true, we have to use the put command instead of sync.
                command = 'put --recursive'
        except ImportError:
            pass

    return command, config_opt
