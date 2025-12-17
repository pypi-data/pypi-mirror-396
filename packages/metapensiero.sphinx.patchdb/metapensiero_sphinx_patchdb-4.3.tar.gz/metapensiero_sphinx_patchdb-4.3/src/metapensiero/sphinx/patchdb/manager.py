# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Script&Patch Manager
# :Created:   ven 14 ago 2009 13:09:28 CEST
# :Author:    Lele Gaifax <lele@nautilus.homeip.net>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2009, 2010, 2012-2018, 2021, 2023 Lele Gaifax
#

import json
import logging
from os.path import dirname, exists, relpath
import pickle


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class DuplicatedScriptError(Exception):
    "Indicates that a script is not unique."


class Missing3rdPartyModule(Exception):
    "Indicates that a 3rd party module is missing"


class PatchManager:
    """
    A dict-like collector of a set of patches.
    """

    def __init__(self):
        self.db = {}

    def __getitem__(self, patchid):
        """
        Return the patch given its `patchid`, or ``None`` if it does not exist.
        """
        return self.db.get(patchid)

    def __setitem__(self, patchid, patch):
        """
        Register the given `patch` identified by `patchid`.
        """
        self.db[patchid] = patch

    def __iadd__(self, patch):
        """
        Syntactic sugar to register the given `patch`.
        """
        self.db[patch.patchid] = patch
        return self


class PersistentPatchManager(PatchManager):
    """
    Patch manager that uses a Pickle/JSON file as its persistent storage.
    """

    def __init__(self, storage_path=None):
        super().__init__()
        if isinstance(storage_path, str):
            self.storages = [storage_path]
        else:
            self.storages = storage_path

    def _checkMissingRevisionsBump(self):
        old_db = self._load()
        if not old_db:
            return

        for patch in self.db.values():
            old = old_db.get(patch.patchid)
            if old is not None:
                if old.revision == patch.revision and old.script != patch.script:
                    logger.warning("The %s has been modified, but the revision did not", patch)

    def save(self):
        self._checkMissingRevisionsBump()

        storage_path = self.storages[0]
        if storage_path is None:
            return

        logger.debug("Writing patches to %s", storage_path)
        if storage_path.endswith('.json'):
            storage = open(storage_path, 'w', encoding='utf-8')

            # Order patches by id, both for easier lookup and to
            # avoid VCs stress

            asdicts = [self.db[sid].as_dict for sid in sorted(self.db)]
            spdir = dirname(storage_path)
            for script in asdicts:
                if script.get('source'):
                    script['source'] = relpath(script['source'], spdir)

            with open(storage_path, 'w', encoding='utf-8') as storage:
                json.dump(asdicts, storage, sort_keys=True, indent=1)
        else:
            with open(storage_path, 'wb') as storage:
                pickle.dump(list(self.db.values()), storage)

        logger.debug("Done writing patches")

    def _load(self):
        db = {}
        loaded_from = {}
        for storage_path in self.storages:
            if not exists(storage_path):
                logger.debug("Storage %s does not exist, skipping", storage_path)
                continue

            logger.debug("Reading patches from %s", storage_path)
            if storage_path.endswith('.json'):
                from .patch import make_patch

                with open(storage_path, encoding='utf-8') as storage:
                    patches = [make_patch(d['ID'], d['script'], d)
                               for d in json.load(storage)]
            else:
                with open(storage_path, 'rb') as storage:
                    patches = pickle.load(storage)

            for patch in patches:
                if patch.patchid in db:
                    existing = db[patch.patchid]
                    if not patch.script:
                        existing.depends.extend(patch.depends)
                        existing.preceeds.extend(patch.preceeds)
                    elif not existing.script:
                        db[patch.patchid] = patch
                    else:
                        logger.critical("Duplicated %s: present in %s and %s",
                                        patch, loaded_from[patch.patchid], storage_path)
                        raise DuplicatedScriptError("%s already loaded!" % patch)
                else:
                    db[patch.patchid] = patch
                loaded_from[patch.patchid] = storage_path

        logger.debug("Done reading patches")
        return db

    def load(self):
        self.db = self._load()
