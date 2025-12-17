# -*- coding: utf-8 -*-
# :Project:   PatchDB — Execution planner
# :Created:   ven 12 mag 2023, 17:04:06
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2023, 2025 Lele Gaifax
#

from collections import defaultdict
from graphlib import TopologicalSorter
import logging

from .patch import DependencyError


logger = logging.getLogger(__name__)


class ExecutionPlanner:
    """
    Iterator over a set of patches, taking into account their relative order.
    """

    def __init__(self, manager, context):
        self.manager = manager
        self.context = context
        self.patches = self._collectPatches()
        self.constraints = self._computeConstraints()

    def _collectPatches(self):
        manager = self.manager
        context = self.context

        patches = set()
        by_pid = dict()

        logger.debug("Collecting patches...")
        for patch in manager.db.values():
            retain, reason = patch.adjustUnspecifiedRevisions(manager, context)
            if not retain:
                logger.debug(' - ignoring %s: %s', patch, reason)
            else:
                applicable, reason = patch.isApplicable(context)
                if applicable:
                    patches.add(patch)
                    by_pid[patch.patchid] = patch
                else:
                    logger.debug(' - ignoring %s: %s', patch, reason)

        drop = set()
        for patch in patches:
            if patch.is_migration:
                for pid, prev in patch.depends:
                    crev = context[pid]
                    if (crev is None
                            and len(patch.depends) == len(patch.brings) == 1
                            and pid == patch.brings[0][0]):
                        # The dependency is not currently present, but given that this is a
                        # simple patch that depends and brings different versions of that
                        # dependency, we can ignore it: surely one other script will introduce
                        # it later. This may happens when long time has passed since last
                        # upgrade and thus there are a backlog of cumulated scripts and
                        # patches.
                        logger.debug(' - ignoring %s,'
                                     ' depends on "%s@%d" but it does not exist yet',
                                     patch, pid, prev)
                        drop.add(patch)
                        break
                    if crev is not None and prev < crev:
                        logger.debug(' - ignoring %s,'
                                     ' depends on "%s@%d" but it is already at %d',
                                     patch, pid, prev, crev)
                        drop.add(patch)
                        break

                if patch in drop:
                    continue

                for pid, prev in patch.replaces:
                    if context[pid] is None:
                        logger.debug(' - ignoring %s, replaces "%s" but it is already gone',
                                     patch, pid)
                        drop.add(patch)
                        break

                if patch in drop:
                    continue

                for pid, prev in patch.drops:
                    if context[pid] is None:
                        logger.debug(' - ignoring %s, drops "%s" but it is already gone',
                                     patch, pid)
                        drop.add(patch)
                        break

                if patch in drop:
                    continue

                for pid, prev in patch.brings:
                    other = by_pid.get(pid)
                    if other is not None:
                        logger.debug(' - ignoring %s, brought by %s', other, patch)
                        drop.add(other)

        return patches - drop

    def _computeConstraints(self):
        patches = self.patches
        if not patches:
            return None

        manager = self.manager
        context = self.context

        logger.debug("Building constraints graph between %d patches...", len(patches))

        # Reverse index between a given patch and the one that brings it
        brings = {}

        # Reverse index between a given patch and those that depend on it
        depends = defaultdict(set)

        # Dependency graph for the toposort
        constraints = {}

        # Patches whose deps are already met
        immediately_appliable = set()

        # First pass, insert all patches in the constraints and collect those that are
        # immediately appliable
        for patch in patches:
            if patch.is_placeholder:
                # This is a "placeholder" patch and it has not been applied yet
                logger.critical("%s has not been applied yet", patch)
                raise DependencyError('%s has not been applied yet' % patch)

            constraints[patch] = set()

            if not patch.always:
                apply_soon = True
                for oid, orev in patch.depends:
                    crev = context[oid]
                    if crev is None or crev < orev:
                        apply_soon = False
                        break
                if apply_soon:
                    immediately_appliable.add(patch)

        # Second pass, fill in constraints for each patch
        for patch in patches:
            # Consider always-first and always-last patches
            if patch.always:
                before = patch.always == 'first'
                logger.debug(' - %s shall be executed %s all the others',
                             patch, "before" if before else "after")
                for other in patches:
                    if other is not patch and other.always != patch.always:
                        if before:
                            constraints[other].add(patch)
                        else:
                            constraints[patch].add(other)

            # Ensure this patch gets executed after the ones it depends on, and take note
            # about the patches that depend on this
            for oid, orev in patch.depends:
                crev = context[oid]
                if crev is not None and crev > orev:
                    raise DependencyError(f'The {patch} depends on "{oid}@{orev}",'
                                          f' but it is currently at {crev}')
                if crev != orev:
                    other = manager[oid]
                    if other in patches:
                        logger.debug(' - %s shall be executed after %s', patch, other)
                        constraints[patch].add(other)
                    depends[(oid, orev)].add(patch)

            # Ensure this patch gets executed after the ones it replaces, and take note
            # about the patches that depend on this
            for oid, orev in patch.replaces:
                crev = context[oid]
                if crev is not None and crev > orev:
                    raise DependencyError(f'The {patch} replaces "{oid}@{orev}",'
                                          f' but it is currently at {crev}')
                if crev != orev:
                    other = manager[oid]
                    if other in patches:
                        logger.debug(' - %s shall be executed after %s', patch, other)
                        constraints[patch].add(other)
                    depends[(oid, orev)].add(patch)

            # Ensure this patch gets executed before the ones it preceeds
            for oid, orev in patch.preceeds:
                crev = context[oid]
                if crev is not None and crev < orev:
                    raise DependencyError(f'The {patch} preceeds "{oid}@{orev}",'
                                          f' but it is currently at {crev}')
                if crev != orev:
                    other = manager[oid]
                    if other in patches:
                        logger.debug(' - %s shall be executed after %s', other, patch)
                        constraints[other].add(patch)

            # Take note about the patches brought by this one
            for oid, orev in patch.brings:
                if (oid, orev) in brings:
                    raise DependencyError(f'Multiple patches bring to "{oid}@{orev}":'
                                          f' {patch} and {brings[(oid, orev)]}')
                crev = context[oid]
                if crev is not None and crev > orev:
                    raise DependencyError(f'The {patch} brings "{oid}@{orev}",'
                                          f' but it is currently at {crev}'
                )
                brings[(oid, orev)] = patch

        # Add further constraints between patch dependencies and the one that brings them
        for p in depends:
            for patch in depends[p]:
                for d in patch.depends:
                    if d in brings:
                        other = brings[d]
                        logger.debug(' - %s shall be executed after %s', patch, other)
                        constraints[patch].add(other)

        # Fixup ordering for immediately appliable patches
        for patch in immediately_appliable:
            logger.debug(' - %s is immediately applicable', patch)
            for other in immediately_appliable:
                if other is not patch:
                    order = self._relativeOrder(patch, other)
                    if order is not None:
                        constraints[order[1]].add(order[0])

        return constraints

    def _relativeOrder(self, patch_a, patch_b):
        "Determine relative ordering for the given patches."

        a_brings = {patch_a.patchid: patch_a.revision}
        for oid, orev in patch_a.brings:
            a_brings[oid] = orev
        b_brings = {patch_b.patchid: patch_b.revision}
        for oid, orev in patch_b.brings:
            b_brings[oid] = orev
        for oid, orev in patch_a.depends:
            if oid in b_brings and b_brings[oid] > orev:
                return patch_a, patch_b
        for oid, orev in patch_a.replaces:
            if oid in b_brings and b_brings[oid] > orev:
                return patch_a, patch_b
        for oid, orev in patch_b.depends:
            if oid in a_brings and a_brings[oid] > orev:
                return patch_b, patch_a
        for oid, orev in patch_b.replaces:
            if oid in a_brings and a_brings[oid] > orev:
                return patch_b, patch_a
        return None

    def __len__(self):
        return len(self.patches)

    def __iter__(self):
        if self.constraints:
            return TopologicalSorter(self.constraints).static_order()
        else:
            return iter(self.patches)
