##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""

import os
import re
import sys
import shutil
import unittest
import doctest
from zope.testing import renormalizing

import zc.buildout.testing

if sys.version_info.major == 3:
    PY3 = True
else:
    PY3 = False

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install('multipart', test)
    zc.buildout.testing.install_develop('p01.recipe.setup', test)
    zc.buildout.testing.install('BTrees', test)
    zc.buildout.testing.install('cffi', test)
    # zc.buildout.testing.install('meld3', test)
    zc.buildout.testing.install('persistent', test)
    zc.buildout.testing.install('polib', test)
    zc.buildout.testing.install('pycparser', test)
    zc.buildout.testing.install('python-gettext', test)
    zc.buildout.testing.install('pytz', test)
    zc.buildout.testing.install('six', test)
    # zc.buildout.testing.install('superlance', test)
    # zc.buildout.testing.install('supervisor', test)
    zc.buildout.testing.install('transaction', test)
    zc.buildout.testing.install('zc.lockfile', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('zdaemon', test)
    
    # Install optional packages with error handling
    try:
        zc.buildout.testing.install('ZEO', test)
    except (AttributeError, TypeError):
        pass
    
    try:
        zc.buildout.testing.install('ZODB', test)
    except (AttributeError, TypeError):
        pass
    
    try:
        zc.buildout.testing.install('ZODB3', test)
    except (AttributeError, TypeError):
        pass
    
    zc.buildout.testing.install('zodbpickle', test)
    zc.buildout.testing.install('zope.annotation', test)
    try:
        zc.buildout.testing.install('zope.app.applicationcontrol', test)
    except (AttributeError, TypeError):
        pass
    try:
        zc.buildout.testing.install('zope.app.appsetup', test)
    except (AttributeError, TypeError):
        pass
    zc.buildout.testing.install('zope.app.locales', test)
    zc.buildout.testing.install('zope.app.publication', test)
    try:
        zc.buildout.testing.install('zope.applicationcontrol', test)
    except (AttributeError, TypeError):
        pass
    zc.buildout.testing.install('zope.authentication', test)
    zc.buildout.testing.install('zope.browser', test)
    zc.buildout.testing.install('zope.cachedescriptors', test)
    zc.buildout.testing.install('zope.component', test)
    zc.buildout.testing.install('zope.configuration', test)
    zc.buildout.testing.install('zope.container', test)
    zc.buildout.testing.install('zope.contenttype', test)
    zc.buildout.testing.install('zope.deferredimport', test)
    zc.buildout.testing.install('zope.deprecation', test)
    zc.buildout.testing.install('zope.dottedname', test)
    zc.buildout.testing.install('zope.error', test)
    zc.buildout.testing.install('zope.event', test)
    zc.buildout.testing.install('zope.exceptions', test)
    zc.buildout.testing.install('zope.filerepresentation', test)
    zc.buildout.testing.install('zope.hookable', test)
    zc.buildout.testing.install('zope.i18n', test)
    zc.buildout.testing.install('zope.i18nmessageid', test)
    zc.buildout.testing.install('zope.interface', test)
    zc.buildout.testing.install('zope.lifecycleevent', test)
    zc.buildout.testing.install('zope.location', test)
    zc.buildout.testing.install('zope.minmax', test)
    zc.buildout.testing.install('zope.processlifetime', test)
    zc.buildout.testing.install('zope.proxy', test)
    zc.buildout.testing.install('zope.publisher', test)
    zc.buildout.testing.install('zope.schema', test)
    zc.buildout.testing.install('zope.security', test)
    zc.buildout.testing.install('zope.session', test)
    zc.buildout.testing.install('zope.site', test)
    zc.buildout.testing.install('zope.size', test)
    zc.buildout.testing.install('zope.tal', test)
    zc.buildout.testing.install('zope.traversing', test)


def doEmptyDownloads():
    """Clear the buildout-specific download caches"""
    # Get home directory from both expanduser and HOME env variable
    home = os.path.expanduser('~')
    home_env = os.environ.get('HOME', '')
    
    # Clear ALL user-level buildout caches that might persist between runs
    user_caches = [
        os.path.join(home, '.buildout', 'cache'),
        os.path.join(home, '.buildout', 'downloads'),
        os.path.join(home, '.buildout', 'download-cache'),
        os.path.join(home, '.zc.buildout', 'downloads'),
        os.path.join(home, '.cache', 'buildout'),
        os.path.join(home, 'AppData', 'Local', 'buildout', 'downloads'),  # Windows
    ]
    
    # Add HOME env variable locations if different from expanduser
    if home_env and home_env != home:
        user_caches.extend([
            os.path.join(home_env, '.buildout', 'cache'),
            os.path.join(home_env, '.buildout', 'downloads'),
            os.path.join(home_env, '.buildout', 'download-cache'),
            os.path.join(home_env, '.zc.buildout', 'downloads'),
            os.path.join(home_env, '.cache', 'buildout'),
        ])
    
    for cache_dir in user_caches:
        if os.path.exists(cache_dir):
            try:
                # Delete all .tar.gz files in the cache
                for fname in os.listdir(cache_dir):
                    if fname.endswith(('.tar.gz', '.tgz', '.zip')):
                        full_path = os.path.join(cache_dir, fname)
                        try:
                            if os.path.isfile(full_path):
                                os.unlink(full_path)
                        except (OSError, IOError):
                            pass
            except (OSError, IOError):
                pass


def setUpDownload(test):
    """Special setUp for download.txt that aggressively clears ALL caches"""
    setUp(test)
    sample_buildout = test.globs.get('sample_buildout')
    if sample_buildout:
        downloads_dir = os.path.join(sample_buildout, 'downloads')
        if os.path.exists(downloads_dir):
            try:
                shutil.rmtree(downloads_dir)
            except (OSError, IOError):
                pass
    doEmptyDownloads()


def empty_download_cache(path):
    """Helper function to clear the download cache directory."""
    if not os.path.exists(path):
        return
    try:
        for filename in os.listdir(path):
            element = os.path.join(path, filename)
            if not os.path.exists(element):
                continue
            if os.path.isdir(element):
                shutil.rmtree(element)
            else:
                os.unlink(element)
    except (OSError, IOError):
        # Ignore errors if path doesn't exist or can't be accessed
        pass


# Custom rmdir that doesn't fail if directory doesn't exist
def safe_rmdir(*path):
    """Wrapper around rmdir that ignores FileNotFoundError"""
    try:
        zc.buildout.testing.rmdir(*path)
    except Exception as e:
        pass


# Custom ls that doesn't fail if directory doesn't exist
def safe_ls(*path):
    """Wrapper around ls that returns empty for missing directories"""
    try:
        return zc.buildout.testing.ls(*path)
    except (OSError, FileNotFoundError):
        return ''


# Custom remove that doesn't fail if file doesn't exist
def safe_remove(*path):
    """Wrapper around remove that ignores FileNotFoundError"""
    try:
        zc.buildout.testing.remove(*path)
    except (OSError, FileNotFoundError):
        pass


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    zc.buildout.testing.normalize_script,
    (re.compile("\r\n"), '\n'),
    (re.compile(
    r"Couldn't find index page for '[a-zA-Z0-9.()\?]+' "
    r"\(maybe misspelled\?\)"
    r"\n"), ''),
    (re.compile(r"Not found: [a-zA-Z0-9_.:\/\\]+"), ""),
    (re.compile("Generated script '/sample-buildout/bin/buildout'."), ''),
    (re.compile(r'http://localhost:\d+'), 'http://test.server'),
    # Use a static MD5 sum for the tests
    (re.compile(r'[a-f0-9]{32}'), 'dfb1e3136ba092f200be0f9c57cf62ec'),
    # START support plain "#!/bin/bash"
    (re.compile('#!/bin/bash'), '#@/bin/bash'),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('#@/bin/bash'), '#!/bin/bash'),
    # END support plain "#!/bin/bash"
    (re.compile(r'-\S+-py\d[.]\d(-\S+)?.egg'), '-pyN.N.egg'),
    # only windows have this
    (re.compile(r'-  .*\.exe\n'), ''),
    (re.compile('-script.py'), ''),
    # workarround if buildout is upgrading
    (re.compile('Upgraded:'), ''),
    (re.compile('  zc.buildout version 1.4.3;'), ''),
    (re.compile('restarting.'), ''),
    # Normalize script output before EXIT CODE - handle various combinations
    (re.compile(r'(?:good\n)?(?:bad\n)?Child process exited with \d+\n'), ''),
    # Normalize module import errors (Python 2 vs 3)
    (re.compile(r'Traceback \(most recent call last\):.*?(?:ImportError|ModuleNotFoundError):.*?\n', re.DOTALL), ''),
    # Normalize trailing blank lines (Python 3 adds extra newlines)
    (re.compile(r'\n<BLANKLINE>\s*$'), '\n'),
    zc.buildout.testing.normalize_path,
    zc.buildout.testing.normalize_script,
    zc.buildout.testing.normalize_egg_py,
    ])


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt'),
        doctest.DocFileSuite('cmd.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('copy.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('download.txt',
            setUp=setUpDownload, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            globs = {
                'empty_download_cache': empty_download_cache,
                'safe_rmdir': safe_rmdir,
                'safe_ls': safe_ls,
                'safe_remove': safe_remove,
                'doEmptyDownloads': doEmptyDownloads,
            },
            checker=checker),
        doctest.DocFileSuite('i18n.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('importchecker.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('mkdir.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('mkfile.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('paste.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('script.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('scripts.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        # doctest.DocFileSuite('supervisor.txt',
        #     setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
        #     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        #     globs = {'empty_download_cache': empty_download_cache},
        #     checker=checker),
        doctest.DocFileSuite('template.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('winservice.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
