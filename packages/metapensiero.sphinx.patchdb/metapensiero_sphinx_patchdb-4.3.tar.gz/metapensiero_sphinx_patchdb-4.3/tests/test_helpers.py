# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test helper functions
# :Created:   sab 28 mag 2016 20:24:52 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2023 Lele Gaifax
#

def test_split_script():
    from metapensiero.sphinx.patchdb.contexts.sql import split_script

    assert split_script('a\n;;\n;;\n;;\nb\n') == ['a\n', 'b\n']
    assert split_script('a\n  ;;  \nb  \n\n;; \n c \n') == ['a\n', 'b  \n\n', ' c \n']


def test_is_create_domain():
    from metapensiero.sphinx.patchdb.contexts.sql import is_create_domain

    assert is_create_domain('Create Domain foo bar')
    assert is_create_domain('/**/ CREATE /* asd */ Domain foo bar')
    assert is_create_domain('-- foo\n\n CREATE /* asd */ Domain foo bar')

    assert not is_create_domain('Create Table foo bar')

    statement = "Create Domain foo /* asd */ varchar(10)"
    iscd = is_create_domain(statement)
    name = next(iscd).value
    definition = statement[next(iscd).pos:]
    assert name == 'foo'
    assert definition == 'varchar(10)'

    statement = "Create Domain `foo` /* asd */ varchar(10)"
    iscd = is_create_domain(statement)
    name = next(iscd).value
    definition = statement[next(iscd).pos:]
    assert name == '`foo`'
    assert definition == 'varchar(10)'

    statement = 'Create Domain "TABLE" /* asd */ varchar(10)'
    iscd = is_create_domain(statement)
    name = next(iscd).value
    definition = statement[next(iscd).pos:]
    assert name == '"TABLE"'
    assert definition == 'varchar(10)'


def test_is_create_or_alter_table():
    from metapensiero.sphinx.patchdb.contexts.sql import is_create_or_alter_table
    from metapensiero.sphinx.patchdb.contexts.sql import replace_fake_domains

    assert is_create_or_alter_table('Create Table foo')
    assert is_create_or_alter_table('/**/ CREATE /* asd */ Table foo')
    assert is_create_or_alter_table('-- foo\n\n CREATE /* asd */ Table foo')

    assert not is_create_or_alter_table('Create Domain foo bar')

    statement = "create table foo (a /* an int */ integer_t, b /* a bool */ bool_t)"
    domains = {'integer_t': 'INTEGER', 'bool_t': 'CHAR(1)'}
    isct = is_create_or_alter_table(statement)
    assert (replace_fake_domains(statement, isct, domains)
            == "create table foo (a /* an int */ INTEGER, b /* a bool */ CHAR(1))")

    statement = 'create table foo (a INTEGER_T, b "Bool_T")'
    domains = {'integer_t': 'INTEGER', 'bool_t': 'CHAR(1)'}
    isct = is_create_or_alter_table(statement)
    assert (replace_fake_domains(statement, isct, domains)
            == 'create table foo (a INTEGER, b "Bool_T")')

    statement = 'CREATE TABLE t (v0 value_t, v1 VALUE_T, v2 "VALUE_T", v3 `Value_T`)'
    domains = {'value_t': 'X', '"VALUE_T"': 'Y', '`Value_T`': 'Z'}
    isct = is_create_or_alter_table(statement)
    assert (replace_fake_domains(statement, isct, domains)
            == 'CREATE TABLE t (v0 X, v1 X, v2 Y, v3 Z)')

    statement = 'ALTER TABLE test ADD another value_t NOT NULL'
    domains = {'value_t': 'X'}
    isct = is_create_or_alter_table(statement)
    assert (replace_fake_domains(statement, isct, domains)
            == 'ALTER TABLE test ADD another X NOT NULL')

    statement = 'ALTER TABLE t CHANGE another another value_t NULL DEFAULT NULL'
    domains = {'value_t': 'X'}
    isct = is_create_or_alter_table(statement)
    assert (replace_fake_domains(statement, isct, domains)
            == 'ALTER TABLE t CHANGE another another X NULL DEFAULT NULL')
