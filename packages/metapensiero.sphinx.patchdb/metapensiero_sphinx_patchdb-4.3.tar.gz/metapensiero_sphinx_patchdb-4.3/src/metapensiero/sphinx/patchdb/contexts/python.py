# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Python script execution context
# :Created:   sab 31 mag 2014 12:55:31 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016, 2017, 2019, 2023 Lele Gaifax
#

import sys

from . import ExecutionContext, logger


class PythonContext(ExecutionContext):
    language_name = 'python'

    execution_context = {'contexts': ExecutionContext.execution_contexts_registry}

    def __init__(self):
        ExecutionContext.__init__(self)
        self.assertions.update({
            'python_3_x': sys.version_info.major == 3,
            'python_2_x': sys.version_info.major == 2,
        })

    def apply(self, patch, options=None, patch_manager=None):
        """
        Execute the Python script, with the following symbols defined in its namespace:

        contexts
          the various *execution contexts*, in particular ``contexts['sql'].connection``
          is the open connection to the database

        patch_manager
          the current store of patches

        logger
          where the script may write its log
        """

        if options is not None and options.dry_run:
            ExecutionContext.apply(self, patch, options, patch_manager)
        else:
            globs = self.execution_context.copy()
            globs['logger'] = logger
            globs['options'] = options
            globs['patch_manager'] =  patch_manager
            script = self.replaceUserVariables(patch.script)
            exec(script, globs)
        sqlctx = self.execution_contexts_registry['sql']
        sqlctx.applied(patch, options is not None and options.dry_run)
