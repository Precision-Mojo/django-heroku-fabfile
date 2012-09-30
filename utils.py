"""Utilities used by the fabfile."""

import datetime
import re
import os
from contextlib import contextmanager
from fabric.api import hide, local, puts


@contextmanager
def msg(txt):
    puts(txt + '...', end='', flush=True)
    with hide('everything'):
        yield
    puts('done.', show_prefix=False, flush=True)


# Tagging/git routines based off of https://gist.github.com/663181.


def get_last_tag_match(str):
    tags = local('git tag -l "%s"' % str, capture=True)

    if len(tags) == 0:
        return None

    tags = tags.split()
    tags.sort()
    return tags[-1]


def get_tag_names(prefix):
    """Return the names of the last and next tag."""
    num = 1
    today = datetime.date.today()
    next_tag_name = '%s-%i-%.2i-%.2i' % (prefix, today.year, today.month, today.day)
    last_tag_name = get_last_tag_match(next_tag_name + '.*')

    if last_tag_name is None:
        num = 1
    else:
        match = re.search('%s-[0-9]{4}-[0-9]{2}-[0-9]{2}\.([0-9]*)' % prefix, last_tag_name)
        num = int(match.group(1)) + 1

    next_tag_name = '%s.%.3i' % (next_tag_name, num)
    return (last_tag_name, next_tag_name)


def need_to_tag(version1, version2):
    sha_version1 = local('git log --pretty=format:%%H %s -1' % version1, capture=True)
    if version2:
        sha_version2 = local('git log --pretty=format:%%H %s -1' % version2, capture=True)
        if sha_version1 == sha_version2:
            return False
    return True


def is_working_directory_clean():
    status = local('git status', capture=True)
    if status.find('working directory clean') > -1:
        return True
    return False


def lines_in_file(filename, skip_prefixes=None):
    if not os.path.exists(filename):
        return
    if skip_prefixes is None:
        skip_prefixes = ()
    for line in open(filename, 'r').readlines():
        line = line.strip()
        if line and not line.startswith(skip_prefixes):
            yield line
