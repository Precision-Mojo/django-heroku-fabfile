"""Tasks that deal with deployment."""

from fabric.api import hide, lcd, local, task

import heroku
from settings import PROJECT_ROOT


@task
def deploy_to_heroku():
    """Deploy the site to Heroku."""
    with lcd(PROJECT_ROOT):
        with heroku.maintenance(), hide('running'):
            local("git push heroku")
            local("heroku run python manage.py syncdb --noinput")
            # TODO: Integrate South to support database migration.
            #local("heroku run python manage.py migrate")
