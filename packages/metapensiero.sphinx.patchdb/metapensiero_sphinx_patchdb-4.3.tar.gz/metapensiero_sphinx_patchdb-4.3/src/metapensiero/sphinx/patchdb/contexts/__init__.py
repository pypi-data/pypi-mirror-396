# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Script execution contexts
# :Created:   Wed Nov  5 17:32:16 2003
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2003, 2014, 2016, 2017, 2019, 2021, 2023 Lele Gaifax
#

import logging
import os
import re

from ..locale import gettext as _


logger = logging.getLogger('context')


class ExecutionError(Exception):
    """
    Exception raised on execution errors.
    """


class ExecutionContext:
    """
    An instance of this class is able to execute a script in some
    particular language. This is somewhat abstract and must be
    subclassed and attached to a database...

    Another responsibility of this class instances is to keep
    a persistent knowledge about last applied revision of
    a given script.
    """

    language_name = None

    execution_contexts_registry = {}
    user_assertions = {}
    user_variables = {}

    @classmethod
    def forLanguage(cls, language):
        """
        Return the right execution context for the given `language`.
        """

        return cls.execution_contexts_registry.get(language)

    @classmethod
    def execute(cls, patch, options, patch_manager):
        """
        Execute the given `patch` in the right context.
        """

        ctx = cls.execution_contexts_registry.get(patch.language)
        if ctx:
            if options.assume_already_applied:
                logger.warning("Considering %s %s as applied", patch.language, patch)
                cls.execution_contexts_registry['sql'].applied(patch, options.dry_run)
            else:
                logger.info("Executing %s %s", patch.language, patch)
                ctx.apply(patch, options, patch_manager)
        else:
            raise ExecutionError("Not able to execute %s %s" %
                                 (patch.language, patch))

    def __init__(self):
        self.assertions = {}

    def register(self):
        """
        Insert this context instance in the registry.
        """

        if not self.language_name:
            raise ValueError(f'Class attribute {self.__class__.__name__}.language_name must'
                             f' be set to a non empty string')
        registry = self.execution_contexts_registry
        if self.language_name in registry:
            raise RuntimeError(f'The context for language {self.language_name!r} has been'
                               f' already registered: {registry[self.language_name]!r}')
        registry[self.language_name] = self

    def __enter__(self):
        self.register()
        return self

    def unregister(self):
        if not self.language_name:
            raise ValueError(f'Class attribute {self.__class__.__name__}.language_name must'
                             f' be set to a non empty string')
        registry = self.execution_contexts_registry
        if self.language_name not in registry:
            raise RuntimeError(f'The context for language {self.language_name!r} has not been'
                               f' registered yet')
        if registry[self.language_name] is not self:
            raise RuntimeError(f'The context for language {self.language_name!r} has been'
                               f' registered to a different instance:'
                               f' {registry[self.language_name]!r}')
        del registry[self.language_name]

    def __exit__(self, exc_type, exc_value, traceback):
        self.unregister()

    def addAssertions(self, assertions):
        """
        Add given `assertions` to the set of assertions managed by the context.
        """

        for assertion in assertions:
            if "=" in assertion:
                assertion, state = assertion.split('=')
                state = state.lower() in ('true', 't', '1', 'yes', 'y')
            else:
                state = True
            if assertion in self.assertions:
                raise ValueError('Cannot override existing "%s" assertion' %
                                 assertion)
            self.user_assertions[assertion] = state

    def addVariables(self, variables):
        """
        Add given `variables` to the set of variables managed by the context.
        """

        for variable in variables:
            if "=" in variable:
                name, value = variable.split('=', 1)
                name = name.strip()
                if not name.isidentifier():
                    raise ValueError('Invalid variable name (must be an identifier): %r'
                                     % name)
                if value and not all(c.isspace() or c.isalnum() for c in value):
                    raise ValueError('Invalid variable value (must be the empty string,'
                                     ' or composed by alphanumeric and whitespace chars): %r'
                                     % value)
                self.user_variables[name] = value
            else:
                raise ValueError('Invalid variable definition (must be VAR=VALUE): %s'
                                 % variable)

    def replaceUserVariables(self, text):
        """
        Replace all ``{{VARIABLE}}`` with their values.
        """

        def replace(match, uvars=self.user_variables):
            var = match.group(1)
            if var in uvars:
                return uvars[var]
            if var.startswith('ENV_'):
                evar = var[4:]
                if evar in os.environ:
                    return os.environ[evar]
            dv = match.group(2)
            if not dv:
                raise ExecutionError(f'Undefined variable "{var}" in {text!r}')
            return dv[1:]

        return re.sub(r"{{([a-zA-Z][a-zA-Z0-9_]*)(=[a-zA-Z0-9 ]*)?}}", replace, text)

    def verifyCondition(self, condition):
        """
        Verify given `condition`, returning False if it is not satisfied.
        """

        negated = condition.startswith('!')
        if negated:
            condition = condition[1:]
        assertion = (self.assertions.get(condition, False)
                     or self.user_assertions.get(condition, False))
        if negated:
            assertion = not assertion
        return assertion

    def isApplicable(self, patch):
        """
        Determine whether the given `patch` is applicable *now*.

        Return a tuple (result, reason).
        """
        return True, None

    def apply(self, patch, options=None, patch_manager=None):
        "Try to execute the given `patch` script"

        if hasattr(self, '_testing_state'):
            self[patch.patchid] = patch.revision
            if patch.brings:
                for pid, rev in patch.brings:
                    self[pid] = rev
            if patch.drops:
                for pid, rev in patch.drops:
                    self[pid] = None
        elif options is not None and options.dry_run:
            print(_("Would apply %s") % patch)


def get_context_from_args(args):
    "Create and return the right execution context for the given CLI arguments"

    if args.postgresql:
        from .postgres import PostgresContext
        return PostgresContext(dsn=args.postgresql)

    if args.firebird:
        from .firebird import FirebirdContext
        return FirebirdContext(dsn=args.firebird,
                               username=args.username, password=args.password)

    if args.mysql:
        from .mysql import MySQLContext
        return MySQLContext(host=args.host, port=args.port, db=args.mysql,
                            username=args.username, password=args.password,
                            charset=args.charset, driver=args.driver)

    if args.sqlite:
        from .sqlite import SQLiteContext
        return SQLiteContext(database=args.sqlite)


class DummyExecutionContext(ExecutionContext):
    def __init__(self, current_state=None):
        super().__init__()
        self.current_state = {} if current_state is None else current_state

    @property
    def patches(self):
        return self.current_state

    def __getitem__(self, patchid):
        return self.current_state.get(patchid)

    def __setitem__(self, patchid, revision):
        self.current_state[patchid] = revision


# Register the context for Python, always available
from .python import PythonContext
PythonContext().register()
