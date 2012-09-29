django-heroku-fabfile
=====================

Introduction
------------

This repository houses a [Fabric][f_src] "fabfile" used at [Precision
Mojo][p_src] to build, manage, and deploy [Django][d_src]-based projects to
[Heroku][h_src].

  [f_src]: http://fabfile.org
  [p_src]: http://www.precision-mojo.com
  [d_src]: https://www.djangoproject.com/
  [h_src]: https://www.heroku.com/

The fabfile is a work-in-progress, it can and will change according to the
needs of the projects we develop at Precision Mojo. Please fork, improve,
suggest, or berate us as necessary.

Installation
------------

To use the fabfile you must first install Fabric. This easiest way to do this is to run:

    $ pip install Fabric

The fabfile is intended to be dropped into an existing project as a git
submodule. To install it as a submodule, run the following commands:

    <from the root of your repository>
    $ git submodule add git://github.com/Precision-Mojo/django-heroku-fabfile.git fabfile
    $ git submodule init
    $ git commit -m "Clone django-heroku-fabfile as a submodule."

To view a list of available tasks type `fab -l`.

Maintenance
-----------

To update to the latest version of the fabfile, run the following commands:

    <from the root of your repository>
    $ cd fabfile
    $ git fetch
    $ git checkout master
    $ git merge origin master
    $ cd ..
    $ git commit -m "Update to the latest version of django-heroku-fabfile." fabfile

To remove the submodule from your repository, run the following commands:

    <from the root of your repository>
    $ git config -f .gitmodules --remove-section submodule.fabric
    $ git config -f .git/config --remove-section submodule.fabric
    $ git rm --cached fabfile
    $ git commit -m "Remove the django-heroku-fabfile submodule." .gitmodules fabfile

Fabric Tasks
------------

TODO
