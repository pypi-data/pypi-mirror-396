# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Python scripts test
# :Created:   lun 22 feb 2016 22:45:29 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2019, 2023 Lele Gaifax
#

import os
import sys

import fixtures


class TestPythonScripts(fixtures.BaseTestCase):
    TEST_TXT = """
    ================
     Python scripts
    ================

    A script may be written in the Python_ language, that obviously is able to perform any
    action, not just tweaking the database.

    .. patchdb:script:: My first script (v2)
       :description: The most basic Python script
       :language: python
       :conditions: python_2_x

       print "This is Python 2!"

    .. patchdb:script:: My second script (v2)
       :description: The most basic Python script
       :language: python
       :conditions: !python_3_x

       print "This is also Python 2!"

    .. patchdb:script:: My first script (v3)
       :description: The most basic Python script
       :language: python
       :conditions: python_3_x

       print("This is Python 3!")

    .. patchdb:script:: My second script (v3)
       :description: The most basic Python script
       :language: python
       :conditions: !python_2_x

       print("This is also Python 3!")

    .. patchdb:script:: Say hello
       :language: python
       :always: first

       print("Hello!")

    .. patchdb:script:: Say hello again
       :description: A cordial script
       :language: python

       print("Hello again from script %r!" % patch_manager['say hello again'].description)

    .. patchdb:script:: Say goodbye
       :language: python
       :always: last

       print("Goodbye{{WHO=}} from {{ENV_USER}}!")

    .. patchdb:script:: Say hello on logger
       :description: A cordial script
       :language: python

       def hello():
         return "Hi from me!"

       def log_hello():
         logger.warning("I got this for you: %s", hello())

       log_hello()

    .. _Python: http://www.python.org/
    """

    def test(self):
        output = self.patchdb()
        self.assertIn('Hello!', output)
        self.assertIn("Hello again from script 'A cordial script'!", output)
        self.assertIn('Goodbye from %s!' % os.environ['USER'], output)
        self.assertIn('This is Python %d!' % sys.version_info.major, output)
        self.assertIn('This is also Python %d!' % sys.version_info.major, output)
        self.assertIn('Done, applied 6 script', output)
        self.assertIn('[W] I got this for you: Hi from me!', self.patchdb_output)
        output = self.patchdb('--define', 'WHO= to you')
        self.assertIn("Hello!", output)
        self.assertNotIn("Hello again", output)
        self.assertIn('Goodbye to you from %s!' % os.environ['USER'], output)
        self.assertIn('Done, applied 2 script', output)
        output = self.patchdb('--define', 'ENV_USER=tester')
        self.assertIn('Hello!', output)
        self.assertIn('Goodbye from tester!', output)
        self.assertIn('Done, applied 2 script', output)
