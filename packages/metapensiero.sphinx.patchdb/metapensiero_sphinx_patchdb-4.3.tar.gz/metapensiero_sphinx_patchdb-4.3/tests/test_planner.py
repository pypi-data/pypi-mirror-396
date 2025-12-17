# -*- coding: utf-8 -*-
# :Project:   PatchDB — Tests for ExecutionPlanner
# :Created:   sab 13 mag 2023, 11:38:25
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2023 Lele Gaifax
#

from graphlib import CycleError

import pytest

from metapensiero.sphinx.patchdb.contexts import DummyExecutionContext
from metapensiero.sphinx.patchdb.contexts.sqlite import SQLiteContext
from metapensiero.sphinx.patchdb.manager import PatchManager
from metapensiero.sphinx.patchdb.patch import make_patch
from metapensiero.sphinx.patchdb.planner import ExecutionPlanner


def test_planner_1():
    ctx = DummyExecutionContext({'second': 1})
    pm = PatchManager()

    first = make_patch('first', 'script',
                       dict(revision=1,
                            language='test',
                            depends='second'))
    pm['first'] = first

    second = make_patch('second', 'script',
                        dict(revision=2,
                             language='test',
                             depends='third'))
    pm['second'] = second

    third = make_patch('third', 'script',
                       dict(depends='second@1',
                            preceeds='first',
                            language='test'))
    pm['third'] = third

    always_beg = make_patch('always_beg', 'script',
                            dict(always='first', language='test'))
    pm['always_beg'] = always_beg

    always_last = make_patch('always_last', 'script',
                             dict(always='last', language='test'))
    pm['always_last'] = always_last

    planner = ExecutionPlanner(pm, ctx)
    assert tuple(planner) == (
        always_beg,
        third,
        second,
        first,
        always_last,
    )


def test_planner_2():
    with SQLiteContext(database=':memory:') as ctx:
        pm = PatchManager()

        initial_a = make_patch('table a', 'create table a (a integer)',
                               dict(revision=1,
                                    language='sql'))

        ctx.apply(initial_a)

        table_a = make_patch('table a', 'create table a (a integer, b integer, c integer)',
                             dict(revision=3,
                                  language='sql'))
        pm += table_a

        transition_1_2 = make_patch('to table a2',
                                    'alter table a add column b integer',
                                    dict(revision=1,
                                         language='sql',
                                         depends='table a@1',
                                         brings='table a@2'))
        pm += transition_1_2

        transition_2_3 = make_patch('to table a3',
                                    'alter table a add column c integer',
                                    dict(revision=1,
                                         language='sql',
                                         depends='table a@2',
                                         brings='table a@3'))
        pm += transition_2_3

        content_table_a = make_patch('content table a',
                                     'insert into a (a,b,c) values (1,2,3)',
                                     dict(revision=1,
                                          language='sql',
                                          depends='table a@3'))
        pm += content_table_a

        planner = ExecutionPlanner(pm, ctx)
        assert tuple(planner) == (
            transition_1_2,
            transition_2_3,
            content_table_a,
        )


def test_planner_3():
    ctx = DummyExecutionContext({})
    pm = PatchManager()

    persons = make_patch('persons', 'script',
                         dict(language='test'))
    pm['persons'] = persons

    addresses = make_patch('addresses', 'script',
                           dict(language='test',
                                depends='persons'))
    pm['addresses'] = addresses

    migration = make_patch('migration', 'script',
                           dict(language='test',
                                depends=('customers@2', 'persons', 'addresses'),
                                drops=('customers', 'add phone numbers to customers')))
    pm['migration'] = migration

    planner = ExecutionPlanner(pm, ctx)
    assert tuple(planner) == (
        persons,
        addresses,
    )


def test_planner_4():
    # V1

    ctx = DummyExecutionContext({})
    pm = PatchManager()

    parents = make_patch('parents', 'script',
                         dict(language='test'))
    pm['parents'] = parents

    children = make_patch('children', 'script',
                          dict(language='test',
                               depends='parents'))
    pm['children'] = children

    data = make_patch('data', 'script',
                      dict(language='test',
                           depends=('parents', 'children')))
    pm['data'] = data

    planner = ExecutionPlanner(pm, ctx)
    assert tuple(planner) == (
        parents,
        children,
        data,
    )

    # V2-bad: there is a circular dependency between migration -> counter -> migration,
    # because counter depends on "highest" revision of parents, brought by the migration

    ctx = DummyExecutionContext({'parents': 1, 'children': 1, 'data': 1})
    pm = PatchManager()

    parents = make_patch('parents', 'script',
                       dict(language='test',
                            revision=2))
    pm['parents'] = parents

    children = make_patch('children', 'script',
                        dict(language='test',
                             depends='parents'))
    pm['children'] = children

    counter = make_patch('counter', 'script',
                         dict(language='test',
                              depends=('parents', 'children')))
    pm['counter'] = counter

    migration = make_patch('migration', 'script',
                           dict(language='test',
                                depends=('parents@1', 'counter'),
                            brings='parents@2'))
    pm['migration'] = migration

    planner = ExecutionPlanner(pm, ctx)
    with pytest.raises(CycleError):
        tuple(planner)

    # V2-good: here we make the counter depends on "any" revision of parents,
    # so it can executed before the migration

    counter = make_patch('counter', 'script',
                         dict(language='test',
                              depends=('parents@*', 'children')))
    pm['counter'] = counter

    planner = ExecutionPlanner(pm, ctx)
    assert tuple(planner) == (
        counter,
        migration,
    )


def test_already_met_deps():
    ctx = DummyExecutionContext({'dep1': 1, 'dep2': 2})
    pm = PatchManager()

    dep1 = make_patch('dep1', 'script',
                      dict(language='test'))
    pm['dep1'] = dep1

    a = make_patch('a', 'script',
                   dict(language='test',
                        depends=('dep1@1', 'dep2@3')))
    pm['a'] = a

    b = make_patch('b', 'script',
                   dict(language='test',
                        depends=('dep1@1', 'dep2@2')))
    pm['b'] = b

    newdep2 = make_patch('dep2', 'script',
                         dict(language='test',
                              revision=3,
                              depends='dep1'))
    pm['dep2'] = newdep2

    planner = ExecutionPlanner(pm, ctx)
    assert tuple(planner) == (
        b,
        newdep2,
        a,
    )

    always_first = make_patch('always_first', 'script',
                              dict(language='test',
                                   always='first'))
    pm['always_first'] = always_first

    planner = ExecutionPlanner(pm, ctx)
    assert tuple(planner) == (
        always_first,
        b,
        newdep2,
        a,
    )

    always_last = make_patch('always_last', 'script',
                              dict(language='test',
                                   always='last'))
    pm['always_last'] = always_last

    planner = ExecutionPlanner(pm, ctx)
    assert tuple(planner) == (
        always_first,
        b,
        newdep2,
        a,
        always_last,
    )
