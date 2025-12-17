.. -*- coding: utf-8 -*-
.. :Project:   PatchDB
.. :Created:   Sat Aug 22 16:19:15 2009 +0000
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2009, 2010, 2012-2018, 2021, 2023 Lele Gaifax
..

=============================
 metapensiero.sphinx.patchdb
=============================

Collects and applies scripts embedded in a reST document
========================================================

:version: 4
:author: Lele Gaifax <lele@metapensiero.it>
:license: GPLv3

Building and maintaining the schema of a database is always a challenge. It may quickly become
a nightmare when dealing with even moderately complex databases, in a distributed development
environment. You have new features going in, and fixes here and there, that keeps accumulating
in the development `branch`. You also have several already deployed instances of the database
you wanna upgrade now and then.

In my experience, it's very difficult to impossible to come up with a completely automated
solution, for several reasons:

* comparison between different releases of a database schema is tricky

* actual contents of the database must be preserved

* some changes require specific recipes to upgrade the data

* any automated solution hides some detail, by definition: I need complete control, to be able
  to create temporary tables and/or procedures for example

I tried, and wrote myself, several different approaches to the problem\ [*]_, and this package
is my latest and most satisfying effort: it builds on top of `docutils`_ and `Sphinx`_, with
the side advantage that you get a quite nice and good documentation of the whole architecture:
`literate database scheming`!

.. _docutils: http://docutils.sourceforge.net/
.. _sphinx: http://sphinx.pocoo.org/intro.html

.. important:: Version 4 requires Python 3.9 or higher, and psycopg 3 to talk with PostgreSQL!

.. contents::

.. [*] Just to mention a few alternatives:

       `Alembic <https://pypi.python.org/pypi/alembic>`_
         Written on top of SQLAlchemy_ by the same author: it does not help when you need to
         manage something outside SA knowledge (stored procedures, permissions, …)

       `Pyrseas <https://pyrseas.readthedocs.io/en/latest/>`_
         ``PostgreSQL`` specific tool, able to distill an ``SQL`` script comparing between a ``YAML``
         description of the schema and the actual one: interesting project, but does not handle
         *data* migration

       `Sqlibrist <https://pypi.python.org/pypi/sqlibrist>`_
         Some similarities with PatchDB, very young, Django integration.

       `Sqitch <http://sqitch.org/>`_
         Quite good, *although* Perl based…

       See the `schema migration <https://en.wikipedia.org/wiki/Schema_migration>`_ page on
       Wikipedia for further details.

----

How it works
------------

The package contains two distinct pieces: a `Sphinx`_ extension and the ``patchdb`` command
line tool.

The extension implements a new `ReST` directive able to embed a `script` in the document: when
processed by the ``sphinx-build`` tool, all the scripts will be collected in an external file,
configurable.

The ``patchdb`` tool takes that scripts collection and determines which scripts need to be
applied to some database, and the right order.

It creates and maintains a single very simple table within the database (unsurprisingly named
``patchdb``), where it records the last version each script it successfully execute, so that it
won't reexecute the same script (actually, a particular `revision` of it) twice: more
technically each record of the table tells *when* a particular `revision` of a `patchid` had
been applied.

So, on the development side you simply write (and document!) each piece, and when it comes the
time of deploying current state you distribute just the script collection (a single file,
usually in `JSON`_ format, or a ``pickle`` archive, see `storage formats`_ below) to the end
points where the database instances live, and execute ``patchdb`` against each one.

.. _json: http://json.org/


Scripts
~~~~~~~

The basic building block is a `script`, an arbitrary sequence of statements written in some
language (currently, either ``Python``, ``SQL`` or ``Shell``), augmented with some metadata
such as the `scriptid`, possibly a longer `description`, its `revision` and so on.

The `scriptid` is a required single line of text, and is whatever comes after the ``script``
directive: it cannot be longer than 100 characters and must not contain the ``@`` character.

The `description` may be arbitrarily long, and is used only for documentation purposes.

The `revision` is a non-negative integer, and when omitted defaults to 1.

As a complete example of the syntax, consider the following::

  .. patchdb:script:: My first script
     :description: Full example of a script
     :revision: 2
     :depends: Other script@4
     :preceeds: Yet another
     :language: python
     :conditions: python_2_x

     print "Yeah!"

This will introduce a script globally identified by `My first script`, written in ``Python``:
this is its second release, and its execution must be constrained such that it happens
**after** the execution of the fourth revision of `Other script` and **before** `Yet another`.

The sequence of statements may be specified either as the *content* of the directive **or**
loaded from an external file, so the previous script could be written as::

  .. patchdb:script:: My first script
     :description: Full example of a script
     :revision: 2
     :depends: Other script@4
     :preceeds: Yet another
     :language: python
     :conditions: python_2_x
     :file: python_script.py

``SQL`` scripts may be composed by multiple statements, separated by a standalone ``;;``
marker, as in::

  .. patchdb:script:: Create and populate

     CREATE TABLE foo (id integer, value varchar(20))
     ;;
     INSERT INTO foo (id, value) VALUES (1, 'bar')

Another special marker is ``;;INCLUDE:``, that can be used to include the content of an
external file, more flexibly than with the ``file`` option above. The previous example could be
written as::

  .. patchdb:script:: Create and populate

     ;;INCLUDE: create_table.sql
     ;;
     ;;INCLUDE: populate_table.sql

where the two statements are loaded respectively from ``create_table.sql`` and
``populate_table.sql``. The ``;;INCLUDE:`` marker is expanded recursively, so that another way
to say the very same thing is::

  .. patchdb:script:: Create and populate

     ;;INCLUDE: create_and_populate.sql

with ``create_and_populate.sql`` containing::

  ;;INCLUDE: create_table.sql
  ;;
  ;;INCLUDE: populate_table.sql

As another concrete example where this can be very useful, consider the case when you need to
replace an existing function with one having a different signature for the output parameters,
something that for example PostgreSQL does not allow. You could then say::

  .. patchdb:script:: Some function
     :revision: 2
     :file: some_function.sql

  .. patchdb:script:: Upgrade some function to revision 2
     :depends: Some function@1
     :brings: Some function@2

     DROP FUNCTION some_function(int, OUT int)
     ;;
     ;;INCLUDE: some_function.sql

A particular case is when you actually need to *replace* something with something else, for
example instead of upgrading the function above you want to replace it entirely. This is when
the ``replaces`` option comes handy: it is almost equivalent to the ``depends`` option, except
that it is not an error when an item specified with the former does not exist::

  .. patchdb:script:: Some other function
     :file: some_other_function.sql

  .. patchdb:script:: Replace some function with a different one
     :replaces: Some function@1
     :brings: Some other function@1

     DROP FUNCTION IF EXISTS some_function(int, OUT int)
     ;;
     ;;INCLUDE: some_other_function.sql


Conditions
++++++++++

The example shows also an usage of the conditions, allowing more than one variant of a script
like::

  .. patchdb:script:: My first script (py3)
     :description: Full example of a script
     :revision: 2
     :depends: Other script@4
     :preceeds: Yet another
     :language: python
     :conditions: python_3_x

     print("Yeah!")

The value of the ``:conditions:`` option may be a single paragraph, containing a comma
separated list of conditions, or alternatively a `bullet list`_.

.. _bullet list:
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bullet-lists

As another use case of this feature, the following snippet declares the same table for two
different databases::

  .. patchdb:script:: Simple table (PostgreSQL)
    :language: sql
    :mimetype: text/x-postgresql
    :conditions: postgresql
    :file: postgresql/simple.sql

  .. patchdb:script:: Simple table (MySQL)
    :language: sql
    :mimetype: text/x-mysql
    :conditions: mysql
    :file: mysql/simple.sql

As you can see, the content of the script can be conveniently stored in an external file, and
the particular dialect specified with the ``:mimetype:`` option, so it will be properly
highlighted by Pygments.

Such conditions may also be arbitrarily defined on the command line, so you can have for
example::

  .. patchdb:script:: Configure for production
    :language: sql
    :conditions: PRODUCTION

    UPDATE configuration SET is_production = true

and then add the option ``--assert PRODUCTION`` when it is the case.

A condition can be `negated`, prepending a ``!`` to its name::

  .. patchdb:script:: Configure for production
    :language: sql
    :conditions: !PRODUCTION

    UPDATE configuration SET is_production = false


Variables
+++++++++

Another way to influence a script effect is by using *variables*: a script may contain one or
more references to arbitrary variables using the syntax ``{{VARNAME}}``, that **must** be
defined at application time, using the ``--define VARNAME=VALUE`` command line option.
Alternatively with the syntax ``{{name=default}}`` the reference can set the default value for
the variable, that can be overridden from the command line.

As an example, you can have the following script::

  .. patchdb:script:: Create table and give read-only rights to the web user
     :language: sql

     CREATE TABLE foo (id INTEGER)
     ;;
     GRANT SELECT ON TABLE foo TO {{WEB=www}}
     ;;
     GRANT ALL ON TABLE foo TO {{ADMIN}}

To apply it, you must specify the value for the ``ADMIN`` variable, with something like
``--define ADMIN=$USER``.

The variable name must be an *identifier* (that is, at least an alphabetic letter possibly
followed by alphanumerics or underscores), while its value may contain whitespaces, letters or
digits.

If the name starts with ``ENV_``, the value is looked up in the process `environment`. In the
following example, the name of the user is taken from the the ``USER`` environment variable
(that must be present), while the password comes from the ``PASSWORD`` environment entry or, if
not set, from the specified default::

  .. patchdb:script:: Insert a default user name
     :language: sql

     INSERT INTO users (name, password) VALUES ('{{ENV_USER}}', '{{ENV_PASSWORD=password}}')

Note that you can override the environment using an explicit ``--define`` option on the command
line, for example with ``--define ENV_PASSWORD=foobar``.


Dependencies
++++++++++++

.. _master-table:

The dependencies (that is, the *options* ``:brings:``, ``:depends:``, ``:drops:``,
``:preceeds:`` and ``:replaces:``) may be a paragraph containing a comma separated list of
script ids, such as::

  .. patchdb:script:: Create master table

     CREATE TABLE some_table (id INTEGER PRIMARY KEY, tt_id INTEGER)

  .. patchdb:script:: Create target table

     CREATE TABLE target_table (id INTEGER PRIMARY KEY)

  .. patchdb:script:: Add foreign key to some_table
     :depends: Create master table, Create target table

     ALTER TABLE some_table
           ADD CONSTRAINT fk_master_target
               FOREIGN KEY (tt_id) REFERENCES target_table (id)

.. warning:: This implies that the referenced ``scriptid``\ s **cannot** include a comma.

Alternatively, they can be entered as a `bullet list`_, so the last script above can be written
also as::

  .. patchdb:script:: Add foreign key to some_table
     :depends:
        - Create master table
        - Create target table

     ALTER TABLE some_table
           ADD CONSTRAINT fk_master_target
               FOREIGN KEY (tt_id) REFERENCES target_table (id)

With this syntax you can reference a ``scriptid`` containing a comma.

Independently from the order these scripts appear in the documentation, the third script will
execute only after the first two are successfully applied to the database. As you can notice,
most of the options are optional: by default, ``:language:`` is ``sql``, ``:revision:`` is
``1``, the ``:description:`` is taken from the title (that is, the script ID), while
``:depends:`` and ``:preceeds:`` are empty.

Just for illustration purposes, the same effect could be achieved with::

  .. patchdb:script:: Create master table
     :preceeds: Add foreign key to some_table

     CREATE TABLE some_table (id INTEGER PRIMARY KEY, tt_id INTEGER)

  .. patchdb:script:: Create target table

     CREATE TABLE target_table (id INTEGER PRIMARY KEY)

  .. patchdb:script:: Add foreign key to some_table
     :depends: Create target table

     ALTER TABLE some_table
           ADD CONSTRAINT fk_master_target
               FOREIGN KEY (tt_id) REFERENCES target_table (id)


Errors handling
+++++++++++++++

By default ``patchdb`` stops when it fails to apply one script. Some time you may want to relax
that rule, for example when operating on a database that was created with other methods so you
cannot relay on the existence of a specific script to make the decision. In such cases, the
option ``:onerror:`` may be used::

  .. patchdb:script:: Remove obsoleted tables and functions
     :onerror: ignore

     DROP TABLE foo
     ;;
     DROP FUNCTION initialize_record_foo()

When ``:onerror:`` is set to `ignore`, each statement in the script is executed and if an error
occurs it is ignored and ``patchdb`` proceeds with the next one. On good databases like
PostgreSQL and SQLite where even DDL statements are transactional, each statement is executed
in a nested subtransaction, so subsequent errors do not ruin the effect of correctly applied
previous statements.

Another possible setting of this option is `skip`: in this case, whenever an error occurs the
effect of the whole script is undone and it is considered as applied. For example, assuming
that the old version of ``SomeProcedure`` accepted a single argument and the new one requires
two of them, you could do something like the following::

  .. patchdb:script:: Fix stored procedure signature
     :onerror: skip

     SELECT somecol FROM SomeProcedure(NULL, NULL)
     ;;
     ALTER PROCEDURE SomeProcedure(p_first INTEGER, p_second INTEGER)
     RETURNS (somecol INTEGER) AS
     BEGIN
       somecol = p_first * p_second;
       SUSPEND;
     END


Patches
~~~~~~~

A `patch` is a particular flavour of script, one that specifies a `brings`, a `drops` or a
`replaces` dependency list. Imagine that the `example above`__ was the first version of the
database, and that the current version looks like the following::

  .. patchdb:script:: Create master table
     :revision: 2

     CREATE TABLE some_table (
       id INTEGER PRIMARY KEY,
       description VARCHAR(80),
       tt_id INTEGER
     )

that is, ``some_table`` now contains one more field, ``description``.

We need an upgrade path from the first revision of the table to the second::

  .. patchdb:script:: Add a description to the master table
     :depends: Create master table@1
     :brings: Create master table@2

     ALTER TABLE some_table ADD COLUMN description VARCHAR(80)

When ``patchdb`` examines the database status, it will execute one *or* the other. If the
script `Create master table` isn't executed yet (for example when operating on a new database),
it will take the former script (the one that creates the table from scratch).  Otherwise, if
the database "contains" revision 1 (and not higher than 1) of the script, it will execute the
latter, bumping up the revision number.

.. note:: Any single dependency may be either `generic` or `pinned` to a particular `revision`
          number.

          A generic dependency is one that does not contain a ``@`` character followed by an
          integer number: in this case ``patchdb`` will consider it pointing to the *highest*
          known revision of that script.

          A pinned dependency contains the ``@``: what follows may be either a revision number
          or, **only** for the `depends` ones, the character ``*``, to indicate that any
          revision is good enough, provided it has been applied. In other words, the asterisk
          will be replaced by the current revision of the script if it has been already
          applied, otherwise by its highest known revision, i.e. handled in the same way as an
          unpinned dependency.

__ master-table_


Obsoleted patches
+++++++++++++++++

Another peculiarity of this kind of scripts is that they may references `non existing scripts`
without producing warnings or errors.

The rationale is that in the database evolution a given script may be removed, possibly
replaced by a different one by some succeeding patch. Consider the case when you once had a
table called ``customers``::

  .. patchdb:script:: Create table customers
     :revision: 2

     CREATE TABLE customers (
       id SERIAL PRIMARY KEY,
       name VARCHAR(80),
       street_address VARCHAR(80),
       city VARCHAR(80),
       telephone_number VARCHAR(80)
     )

  .. patchdb:script:: Add telephone number to customers table
     :depends: Create table customers@1
     :brings: Create table customers@2

     ALTER TABLE customers ADD COLUMN telephone_number VARCHAR(80)

and then the need for multiple addresses arose thus you decided to split it in two distinct
relations, a ``persons`` and a ``person_addresses``::

  .. patchdb:script:: Create table persons

     CREATE TABLE persons (
       id SERIAL PRIMARY KEY,
       name VARCHAR(80)
     )

  .. patchdb:script:: Create table person_addresses
     :depends: Create table persons

     CREATE TABLE person_addresses (
       id SERIAL PRIMARY KEY,
       person_id INTEGER REFERENCES persons (id),
       street_address VARCHAR(80),
       city VARCHAR(80),
       telephone_number VARCHAR(80)
     )

  .. patchdb:script:: Migrate from customers to persons and person_addresses
     :replaces: Create table customers@2
     :depends:
        - Create table persons
        - Create table person_addresses
     :drops:
        - Create table customers
        - Add telephone number to customers table

     INSERT INTO persons (id, name) SELECT id, name FROM customers
     ;;
     INSERT INTO person_addresses (person_id, street_address, city, telephone_number)
       SELECT id, street_address, city, telephone_number
       FROM customers
     ;;
     DROP TABLE customers

At that point the script that introduced the original ``customers`` table disappeared from the
documentation, but you most probably want to keep the migration patch around for a while, at
least until you are sure all your production databases got upgraded.

.. hint:: In the HTML output, missing dependencies such as the ``"Create table customers"``
          above are marked with a ``strike`` class. In order to actually get a visual effect
          you need to define the ``CSS`` style for that, for example putting the following in
          the Sphinx configuration::

            html_context = {
                'css_files': [
                    '_static/theme_overrides.css',
                ],
            }

          and something like

          ::

            span.strike {
              text-decoration: line-through;
            }

          in ``_static/theme_overrides.css``.


Run-always scripts
~~~~~~~~~~~~~~~~~~

Yet another variant of scripts, which get applied always, **every time** ``patchdb`` is
executed.  This kind may be used to perform arbitrary operations, either at the start or at the
end of the ``patchdb`` session::

  .. patchdb:script:: Say hello
     :language: python
     :always: first

     print("Hello!")

  .. patchdb:script:: Say goodbye
     :language: python
     :always: last

     print("Goodbye!")


Fake data domains
+++++++++++++++++

As a special case that uses this kind of script, the following example illustrate an
`approximation` of the `data domains` with MySQL, that lacks them::

  .. patchdb:script:: Define data domains (MySQL)
     :language: sql
     :mimetype: text/x-mysql
     :conditions: mysql
     :always: first

     CREATE DOMAIN bigint_t bigint
     ;;
     CREATE DOMAIN `Boolean_t` char(1)

  .. patchdb:script:: Create some table (MySQL)
     :language: sql
     :mimetype: text/x-mysql
     :conditions: mysql
     :always: first

     CREATE TABLE `some_table` (
         `ID` bigint_t NOT NULL,
       , `FLAG` `Boolean_t`

       , PRIMARY KEY (`ID`)
     )

.. warning:: This is just a dirty hack, based on relatively simple search and replace: don't
             take it seriously, use a better database if you really need `data domains`!

.. note:: This works also with SQLite.


Placeholders
~~~~~~~~~~~~

Another feature is that the definition of the database, that is the collection of the scripts
that actually define its schema, may be splitted on multiple Sphinx environments: the use case
is when you have a complex application, composed by multiple modules, each of them requiring
its own set of DB objects.

A script is considered a `placeholder` when it has an empty body: it won't be ever applied, but
instead its presence in the database will be asserted. In this way, one Sphinx environment
could contain the following script::

  .. patchdb:script:: Create table a

     CREATE TABLE a (
         id INTEGER NOT NULL PRIMARY KEY
       , value INTEGER
     )

and another documentation set could extend that with::

  .. patchdb:script:: Create table a
     :description: Place holder

  .. patchdb:script:: Create unique index on value
     :depends: Create table a

     CREATE UNIQUE INDEX on_value ON a (value)

The second set can be applied **only** after the former one is.


Usage
-----

Collecting patches
~~~~~~~~~~~~~~~~~~

To use it, first of all you must register the extension within the Sphinx environment, adding
the full name of the package to the ``extensions`` list in the file ``conf.py``, for example::

  # Add any Sphinx extension module names here, as strings.
  extensions = ['metapensiero.sphinx.patchdb']

The other required bit of customization is the location of the `on disk scripts storage`,
i.e. the path of the file that will contain the information about every found script: this is
kept separated from the documentation itself because you will probably deploy it on production
servers just to update their database.

.. _storage formats:

.. topic:: Storage formats

   If the filename ends with ``.json`` it will contain a ``JSON`` formatted array otherwise it
   will be a Python ``pickle``. I usually prefer ``JSON`` because it's more VCs friendly and
   open to human inspection.

The location may be set in the same ``conf.py`` as above, like::

  # Location of the external storage
  patchdb_storage = '…/dbname.json'

Otherwise, you can set it using the ``-D`` option of the ``sphinx-build`` command, so that you
can easily share its definition with other rules in a ``Makefile``. I usually put the following
snippet at the beginning of the ``Makefile`` created by ``sphinx-quickstart``::

  TOPDIR ?= ..
  STORAGE ?= $(TOPDIR)/database.json

  SPHINXOPTS = -D patchdb_storage=$(STORAGE)

At this point, executing the usual ``make html`` will update the scripts archive: that file
contains everything is needed to update the database either local or remote; in other words,
running Sphinx (or even having it installed) is **not** required to update a database.


Updating the database
~~~~~~~~~~~~~~~~~~~~~

The other side of the coin is managed by the ``patchdb`` tool, that digests the scripts archive
and is able to determine which of the scripts are not already applied and eventually executes
those, in the right order. It does that performing the following steps:

1. load the scripts from one or more archives specified on the command line
2. discard not-applicable scripts, for example those with a non-met condition, or already
   applied ones
3. reorder remaining scripts honoring their relative dependencies, giving priority to the
   patches_
4. apply them one after the other, storing a new record in the ``patchdb`` table at each
   successful execution; if the executed script was actually a patch, *prune* the set of
   pending scripts, accordingly to the new state *brought* by the patch

You can inspect what will be done, that is obtain the list of not already applied patches, with
a command like::

  patchdb --dry-run --postgresql "dbname=test" database.json

The `database.json` archive can be sent to the production machines (in some cases I put it in a
*production* branch of the repository and use the version control tool to update the remote
machines, in other I simply used ``scp`` or ``rsync`` based solutions). Another way is to
include it in some package and then use the syntax ``some.package:path/database.json``.

The scripts may even come from several different archives (see `placeholders`_ above)::

  patchdb --postgresql "dbname=test" app.db.base:pdb.json app.db.auth:pdb.json


Bootstrapping an existing database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When your database does already exist and you are just starting using ``patchdb``, the first
thing you must do is to write a Sphinx documentation containing the scripts that recreate the
*status-quo*: on one extreme there may be a single gargantuan script with the whole schema, on
the other end you may split it up and actually document each object, properly linking each
other to build the dependency graph.

At that point, you can force the initial state with the following command::

  patchdb --assume-already-applied --postgresql "dbname=test" database.json

that will just update the ``patchdb`` table registering current revision of all the missing
scripts, without executing them.


Automatic backup
~~~~~~~~~~~~~~~~

In particular in development mode, I find it useful to have a simple way of going back to a
previous state and retry the upgrade, either to test different upgrade paths or to fix silly
typos in the new patches.

Since version 2.3 ``patchdb`` has a new option, ``--backups-dir``, that controls an automatic
backup facility: at each execution, before proceeding with applying missing patches,
*regardless* whether there are any, by default it takes a backup of the current database and
keeps a simple index of these snapshots.

The option defaults to the system-wide temporary directory (usually ``/tmp`` on POSIX systems):
if you you don't need the automatic backup (a reasonable production system should have a
different approach to taking such snapshots), specify ``None`` as argument to the option.

With the ``patchdb-states`` tool you obtain a list of the available snapshots, or restore any
previous one::

  $ patchdb-states list
  [lun 18 apr 2016 08:24:48 CEST] bc5c5527ece6f11da529858d5ac735a8 <create first table@1>
  [lun 18 apr 2016 10:27:11 CEST] 693fd245ad9e5f4de0e79549255fbd6e <update first table@1>

  $ patchdb-states restore --sqlite /tmp/quicktest.sqlite 693fd245ad9e5f4de0e79549255fbd6e
  [I] Creating patchdb table
  [I] Restored SQLite database /tmp/quicktest.sqlite from /tmp/693fd245ad9e5f4de0e79549255fbd6e

  $ patchdb-states clean -k 1
  Removed /tmp/bc5c5527ece6f11da529858d5ac735a8
  Kept most recent 1 snapshot


Supported databases
~~~~~~~~~~~~~~~~~~~

``patchdb`` can operate on the following databases:

* Firebird (requires fdb_)
* MySQL (requires PyMySQL_ by default, see option ``--driver`` to select a different one)
* PostgreSQL (requires psycopg_ 3)
* SQLite (uses the standard library ``sqlite3`` module)

.. _fdb: https://pypi.python.org/pypi/fdb
.. _PyMySQL: https://pypi.python.org/pypi/PyMySQL
.. _psycopg: https://pypi.python.org/pypi/psycopg
.. _SQLAlchemy: http://www.sqlalchemy.org/


Example development Makefile snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following is a snippet that I usually put in my outer ``Makefile``::

  export TOPDIR := $(CURDIR)
  DBHOST := localhost
  DBPORT := 5432
  DBNAME := dbname
  DROPDB := dropdb --host=$(DBHOST) --port=$(DBPORT) --if-exists
  CREATEDB := createdb --host=$(DBHOST) --port=$(DBPORT) --encoding=UTF8
  STORAGE := $(TOPDIR)/$(DBNAME).json
  DSN := host=$(DBHOST) port=$(DBPORT) dbname=$(DBNAME)
  PUP := patchdb --postgresql="$(DSN)" --log-file=$(DBNAME).log $(STORAGE)

  # Build the Sphinx documentation
  doc:
          $(MAKE) -C doc STORAGE=$(STORAGE) html

  $(STORAGE): doc

  # Show what is missing
  missing-patches: $(STORAGE)
          $(PUP) --dry-run

  # Upgrade the database to the latest revision
  database: $(STORAGE)
          $(PUP)

  # Remove current database and start from scratch
  scratch-database:
          $(DROPDB) $(DBNAME)
          $(CREATEDB) $(DBNAME)
          $(MAKE) database


Quick example
-------------

The following shell session illustrates the basics:

.. code-block:: shell

   python3 -m venv patchdb-session
   cd patchdb-session
   source bin/activate
   pip install metapensiero.sphinx.patchdb[dev]
   yes n | sphinx-quickstart --project PatchDB-Quick-Test \
                             --author JohnDoe \
                             -v 1 --release 1 \
                             --language en \
                             --master index --suffix .rst \
                             --makefile --no-batchfile \
                             pdb-qt
   cd pdb-qt
   echo "extensions = ['metapensiero.sphinx.patchdb']" >> conf.py
   echo "patchdb_storage = 'pdb-qt.json'" >> conf.py
   echo "
   .. patchdb:script:: My first script
      :depends: Yet another
      :language: python

      print('world!')

   .. patchdb:script:: Yet another
      :language: python

      print('Hello')
   " >> index.rst
   make html
   patchdb --sqlite /tmp/pdb-qt.sqlite --dry-run pdb-qt.json

At the end you should get something like::

  Would apply script "yet another@1"
  Would apply script "my first script@1"
  100% (2 of 2) |########################################| Elapsed Time: 0:00:00 Time: 0:00:00

Removing the ``--dry-run``::

  $ patchdb --sqlite /tmp/pdb-qt.sqlite pdb-qt.json
  Hello
  world!

  Done, applied 2 scripts
  100% (2 of 2) |########################################| Elapsed Time: 0:00:00 Time: 0:00:00

Once again::

  $ patchdb --sqlite /tmp/pdb-qt.sqlite pdb-qt.json
  Done, applied 0 scripts
