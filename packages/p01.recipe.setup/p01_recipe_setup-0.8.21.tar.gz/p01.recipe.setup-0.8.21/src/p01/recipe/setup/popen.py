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
"""Z3c development recipes

$Id: popen.py 5080 2021-01-21 14:44:34Z roger.ineichen $
"""

import os
import subprocess

import zc.buildout
import zc.recipe.egg

from p01.recipe.setup import LoggerMixin


class PopenRecipe(LoggerMixin):
    """Popen recipe"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def popen(self, cmd):
        if self.buildout['buildout']['offline'] != 'true':
            # environ
            env = {'PATH': os.environ['PATH']}
            env_section = self.options.get('env', '').strip()
            if env_section:
                for key, value in self.buildout[env_section]:
                    env[key.strip()] = value.strip()
            # subprocess
            self.logger.info('environ: %s' % ' '.join(
                ['    %s:%s' % (k, v) for k, v in list(env.items())]))
            self.logger.info('processing: %s' % cmd)
            stdout = stderr = subprocess.PIPE
            p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, shell=True,
                env=env)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                msg = "Error code (%s) while running command: %s" % (
                    p.returncode, stderr)
                self.logger.error(msg)
                raise zc.buildout.UserError(msg)

    def install(self):
        location = os.path.abspath(os.path.join(
            self.buildout["buildout"]["parts-directory"], self.name))
        if not os.path.exists(location):
            os.mkdir(location)
            self.options.created(location)

        # switch location
        chdir = os.path.abspath(self.options['chdir'])
        os.chdir(chdir)

        # install
        install = self.options.get('install')
        if install is not None:
            arguments = []
            for arg in install.strip().split():
                if arg:
                    #arguments.append(arg.replace('\\', '/'))
                    arguments.append(arg)
        cmd = ' '.join(arguments)
        self.popen(cmd)

        return self.options.created()

    def update(self):
        pass
