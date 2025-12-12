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

$Id:$
"""

import os
import sys
import string
import shutil

import zc.buildout
import zc.recipe.egg


def fixPath(path):
    """Ensure \\ in path"""
    path = os.path.abspath(path)
    path = path.replace('\\\\', '\\')
    path = path.replace('\\', '/')
    return path.replace('/', '\\\\')


def setUpInstallScript(srcFile, script, replacements):
    """Setup install script"""
    generated = []

    # generate the winservice script
    text = open(srcFile, "r").read()
    # perform replacements
    for var, string in replacements:
        text = text.replace(var, string)

    changed = not (os.path.exists(script) and open(script).read() == text)

    if changed:
        # If the file exists, keep the old file.  This is a
        # hopefully temporary hack to get around distutils
        # stripping the permissions on the server skeleton files.
        # We reuse the original default files, which have the
        # right permissions.
        old = os.path.exists(script)
        if old:
            f = open(script, "r+")
            f.truncate(0)
        else:
            f = open(script, "w")

        f.write(text)
        f.close()

        if not old:
            shutil.copymode(srcFile, script)
            shutil.copystat(srcFile, script)

            #get rid of compiled versions
            try:
                os.unlink(os.path.splitext(script)[0]+'.pyc')
            except OSError:
                pass
            try:
                os.unlink(os.path.splitext(script)[0]+'.pyo')
            except OSError:
                pass

    generated.append(script)

    return generated


PATCH_TEMPLATE = """
def exceptionlogger():
    import servicemanager
    import traceback
    servicemanager.LogErrorMsg("Script %%s had an exception: %%s" %% (
      __file__, traceback.format_exc()
    ))

try:
%(script)s
except Exception as e:
    exceptionlogger()
"""


def setUpPatchScript(srcFile, dstFile):
    """Setup patch script"""
    generated = []
    src = open(srcFile, 'rU').read()
    src = '\n'.join(['    '+line for line in src.split('\n')])
    dest = PATCH_TEMPLATE % dict(script=src, srcFile=srcFile)
    changed = not (os.path.exists(dstFile) and open(dstFile).read() == dest)

    if changed:
        open(dstFile, 'w').write(dest)
        shutil.copymode(srcFile, dstFile)
        shutil.copystat(srcFile, dstFile)

        #get rid of compiled versions
        try:
            os.unlink(os.path.splitext(dstFile)[0]+'.pyc')
        except OSError:
            pass

        try:
            os.unlink(os.path.splitext(dstFile)[0]+'.pyo')
        except OSError:
            pass

    generated.append(dstFile)

    return generated


class WinServiceSetup:
    """Windows service setup"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        # setup executable
        self.executable = self.buildout['buildout']['executable']

        if 'eggs' not in self.options:
            self.options['eggs'] = ''
        self.options['eggs'] = self.options['eggs'] + '\n' + 'pywin32'
        self.egg = zc.recipe.egg.Egg(buildout, name, self.options)

        # setup start script
        binDir = self.buildout['buildout']['bin-directory']
        runzope = options.get('runzope')
        runscript = options.get('runscript')

        # fix script name
        if not runzope and not runscript:
            raise zc.buildout.UserError(
                'Missing `runzope` or `runscript` option in the recipe.')

        if runzope and runscript:
            raise zc.buildout.UserError(
                'Only one of `runzope` or `runscript` allowed in the recipe.')

        if runzope:
            # old-ish way
            if not runzope.endswith('-script.py'):
                if runzope.endswith('.py'):
                    runzope = runzope[:3]
                runzope = '%s-script.py' % runzope

            if '/' in runzope or '\\' in runzope:
                # don't add the bin folder if there's already a folder
                script = runzope
            else:
                script = os.path.join(binDir, runzope)
        else:
            # new-ish way, just don't touch runscript
            script = runscript

        self.runScript = fixPath(script)

        options['serviceName'] = self.getServiceName()

    def getServiceName(self):
        try:
            serviceName = self.options['serviceName']
        except KeyError:
            if len(self.runScript) < 128:
                # make a meaningful name in case it fits
                serviceName = ''
                for c in self.runScript:
                    if c in string.ascii_letters + string.digits:
                        serviceName += c
                    else:
                        serviceName += '_'
            else:
                #otherwise a dumb hash
                serviceName = str(hash(self.runScript))
        return serviceName

    def install(self):
        if sys.platform != 'win32':
            print("winservice: Not a windows platform, doing nothing")
            return []

        options = self.options

        # setup service name
        defaultName = 'Zope3 %s' % self.name
        defaultDescription = 'Zope3 windows service for %s, using %s' % (
            self.name, self.runScript)
        displayName = options.get('name', defaultName)
        serviceName = options['serviceName']
        description = options.get('description', defaultDescription)
        parameters = options.get('parameters', '')
        python = self.executable
        pythondir = os.path.split(python)[0]
        #this is dumb... but stays unless someone figures something better
        pythonservice_exe = fixPath(
            r'%s\Lib\site-packages\win32\pythonservice.exe' % pythondir)
        instance_home = self.buildout['buildout']['directory']

        # raise exeption if the service exe is not here now
        if not os.path.exists(pythonservice_exe):
            raise zc.buildout.UserError('Python service %s does not exist.'  %
                pythonservice_exe)

        generated = []

        if options.get('debug') and self.runScript.lower().endswith('.py'):
            serviceScript = self.runScript.replace(
                '-script.py', '-servicedebug.py')
            generated += setUpPatchScript(self.runScript, serviceScript)
        else:
            serviceScript = self.runScript

        if serviceScript.lower().endswith('.exe'):
            # if the script is an exe, no need to run it with python
            python = ''

        self.winServiceVars = [
            ("<<PYTHON>>", python),
            ("<<SCRIPT>>", serviceScript),
            ("<<PYTHONSERVICE_EXE>>", pythonservice_exe),
            ("<<SERVICE_NAME>>", serviceName),
            ("<<SERVICE_DISPLAY_NAME>>", displayName),
            ("<<SERVICE_DESCRIPTION>>", description),
            ("<<PARAMETERS>>", parameters),
            ("<<INSTANCE_HOME>>", fixPath(instance_home)),
            ]

        # raise exeption if the app script is not here now
        if not os.path.exists(serviceScript):
            raise zc.buildout.UserError(
                'App start script %s does not exist.'  % self.runScript)

        # get templates
        winServiceTemplate = os.path.join(os.path.dirname(__file__),
            'winservice.in')

        # setup winservice file paths
        binDir = self.buildout['buildout']['bin-directory']
        script = os.path.join(binDir, 'winservice.py')

        generated += setUpInstallScript(winServiceTemplate, script,
            self.winServiceVars)

        # return list of generated files
        return generated

    update = install
