# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test for PatchManager
# :Created:   mer 24 feb 2016 16:37:44 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2018, 2019, 2021, 2023 Lele Gaifax
#

from os import unlink
from tempfile import mktemp

import pytest

from metapensiero.sphinx.patchdb.manager import PatchManager, PersistentPatchManager
from metapensiero.sphinx.patchdb.patch import make_patch


def test_patch__manager():
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
    pm += second

    assert pm['first'] is first
    assert pm['second'] is second


@pytest.mark.parametrize('suffix', ('.json', '.pickle'))
def test_persistent_patch_manager(suffix):
    tempfile = mktemp(suffix=suffix)
    pm = PersistentPatchManager(tempfile)
    first = make_patch('first', 'script',
                       dict(revision=1, language='test',
                            depends='second'),
                       'This patch costs € 0.1')
    pm['first'] = first
    second = make_patch('second', 'script',
                        dict(revision=2, language='test'))
    pm['second'] = second
    third = make_patch('third', 'script',
                       dict(depends='second@1',
                            preceeds='first',
                            language='test'))
    pm['third'] = third
    pm.save()
    pm.load()
    assert 'This patch costs € 0.1' == pm['first'].description
    unlink(tempfile)
