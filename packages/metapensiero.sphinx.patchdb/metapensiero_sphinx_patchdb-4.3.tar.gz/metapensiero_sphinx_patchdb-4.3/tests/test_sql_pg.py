# -*- coding: utf-8 -*-
# :Project:   PatchDB -- PG specific SQL statements test
# :Created:   mar 23 feb 2016 00:08:50 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2021, 2023, 2025 Lele Gaifax
#

from os import environ
from os.path import dirname, join
import subprocess

try:
    import psycopg
except ImportError:
    pass
else:
    import fixtures
    import test_sql
    import test_states

    DBNAME = 'mp-s-patchdb-test'
    PORT = '65432'

    class PGMixin:
        DB_OPTION = '--postgresql'
        DB_NAME = f'dbname={DBNAME} host=localhost port={PORT} user=patchdb'

        @classmethod
        def start_postgresql(cls):
            tests_dir = dirname(__file__)
            subprocess.call(('bash', join(tests_dir, 'postgresql'), 'start'))

        @classmethod
        def drop_database_if_exists(cls):
            cls.start_postgresql()
            env = environ | dict(PGHOST='localhost', PGPORT=PORT, PGUSER='patchdb')
            subprocess.call(('dropdb', '--if-exists', DBNAME), env=env)

        @classmethod
        def create_database(cls):
            cls.start_postgresql()
            env = environ | dict(PGHOST='localhost', PGPORT=PORT, PGUSER='patchdb')
            subprocess.check_call(('createdb', '-E', 'UTF-8', '-T', 'template0', DBNAME),
                                  env=env)

    class TestSingleSQLScript(PGMixin, test_sql.TestSingleSQLScript):
        pass

    class TestMultiSQLScriptIgnoringErrors(PGMixin,
                                           test_sql.TestMultiSQLScriptIgnoringErrors):
        pass

    class TestStates(PGMixin, test_states.TestStates):
        pass

    class TestRestoreState(PGMixin, test_states.TestRestoreState):
        pass

    class TestDropNonExistingTable(PGMixin, test_sql.TestDropNonExistingTable):
        pass

    class TestRevokeAllPrivileges(PGMixin, fixtures.BaseTestCase):
        TEST_TXT = """
        Ignore revoking non granted privileges
        ======================================

        .. patchdb:script:: Create first table

           create table sl_test (
             id integer primary key
           )

        .. patchdb:script:: Revoke all privileges
           :depends: Create first table

           revoke all privileges on table sl_test from public

        .. patchdb:script:: Revoke all privileges on table again
           :depends: Revoke all privileges

           revoke all privileges on table sl_test from public
        """
        NUM_OF_SCRIPTS = 3

    class TestAutocommitScript(PGMixin, fixtures.BaseTestCase):
        TEST_TXT = """
        Some SQL statements cannot be executed within a transaction
        ===========================================================

        .. patchdb:script:: Create empty enum

           create type my_enum as enum ()

        .. patchdb:script:: Add an item to the enum
           :depends: Create empty enum
           :autocommit:

           alter type my_enum add value 'foo'
        """
        NUM_OF_SCRIPTS = 2

    class TestCircularDependencyCase(PGMixin, fixtures.BaseTestCase):
        TEST_TXT = """
        First version
        =============

        .. patchdb:script:: Parents table

           create table parents (
             id integer primary key,
             name text not null,
             children_count integer
           )

        .. patchdb:script:: Children table
           :depends: Parents table

           create table children (
             id integer primary key,
             parent_id integer not null,
             name text not null,
             constraint parent foreign key (parent_id) references parents (id)
           )

        .. patchdb:script:: Data
           :depends:
             - Parents table
             - Children table

           insert into parents (id, name, children_count) values (1, 'adam', 3)
           ;;
           insert into children (id, parent_id, name) values (1, 1, 'cain'), (2, 1, 'abel'), (3, 1, 'seth')
        """
        NUM_OF_SCRIPTS = 3

        def test_1(self):
            connection, exception = self.get_connection_and_base_exception()
            try:
                cursor = connection.cursor()
                cursor.execute('select name, children_count from parents')
                row = cursor.fetchone()
                assert row == ('adam', 3)
            finally:
                connection.close()

        SECOND_REV = """
        Second version
        ==============

        .. patchdb:script:: Parents table
           :revision: 2

           create table parents (
             id integer primary key,
             name text not null
           )

        .. patchdb:script:: Children table
           :depends: Parents table

           create table children (
             id integer primary key,
             parent_id integer not null,
             name text not null,
             constraint parent foreign key (parent_id) references parents (id)
           )

        .. patchdb:script:: Counter function
           :depends:
             - Parents table
             - Children table

           create function children_count(parents)
           returns integer as $$
             select count(*) from children where parent_id = $1.id
           $$ stable language sql

        .. patchdb:script:: Replace children_count with a function
           :depends:
             - Parents table@1
             - Counter function
           :brings:
             - Parents table@2

           alter table parents drop column children_count
        """

        def test_2(self):
            self.build({'test.txt': self.SECOND_REV})
            output = self.patchdb('--debug')
            self.assertIn('could not apply 2 scripts', output.lower())

    class TestDependencyOnAnyRevision(TestCircularDependencyCase):
        SECOND_REV = """
        Second version
        ==============

        .. patchdb:script:: Parents table
           :revision: 2

           create table parents (
             id integer primary key,
             name text not null
           )

        .. patchdb:script:: Children table
           :depends: Parents table

           create table children (
             id integer primary key,
             parent_id integer not null,
             name text not null,
             constraint parent foreign key (parent_id) references parents (id)
           )

        .. patchdb:script:: Counter function
           :depends:
             - Parents table@*
             - Children table

           create function children_count(parents)
           returns integer as $$
             select count(*) from children where parent_id = $1.id
           $$ stable language sql

        .. patchdb:script:: Replace children_count with a function
           :depends:
             - Parents table@1
             - Counter function
           :brings:
             - Parents table@2

           alter table parents drop column children_count
        """

        def test_2(self):
            self.build({'test.txt': self.SECOND_REV})
            output = self.patchdb('--debug')
            self.assertIn('Done, applied 2 scripts', output)

        def test_3(self):
            connection, exception = self.get_connection_and_base_exception()
            try:
                cursor = connection.cursor()
                cursor.execute('select p.name, p.children_count from parents as p')
                row = cursor.fetchone()
                assert row == ('adam', 3)
            finally:
                connection.close()

    class TestPatchOnNewTable(PGMixin, fixtures.BaseTestCase):
        TEST_TXT = """
        Create first table
        ==================

        .. patchdb:script:: First table

           create table first_table (
             id integer primary key
           )
        """

        TEST2_TXT = """
        Create first and second table
        =============================

        .. patchdb:script:: First table

           create table first_table (
             id integer primary key
           )

        .. patchdb:script:: Second table

           create table second_table (
             id integer primary key
           )
        """

        TEST3_TXT = """
        Create first and second table with a variant
        ============================================

        .. patchdb:script:: First table

           create table first_table (
             id integer primary key
           )

        .. patchdb:script:: Second table
           :revision: 2

           create table second_table (
             id integer primary key,
             a varchar
           )

        .. patchdb:script:: Add field to second table
           :depends:
             - Second table@1
           :brings:
             - Second table@2

           alter table second_table add column a varchar
        """

        def NO_test_2(self):
            assert self.build({'test.txt': self.TEST2_TXT}) is None
            output = self.patchdb('--debug')
            print(self.sphinx.patchdb_output)
            self.assertIn('Done, applied 1 scripts', output)

        # Here we exercise the case when the target DB is still
        # at the initial state, that is, the TEST2_TXT patches
        # where not applied, and we are jumping to TEST3 directly:
        # the "Add field to second table" shall be ignored, and
        # instead the "Second table" script should be applied

        def test_3(self):
            assert self.build({'test.txt': self.TEST3_TXT}) is None
            output = self.patchdb('--debug')
            self.assertIn('Done, applied 1 script', output)
