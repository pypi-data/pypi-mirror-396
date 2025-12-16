# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

  $ POSTGRES_EXPORTER=$(command -v postgres_exporter || command -v prometheus-postgres-exporter)
  $ export PGLIFT_CONFIG_DIR=$TMPDIR/$TESTFILE.conf.d
  $ mkdir $PGLIFT_CONFIG_DIR
  $ cat > $PGLIFT_CONFIG_DIR/settings.yaml <<EOF
  > cli:
  >   log_format: '%(levelname)-4s %(message)s'
  > prefix: '$TMPDIR'
  > run_prefix: '$TMPDIR/run'
  > postgresql:
  >   auth:
  >     passfile: null
  > prometheus:
  >   execpath: '$POSTGRES_EXPORTER'
  > pgbackrest:
  >   # enable pgbackrest in site configuration, but don't use it in created instance.
  >   repository:
  >     mode: path
  >     path: '$TMPDIR/pgbackrest-not-used'
  > EOF

  $ alias pglift="pglift --non-interactive --log-level=info"

  $ pglift site-configure install
  INFO creating base pgBackRest configuration directory: $TMPDIR/etc/pgbackrest
  INFO installing base pgBackRest configuration
  INFO creating pgBackRest include directory
  INFO creating pgBackRest repository backups and archive directory: $TMPDIR/pgbackrest-not-used
  INFO creating pgBackRest log directory: $TMPDIR/log/pgbackrest
  INFO creating pgBackRest spool directory: $TMPDIR/srv/pgbackrest/spool
  INFO creating PostgreSQL log directory: $TMPDIR/log/postgresql

  $ trap "pglift --non-interactive site-configure uninstall; \
  >     port-for -u pg1; \
  >     port-for -u pg2; \
  >     port-for -u pge1; \
  >     port-for -u pge2" \
  >     EXIT

With custom ports

  $ PG1PORT=$(port-for pg1)
  $ PG2PORT=$(port-for pg1)
  $ PGE1PORT=$(port-for pge1)
  $ PGE2PORT=$(port-for pge2)
  $ pglift instance create main --port=$PG1PORT --prometheus-port=$PGE1PORT
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/run/postgresql
  INFO starting PostgreSQL 1\d\/main (re)
  INFO creating role 'prometheus'
  INFO configuring Prometheus postgres_exporter 1\d-main (re)
  INFO creating instance dumps directory: \$TMPDIR\/srv\/dumps\/1\d-main (re)
  INFO starting Prometheus postgres_exporter 1\d-main (re)
  $ pglift instance create other --port=$PG2PORT --prometheus-port=$PGE1PORT
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--prometheus-port': port \d+ already in use (re)
  [2]
  $ pglift instance create other --port=$PG1PORT --prometheus-port=$PGE2PORT
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--port': port \d+ already in use (re)
  [2]
  $ pglift instance create other --port=$PG1PORT --prometheus-port=$PGE1PORT
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--prometheus-port': port \d+ already in use (re)
  [2]
  $ pglift instance drop main
  INFO dropping instance 1\d\/main (re)
  INFO stopping PostgreSQL 1\d\/main (re)
  INFO stopping Prometheus postgres_exporter 1\d-main (re)
  INFO deconfiguring Prometheus postgres_exporter 1\d-main (re)
  INFO deleting PostgreSQL data and WAL directories

With a port set in postgresql.conf template

  $ mkdir $PGLIFT_CONFIG_DIR/postgresql
  $ cat > $PGLIFT_CONFIG_DIR/postgresql/postgresql.conf <<EOF
  > port=$PG2PORT
  > unix_socket_directories=$TMPDIR
  > EOF

  $ pglift instance create main --prometheus-port=$PGE1PORT
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO starting PostgreSQL 1\d\/main (re)
  INFO creating role 'prometheus'
  INFO configuring Prometheus postgres_exporter 1\d-main (re)
  INFO creating instance dumps directory: \$TMPDIR\/srv\/dumps\/1\d-main (re)
  INFO starting Prometheus postgres_exporter 1\d-main (re)
  $ pglift instance create other --prometheus-port=$PGE2PORT
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--port': port \d+ already in use (re)
  [2]
  $ pglift instance create other --port=$PG2PORT --prometheus-port=$PGE1PORT
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--prometheus-port': port \d+ already in use (re)
  [2]

  $ pglift instance drop main
  INFO dropping instance 1\d\/main (re)
  INFO stopping PostgreSQL 1\d\/main (re)
  INFO stopping Prometheus postgres_exporter 1\d-main (re)
  INFO deconfiguring Prometheus postgres_exporter 1\d-main (re)
  INFO deleting PostgreSQL data and WAL directories
  $ rm -rf $PGLIFT_CONFIG_DIR/postgresql

With default ports

  $ pglift instance create main
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO starting PostgreSQL 1\d\/main (re)
  INFO creating role 'prometheus'
  INFO configuring Prometheus postgres_exporter 1\d-main (re)
  INFO creating instance dumps directory: \$TMPDIR\/srv\/dumps\/1\d-main (re)
  INFO starting Prometheus postgres_exporter 1\d-main (re)
  $ pglift instance create other
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--port': port 5432 already in use
  [2]

  $ pglift instance drop main
  INFO dropping instance 1\d\/main (re)
  INFO stopping PostgreSQL 1\d\/main (re)
  INFO stopping Prometheus postgres_exporter 1\d-main (re)
  INFO deconfiguring Prometheus postgres_exporter 1\d-main (re)
  INFO deleting PostgreSQL data and WAL directories

(cleanup)
  INFO deleting pgBackRest include directory
  INFO uninstalling base pgBackRest configuration
  INFO deleting pgBackRest log directory
  INFO deleting pgBackRest spool directory
  INFO deleting PostgreSQL log directory
  INFO deleting PostgreSQL socket directory (no-eol)
