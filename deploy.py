"""Tasks that deal with deployment."""

from fabric.api import abort, hide, lcd, local, task

import heroku
from settings import PROJECT_ENVIRONMENT, PROJECT_ROOT
from utils import get_tag_names, is_working_directory_clean, msg, need_to_tag


@task
def prepare_to_deploy():
    """Prepare the project's working copy for deployment."""
    with lcd(PROJECT_ROOT), hide('commands'):
        if not is_working_directory_clean():
            abort("Working directory must be clean before deployment.")
        local('git pull')


@task
def tag_project(prefix):
    """Tag the project for the specified environment."""
    if prefix is None:
        abort('Tag prefix must be specified!')

    (last_tag_name, next_tag_name) = get_tag_names(prefix)

    print('Last tag: %s' % last_tag_name)
    print('Next tag: %s' % next_tag_name)

    if not need_to_tag("HEAD", last_tag_name):
        print("Current tag '%s' is the most recent version." % last_tag_name)
        return

    with msg("Tagging %s with '%s'" % (PROJECT_ENVIRONMENT, next_tag_name)):
        local("git tag -a -m 'Tag latest for %s.' %s" % (PROJECT_ENVIRONMENT, next_tag_name))


@task
def deploy_to_heroku():
    """Deploy the site to Heroku."""
    with lcd(PROJECT_ROOT):
        with heroku.maintenance(), hide('running'):
            local("git push heroku")
            local("heroku run python manage.py syncdb --noinput")
            # TODO: Integrate South to support database migration.
            #local("heroku run python manage.py migrate")
