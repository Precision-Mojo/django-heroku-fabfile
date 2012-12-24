"""Tasks that deal with deployment."""

from fabric.api import abort, hide, lcd, local, puts, task

import heroku
from settings import PROJECT_ROOT
from utils import get_tag_names, is_working_directory_clean, need_to_tag


@task
def prepare_to_deploy(skip_clean_check=False):
    """Prepare the project's working copy for deployment."""
    with lcd(PROJECT_ROOT), hide('commands'):
        if not skip_clean_check and not is_working_directory_clean():
            abort("Working directory must be clean before deployment.")
        local('git pull')


@task
def tag_project(prefix):
    """Tag the project for the specified environment."""
    if prefix is None:
        abort('Tag prefix must be specified!')

    with lcd(PROJECT_ROOT), hide('commands'):
        (last_tag_name, next_tag_name) = get_tag_names(prefix)

        puts('Last tag: %s' % last_tag_name)
        puts('Next tag: %s' % next_tag_name)

        if not need_to_tag("HEAD", last_tag_name):
            puts("Current tag '%s' is the most recent version." % last_tag_name)
            return

        puts("Tagging project with '%s'." % next_tag_name)
        local('git tag -a -m "Tag latest for %s." %s' % (prefix, next_tag_name))
        local('git push origin %s' % next_tag_name)


@task
def deploy_to_heroku():
    """Deploy the site to Heroku."""
    with lcd(PROJECT_ROOT):
        with heroku.maintenance(), hide('running'):
            local("git push heroku")
            local("heroku run fab management.syncdb")
