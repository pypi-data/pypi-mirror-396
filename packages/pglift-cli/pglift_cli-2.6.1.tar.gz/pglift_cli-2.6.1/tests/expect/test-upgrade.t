# SPDX-FileCopyrightText: 2023 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

Test instance upgrade, along with local "password" authentication without a
.pgpass nor a password_command.

Site settings:

  $ export PGLIFT_CONFIG_DIR="$TMPDIR/$TESTFILE.conf.d"
  $ mkdir $PGLIFT_CONFIG_DIR
  $ cat > $PGLIFT_CONFIG_DIR/settings.yaml <<EOF
  > cli:
  >   log_format: '%(levelname)-4s %(message)s'
  > prefix: '$TMPDIR'
  > run_prefix: '$TMPDIR/run'
  > postgresql:
  >   auth:
  >     passfile: null
  > EOF

  $ pglift site-settings -o json | jq '.run_prefix, .prefix'
  "$TMPDIR/run"
  "$TMPDIR"

  $ alias pglift="pglift --non-interactive --log-level=info"

  $ pglift site-configure install
  INFO creating PostgreSQL log directory: $TMPDIR/log/postgresql

  $ trap "pglift --non-interactive instance drop old new; \
  >   pglift --non-interactive site-configure uninstall; \
  >   port-for -u pg1; \
  >   port-for -u pg2" \
  >   EXIT

Define ports:

  $ PG1PORT=$(port-for pg1)
  $ PG2PORT=$(port-for pg2)

Create an instance with "password" local authentication method, and upgrade it:

  $ pglift instance create old --port=$PG1PORT --auth-local=scram-sha-256 --surole-password=s3kret
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/run/postgresql
  INFO starting PostgreSQL 1\d\/old (re)
  INFO creating instance dumps directory: \$TMPDIR\/srv\/dumps\/1\d-old (re)
  $ pglift instance upgrade old --name=new --port=$PG2PORT -- --jobs=3
  Error: instance is running
  [1]
  $ pglift instance stop old
  INFO stopping PostgreSQL 1\d\/old (re)
  $ env PGPASSWORD=s3kret pglift --non-interactive -Linfo instance upgrade old --name=new --port=$PG2PORT -- --jobs=3 --link
  INFO upgrading instance 1\d\/old as 1\d\/new (re)
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO upgrading instance with pg_upgrade
  INFO configuring PostgreSQL
  INFO creating instance dumps directory: \$TMPDIR\/srv\/dumps\/1\d-new (re)
  INFO starting PostgreSQL 1\d\/new (re)

(cleanup)
  INFO dropping instance 1\d\/old (re)
  WARNING instance 1\d\/old is already stopped (re)
  INFO deleting PostgreSQL data and WAL directories
  INFO dropping instance 1\d\/new (re)
  INFO stopping PostgreSQL 1\d\/new (re)
  INFO deleting PostgreSQL data and WAL directories
  INFO deleting PostgreSQL log directory
  INFO deleting PostgreSQL socket directory (no-eol)
