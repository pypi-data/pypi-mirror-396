# -*- coding: utf-8 -*-
# :Project:   PatchDB -- PostgreSQL script execution context
# :Created:   sab 31 mag 2014 13:03:33 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016, 2017, 2019, 2021, 2023 Lele Gaifax
#

from os import makedirs
from os.path import isdir, join
import subprocess

from ..states import StatesIndex
from . import logger
from .sql import SqlContext


class PostgresContext(SqlContext):
    def makeConnection(self, dsn):
        import psycopg as dbapi
        import re

        self.dsn = dsn
        logger.debug('Connecting to %s', self.dsn)
        self.connection = dbapi.connect(self.dsn)
        cursor = self.connection.cursor()
        cursor.execute("set client_encoding to unicode;")

        cursor.execute("SELECT version()")
        v = cursor.fetchone()[0]
        self.connection.rollback()

        m = re.match(r'PostgreSQL (\d+)\.?(\d+)?(?:\.(\d+))?(?:\.\d+)?(?:devel|beta|rc)?', v)
        if m is None:
            raise RuntimeError(f"Could not determine PostgreSQL version from {v!r}")

        pg_version = tuple(int(x) for x in m.group(1, 2) if x is not None)
        if len(pg_version) < 2:
            pg_version = pg_version + (0,)

        self.assertions.update({
            'postgresql': True,
            f'postgresql_{pg_version[0]}': True,
            f'postgresql_{pg_version[0]}_{pg_version[1]}': True,
            })
        for v in range(10, 15):
            self.assertions[f'postgresql_{v}_x'] = (v, 0) <= pg_version < (v + 1, 0),

    def setupContext(self):
        from ..patch import MAX_PATCHID_LEN

        cursor = self.connection.cursor()
        cursor.execute("SELECT tablename"
                       " FROM pg_tables"
                       " WHERE tablename = 'patchdb'")
        result = cursor.fetchone()
        if not result:
            logger.info('Creating patchdb table')
            cursor.execute("CREATE TABLE patchdb ("
                           " patchid VARCHAR(%d) NOT NULL PRIMARY KEY,"
                           " revision SMALLINT NOT NULL,"
                           " applied TIMESTAMP WITH TIME ZONE NOT NULL"
                           ")" % MAX_PATCHID_LEN)
        self.connection.commit()

    def savePoint(self, point):
        if not self.connection.autocommit:
            cursor = self.connection.cursor()
            cursor.execute("SAVEPOINT point_%s" % point)

    def rollbackPoint(self, point):
        if not self.connection.autocommit:
            cursor = self.connection.cursor()
            cursor.execute("ROLLBACK TO SAVEPOINT point_%s" % point)

    def commitTransaction(self):
        """Complete current transaction."""
        if not self.connection.autocommit:
            super().commitTransaction()
        else:
            self.connection.autocommit = False

    def rollbackTransaction(self):
        """Rollback current transaction."""
        if not self.connection.autocommit:
            super().rollbackTransaction()
        else:
            self.connection.autocommit = False

    def apply(self, patch, options=None, patch_manager=None):
        if patch.autocommit:
            self.connection.autocommit = True
        super().apply(patch, options, patch_manager)

    def classifyError(self, exc):
        code = exc.sqlstate
        msg = f'[{code}] {exc}'
        # See https://www.postgresql.org/docs/current/static/errcodes-appendix.html
        syntaxerror = code in ('42000', '42601')
        nonexistingobj = code in ('42883', '42P01', '42704')
        return msg, syntaxerror, nonexistingobj

    def backup(self, dir):
        state = self.state
        if state is None:
            logger.debug("Skipping initial backup")
            return

        if not isdir(dir):
            makedirs(dir)

        outfname = join(dir, state.state)
        cmd = ['pg_dump', '-d', self.dsn, '-Fc', '-Z9', '-f', outfname]
        subprocess.check_call(cmd)

        with StatesIndex(dir) as index:
            index.append(state)

        logger.info("Wrote pg_dump compressed backup to %s", outfname)

    def restore(self, backup):
        cmd = ['pg_restore', '-d', self.dsn, '-c', backup]
        subprocess.check_call(cmd)
        logger.info("Restored PostgreSQL database from %s", backup)
