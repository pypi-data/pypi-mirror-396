# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Apply collected patches to a database
# :Created:   Wed Nov 12 23:10:22 2003
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2003, 2009, 2010, 2012-2017, 2019, 2021, 2022, 2023 Lele Gaifax
#

from graphlib import CycleError
from os.path import isabs
import sys

import enlighten

from .contexts import ExecutionError, get_context_from_args
from .locale import gettext as _, ngettext, setup as setup_i18n
from .manager import DuplicatedScriptError, Missing3rdPartyModule, PersistentPatchManager
from .patch import DependencyError
from .planner import ExecutionPlanner


OK, SOFTWARE, DATAERR, CONFIG, USAGE = 0, 1, 2, 3, 128


def path_spec(ps):
    if isabs(ps) or ':' not in ps:
        return ps
    pkgname, subpath = ps.split(':', 1)
    from importlib.resources import path
    return path(pkgname, subpath)


def apply_missing_patches(manager, context, options, progress):
    with context:
        try:
            count = 0
            patches = ExecutionPlanner(manager, context)
            npatches = len(patches)
            if npatches > 0:
                with progress.counter(total=npatches, desc=_('Upgrading:'), unit='script') as pbar:
                    for p in patches:
                        if p is not None:
                            count += 1
                            context.execute(p, options, manager)
                        pbar.update()
            if not options.dry_run and not options.quiet:
                print()
                print(ngettext("Done, applied %d script",
                               "Done, applied %d scripts",
                               count) % count)
            return OK
        except (DependencyError, ExecutionError) as e:
            write = sys.stderr.write
            write(_("\nError: %s") % e)
            write('\n')
            return DATAERR
        except CycleError as e:
            cycle = e.args[1]
            write = sys.stderr.write
            unapplied = set(cycle)
            errmsg = _("Error: could not apply %d scripts due to circular dependencies") % len(unapplied)
            write("\n%s\n\n" % errmsg)
            write('digraph cycle {\n')
            seen = set()
            for script in cycle:
                sid = script.patchid.replace('"', r'\"')
                srev = script.revision
                if script.depends:
                    for did, drev in script.depends:
                        did = did.replace('"', r'\"')
                        fid = f'{sid}@{srev}'
                        tid = f'{did}@{drev}'
                        if (fid, tid) not in seen:
                            write(f'  "{fid}" -> "{tid}";\n')
                            seen.add((fid, tid))
                if script.preceeds:
                    for did, drev in script.preceeds:
                        did = did.replace('"', r'\"')
                        fid = f'{did}@{drev}'
                        tid = f'{sid}@{srev}'
                        if (fid, tid) not in seen:
                            write(f'  "{fid}" -> "{tid}";\n')
                            seen.add((fid, tid))
            write('}\n')
            return DATAERR


def workhorse(args, progress):
    context = get_context_from_args(args)
    if context is None:
        print(_("You must select exactly one database with either “--postgresql”,"
                " “--firebird”, “--mysql” or “--sqlite”!"))
        return USAGE

    if args.backups_dir and args.backups_dir != 'None' and not args.dry_run:
        context.backup(args.backups_dir)

    if args.assertions:
        try:
            context.addAssertions(args.assertions)
        except ValueError as e:
            print("Invalid assertion: %s" % e)
            return CONFIG

    if args.variables:
        try:
            context.addVariables(args.variables)
        except ValueError as e:
            print(_("Invalid variable: %s") % e)
            return CONFIG

    try:
        pm = PersistentPatchManager(args.storage)
        pm.load()
    except (DuplicatedScriptError, Missing3rdPartyModule) as e:
        print(_("Error: %s") % e)
        return DATAERR

    return apply_missing_patches(pm, context, args, progress)


def main():
    import locale
    import logging
    from argparse import ArgumentParser
    from importlib import metadata

    locale.setlocale(locale.LC_ALL, '')
    setup_i18n()

    version = metadata.version('metapensiero.sphinx.patchdb')
    parser = ArgumentParser(description=_("Database script applier"))

    parser.add_argument("storage", type=path_spec, nargs='+',
                        help=_("One or more archives containing collected scripts."
                               " May be either plain file names or package relative paths"
                               " like “package.name:some/file”."))
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    parser.add_argument("--postgresql", metavar="DSN",
                        help=_("Select the PostgreSQL context. DSN is a string of the kind"
                               " “host=localhost dbname=mydb user=myself password=ouch”."))
    parser.add_argument("--firebird", metavar="DSN",
                        help=_("Select the Firebird context."))
    parser.add_argument("--sqlite", metavar="DATABASE",
                        help=_("Select the SQLite context."))
    parser.add_argument("--mysql", metavar="DBNAME",
                        help=_("Select the MySQL context."))
    parser.add_argument("-u", "--username", metavar="USER",
                        help=_("Username to log into the database."))
    parser.add_argument("-p", "--password", metavar="PASSWORD",
                        help=_("Password"))
    parser.add_argument("--host", metavar="HOSTNAME", default="localhost",
                        help=_("Host name where MySQL server runs, defaults to “localhost”."))
    parser.add_argument("--port", metavar="PORT", default=3306, type=int,
                        help=_("Port number used by the MySQL server, defaults to “3306”."))
    parser.add_argument("--charset", metavar="CHARSET", default="utf8mb4",
                        help=_("Encoding used by the MySQL driver, defaults to “utf8mb4”."))
    parser.add_argument("--driver", metavar="DRIVER", default="pymysql",
                        help=_("Driver to access MySQL, defaults to “pymysql”."))
    parser.add_argument("-l", "--log-file", metavar="FILE",
                        dest="log_path",
                        help=_("Specify where to write the execution log."))
    parser.add_argument("--assume-already-applied", default=False, action="store_true",
                        help=_("Assume missing patches are already applied, do not"
                               " re-execute them."))
    parser.add_argument("--assert", metavar="NAME", action="append", dest="assertions",
                        help=_("Introduce an arbitrary assertion usable as a pre-condition"
                               " by the scripts. NAME may be a simple string or something like"
                               " “production=true”. This option may be given multiple times."))
    parser.add_argument("--define", metavar="VAR", action="append", dest="variables",
                        help=_("Define an arbitrary variable usable as “{{VARNAME}}” within"
                               " a script. VAR must be something like “varname=value”."
                               " This option may be given multiple times."))
    parser.add_argument("-n", "--dry-run", default=False, action="store_true",
                        help=_("Don't apply patches, just list them."))
    parser.add_argument("-q", "--quiet", default=False, action="store_true",
                        help=_("Be quiet, emit only error messages."))
    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help=_("Emit debug messages."))
    parser.add_argument("-b", "--backups-dir", metavar="DIR", default=None,
                        help=_("Perform a backup of the database in directory DIR"
                               " before doing anything, that by default (or by specifying"
                               " “None”) does not happen."))

    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.WARNING if args.quiet else logging.INFO
    if args.log_path:
        logging.basicConfig(filename=args.log_path, level=level,
                            format="%(asctime)s [%(levelname).1s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    else:
        logging.basicConfig(level=level, format="[%(levelname).1s] %(message)s")

    with enlighten.get_manager(enabled=not args.quiet) as progress:
        return workhorse(args, progress)


if __name__ == '__main__':
    from sys import exit
    from traceback import print_exc

    try:
        status = main()
    except Exception:
        print_exc()
        status = SOFTWARE
    exit(status)
