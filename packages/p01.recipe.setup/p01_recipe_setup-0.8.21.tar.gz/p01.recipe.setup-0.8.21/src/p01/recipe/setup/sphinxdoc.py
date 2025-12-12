##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

import sys
import os
import os.path
from email import message_from_string

import zc.buildout
import zc.buildout.easy_install
import zc.recipe.egg
import pkg_resources
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

from p01.recipe.setup import CHMODMixin
from p01.recipe.setup import CHOWNMixin
from p01.recipe.setup import LoggerMixin
from p01.recipe.setup import TRUE_VALUES


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""


env_template = """os.environ['%s'] = %r
"""


class SphinxDocRecipe(CHOWNMixin, CHMODMixin, LoggerMixin):
    """Make directory recipe using os.makedirs(path).

    See sphinx/cmdline.py and sphinx/application.py for enhance this recipe.

    Here are some samples:

    [docs]
    recipe = p01.recipe.setup:sphinx
    eggs = p01.recipe.setup
           sphinx_rtd_theme
    pkg = p01.recipe.setup
    conf =

        source_suffix = '.txt'
        master_doc = 'index'
        project = '%(project)s'
        copyright = 'Projekt01 GmbH, 6330 Cham'
        version = '%(version)s'
        release = '%(version)s'
        pygments_style = 'sphinx'
        today_fmt = '%%B %%d, %%Y'
        html_last_updated_fmt = '%%b %%d, %%Y'

        # theme
        import sphinx_rtd_theme
        html_theme = "sphinx_rtd_theme"
        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


    [docs2]
    recipe = p01.recipe.setup:sphinx
    eggs = sphinx_rtd_theme
    source = ${buildout:directory}/foo
    target = ${buildout:directory}/docs
    conf =

        source_suffix = '.txt'
        master_doc = 'index'
        project = 'Dokumentation Projekt'
        copyright = 'Projekt01 GmbH'
        version = '1.0'
        release = '1.0'
        pygments_style = 'sphinx'
        today_fmt = '%%B %%d, %%Y'
        html_last_updated_fmt = '%%b %%d, %%Y'

        # theme
        import sphinx_rtd_theme
        html_theme = "sphinx_rtd_theme"
        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
            options.get('script', self.name))

        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'p01.recipe.setup[sphinx]'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

        self.pkgName = self.options.get('pkg', None)
        self.source = self.options.get('source', None)
        if self.pkgName is not None and self.source is not None:
            raise zc.buildout.UserError(
                "You can only define pkg or source as documentation source and "
                "not both")
        if self.pkgName is None and self.source is None:
            raise zc.buildout.UserError(
                "You must define source or pkg and reference the documentation "
                "source")

    def getSourceDirectory(self, pkg=None):
        """Returns package metadata"""
        if pkg is not None:
            srcdir = os.path.join(pkg.location,
                pkg.project_name.replace('.','/'))
        else:
            srcdir = self.options.get('source', )
            if srcdir is None:
                raise zc.buildout.UserError("You must define source or pkg")
        if not os.path.isdir(srcdir):
            raise zc.buildout.UserError("Source directory %s does not exist" %
                srcdir)
        return os.path.normpath(srcdir)

    def install(self):
        dest = []
        eggs, ws = self.egg.working_set()

        # create parts directory for configuration files.
        partdir = os.path.join(
            self.buildout['buildout']['parts-directory'], self.name)
        if not os.path.isdir(partdir):
            os.mkdir(partdir)

        # setup doc eggs
        if self.pkgName is not None:
            # generate doc for a package by it's package name
            #
            # get source
            pkg = ws.find(pkg_resources.Requirement.parse(self.pkgName))
            # get source directory
            srcdir = os.path.join(pkg.location,
                pkg.project_name.replace('.','/'))
            # get package meta data
            infos = pkg._get_metadata('PKG-INFO')
            msg = '\n'.join(infos)
            data = dict(list(message_from_string(msg).items()))
            metadata = {
                'project': data.get('Name', pkg.project_name),
                'version': data.get('Version', pkg.version)
            }
        else:
            # generate doc based on given source directory
            pkg = None
            # get source directory
            srcdir = self.options.get('source', )
            if srcdir is None:
                raise zc.buildout.UserError("You must define source or pkg")
            # get package meta data
            metadata = {}

        # get source directory
        srcdir = self.getSourceDirectory(pkg)

        # get/create .doctrees directory
        doctreedir = os.path.join(partdir, '.doctrees')
        if not os.path.isdir(doctreedir):
            os.mkdir(doctreedir)

        # create conf.py
        conf = self.options['conf']
        try:
            cFile = conf % metadata
        except TypeError:
            raise zc.buildout.UserError(
                "p01.recipe.setup:sphinx: Your conf.py file definition in your "
                "part section [%s] contains unquoted %% variables. Please only "
                "use %%%% instead of %%." % self.name)
        except KeyError:
            if pkg is not None:
                raise zc.buildout.UserError(
                    "p01.recipe.setup:sphinx: Your conf.py file definition in "
                    "your part section [%s] contains unsuported python "
                    "variable. We only support %%(project)s and %%(version)s "
                    "as variable." % self.name)
            else:
                raise zc.buildout.UserError(
                    "p01.recipe.setup:sphinx: Your conf.py file definition in "
                    "your part section [%s] contains unsuported python "
                    "variable. We do not support variables if you use a "
                    "document resource target" % self.name)
        confPyPath = os.path.join(partdir, 'conf.py')
        confPy = open(confPyPath, 'w')
        confPy.write(cFile)
        confPy.close()
        dest.append(confPyPath)

        # get/create output directory
        outdir = os.path.join(partdir, 'build')
        outdir = self.options.get('target', outdir)
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

        arguments = {}
        cmdargs = []
        for ar in self.options.get('arguments', '').splitlines():
            a = ar.strip()
            if a:
                cmdargs.append(a)
        quiet = self.options.get('quiet', '')
        if quiet in TRUE_VALUES:
            quiet = True
        else:
            quiet = False
        arguments = {
            'srcdir': srcdir,
            'outdir': outdir,
            'confdir': partdir,
            'doctreedir': doctreedir,
            'arguments': cmdargs,
            'quiet': quiet
            }

        # setup environment
        initialization = initialization_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in list(env.items()):
                initialization += env_template % (key, value)

        dest.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'p01.recipe.setup.sphinxdoc', 'main'),],
            ws,
            self.options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths=self.egg.extra_paths,
            arguments = "%r" % arguments,
            initialization = initialization,
            ))

        return dest

    update = install


def main(data):
    import sphinx
    quiet = data['quiet']
    confdir = data['confdir']
    doctreedir = data['doctreedir']
    srcdir = data['srcdir']
    outdir = data['outdir']
    arguments = data['arguments']
    args = ['-q','-c', confdir, '-d', doctreedir]
    if arguments:
        args += arguments
    args += [srcdir, outdir]
    pargs = []
    aa = ''
    for a in args:
        if a.startswith('-'):
            if aa.startswith('-'):
                # also add previous arg
                pargs.append(aa)
            aa = a
        elif aa.startswith('-'):
            pargs.append('%s %s' % (aa, a))
            aa = ''
        else:
            pargs.append(a)
            aa = ''

    if not os.path.isdir(doctreedir):
        os.mkdir(doctreedir)
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    if not quiet:
        print("=============================")
        print("building sphinx documentation")
        print("confdir:    %s" % confdir)
        print("srcdir:  %s" % srcdir)
        print("outdir:  %s" % outdir)
        print("doctree: %s" % doctreedir)
        print("quiet:  %s" % quiet)
        print("args:    %s" % "\n         ".join(pargs))
        print("-----------------------------")
    sphinx.main(argv=sys.argv+args)
    if not quiet:
        print("=============================")

