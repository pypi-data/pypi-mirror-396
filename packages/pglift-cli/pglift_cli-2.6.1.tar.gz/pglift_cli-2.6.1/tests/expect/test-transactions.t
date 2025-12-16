# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

Tests for transactions (revert of created objects in case of operational errors).

  $ export PGLIFT_CLI__LOG_FORMAT="%(levelname)-4s %(message)s"
  $ export PGLIFT_PREFIX=$TMPDIR
  $ export PGLIFT_RUN_PREFIX=$TMPDIR/run
  $ export PGLIFT_POSTGRESQL='{
  >       "datadir": "pgsql/{name}/data",
  >       "waldir": "pgsql/{name}/wal"
  > }'
  $ export PGLIFT_CONFIG_DIR=/dev/null

  $ trap "
  >   pglift --non-interactive instance drop; \
  >   pglift site-configure uninstall; \
  >   port-for -u pg" \
  >   EXIT

  $ PGPORT=$(port-for pg)

  $ pglift -Linfo site-configure install
  INFO creating PostgreSQL log directory: $TMPDIR/log/postgresql

Create a working instance for later use (this also checks that creating an instance "stopped" works)

  $ pglift -Linfo instance create main --port=$PGPORT --state=stopped
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/run/postgresql
  INFO starting PostgreSQL 1\d\/main (re)
  INFO stopping PostgreSQL 1\d/main (re)
  INFO creating instance dumps directory: $TMPDIR/srv/dumps/1*-main (glob)

Try to create an instance with a non-existing encoding, triggering a failure in 'initdb'

  $ pglift -Linfo instance create test --encoding=notanencoding --port=$PGPORT
  INFO initializing PostgreSQL
  WARNING Command '['*/bin/pg_ctl', 'init', '-D', '$TMPDIR/srv/pgsql/test/data', '-o', '--auth-host=trust --auth-local=trust --encoding=notanencoding --locale=C --username=postgres --waldir=$TMPDIR/srv/pgsql/test/wal']' returned non-zero exit status 1. (glob)
  WARNING reverting: initializing PostgreSQL
  INFO deleting PostgreSQL data and WAL directories
  Error: Command '['*/bin/pg_ctl', 'init', '-D', '$TMPDIR/srv/pgsql/test/data', '-o', '--auth-host=trust --auth-local=trust --encoding=notanencoding --locale=C --username=postgres --waldir=$TMPDIR/srv/pgsql/test/wal']' returned non-zero exit status 1. (glob)
  initdb: error: "notanencoding" is not a valid server encoding name
  pg_ctl: database system initialization failed
  
  The files belonging to this database system will be owned by user "*". (glob)
  This user must also own the server process.
  
  The database cluster will be initialized with locale "C".
  
  [1]

Try to create a database with a non-existing tablespace

  $ pglift -Linfo database create db --tablespace=nosuchtbspc
  INFO starting PostgreSQL 1\d\/main (re)
  INFO creating 'db' database in 1\d\/main (re)
  WARNING tablespace "nosuchtbspc" does not exist
  WARNING reverting: creating 'db' database in 1\d\/main (re)
  INFO stopping PostgreSQL 1\d\/main (re)
  Error: tablespace "nosuchtbspc" does not exist
  [1]

Try to create a database with a non-existing owner

  $ pglift -Linfo database create db --owner=nosuchowner
  INFO starting PostgreSQL 1\d\/main (re)
  INFO creating 'db' database in 1\d\/main (re)
  WARNING role "nosuchowner" does not exist
  WARNING reverting: creating 'db' database in 1\d\/main (re)
  INFO stopping PostgreSQL 1\d\/main (re)
  Error: role "nosuchowner" does not exist
  [1]

(cleanup)
  WARNING instance 1*/main is already stopped (no-eol) (glob)
