##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""zc.recipe.egg with windows bugfixes
$Id: egg.py 5091 2021-01-22 14:17:52Z roger.ineichen $
"""

import logging
import os
import re
import sys
import zc.recipe.egg
import zc.buildout.easy_install

from p01.recipe.setup import makeBoolString


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""


env_template = """os.environ['%s'] = %r
"""


class ScriptsRecipe(zc.recipe.egg.Eggs):
    """Same as zc.recipe.egg:scripts but with fixing path in initialization"""

    def __init__(self, buildout, name, options):
        super(ScriptsRecipe, self).__init__(buildout, name, options)

        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['_b'] = options['bin-directory'] # backward compat.

        self.extra_paths = [
            os.path.join(buildout['buildout']['directory'], p.strip())
            for p in options.get('extra-paths', '').split('\n')
            if p.strip()
            ]
        if self.extra_paths:
            options['extra-paths'] = '\n'.join(self.extra_paths)

        relative_paths = options.get(
            'relative-paths',
            buildout['buildout'].get('relative-paths', 'false')
            )
        if relative_paths == 'true':
            options['buildout-directory'] = buildout['buildout']['directory']
            self._relative_paths = options['buildout-directory']
        else:
            self._relative_paths = ''
            assert relative_paths == 'false'

    parse_entry_point = re.compile(
        r'([^=]+)=(\w+(?:[.]\w+)*):(\w+(?:[.]\w+)*)$'
        ).match

    def install(self):
        reqs, ws = self.working_set()
        options = self.options

        scripts = options.get('scripts')
        if scripts or scripts is None:
            if scripts is not None:
                scripts = scripts.split()
                scripts = dict([
                    ('=' in s) and s.split('=', 1) or (s, s)
                    for s in scripts
                    ])

            for s in options.get('entry-points', '').split():
                parsed = self.parse_entry_point(s)
                if not parsed:
                    logging.getLogger(self.name).error(
                        "Cannot parse the entry point %s.", s)
                    raise zc.buildout.UserError("Invalid entry point")
                reqs.append(parsed.groups())

            dependent = makeBoolString(options.get('dependent-scripts'), False)
            if dependent:
                # Generate scripts for all packages in the working set,
                # except setuptools.
                reqs = list(reqs)
                for dist in ws:
                    name = dist.project_name
                    if name != 'setuptools' and name not in reqs:
                        reqs.append(name)

            # setup environment and
            initialization = initialization_template
            env_section = options.get('environment', '').strip()
            if env_section:
                env = self.buildout[env_section]
                for key, value in list(env.items()):
                    initialization += env_template % (key, value)

            # append additional initialization after sys path loading if given
            if options.get('initialization'):
                initialization += options.get('initialization')
                if initialization and sys.platform == 'win32':
                    initialization = initialization.replace('\\\\', '\\')
                    initialization = initialization.replace('\\', '/')

            return zc.buildout.easy_install.scripts(
                reqs, ws, sys.executable, options['bin-directory'],
                scripts=scripts,
                extra_paths=self.extra_paths,
                interpreter=options.get('interpreter'),
                initialization=initialization,
                arguments=options.get('arguments', ''),
                relative_paths=self._relative_paths,
                )

        return ()

    update = install
