# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

Site settings and configuration

  $ PASSWORDS=$TMPDIR/passwords.json
  $ cat > $PASSWORDS << 'EOF'
  > {
  >   "postgres": "s3per",
  >   "replication": "r3pl"
  > }
  > EOF

  $ export PGLIFT_CLI__LOG_FORMAT="%(levelname)-4s %(message)s"
  $ export PGLIFT_POSTGRESQL__AUTH__LOCAL=md5
  $ export PGLIFT_POSTGRESQL__AUTH__PASSFILE=null
  $ export PGLIFT_POSTGRESQL__AUTH__PASSWORD_COMMAND='["jq", "-r", ".{role}", "'$PASSWORDS'"]'
  $ export PGLIFT_POSTGRESQL__REPLROLE=replication

  $ export PGLIFT_CONFIG_DIR="$TMPDIR/$TESTFILE.conf.d"
  $ mkdir -p $PGLIFT_CONFIG_DIR/postgresql
  $ cat > $PGLIFT_CONFIG_DIR/postgresql/pg_hba.conf << 'EOF'
  > local   all             {surole}                                {auth.local}
  > local   all             all                                     {auth.local}
  > host    all             all             127.0.0.1/32            {auth.host}
  > host    all             all             ::1/128                 {auth.host}
  > local   replication     all                                     {auth.local}
  > host    replication     {replrole}      127.0.0.1/32            {auth.host}
  > host    replication     {replrole}      ::1/128                 {auth.host}
  > EOF

  $ PREFIX1=$TMPDIR/primary
  $ PREFIX2=$TMPDIR/secondary
  $ RUN_PREFIX1=$PREFIX1/run
  $ RUN_PREFIX2=$PREFIX2/run
  $ PG1PORT=$(port-for pg1)
  $ PG2PORT=$(port-for pg2)
  $ alias pglift1="env PGLIFT_PREFIX=$PREFIX1 PGLIFT_RUN_PREFIX=$RUN_PREFIX1 pglift --log-level=INFO --non-interactive"
  $ alias pglift2="env PGLIFT_PREFIX=$PREFIX2 PGLIFT_RUN_PREFIX=$RUN_PREFIX2 pglift --log-level=INFO --non-interactive"

  $ pglift1 site-configure install
  INFO creating PostgreSQL log directory: $TMPDIR/primary/log/postgresql
  $ pglift2 site-configure install
  INFO creating PostgreSQL log directory: $TMPDIR/secondary/log/postgresql

(Cleanup steps)

  $ trap "
  >     pglift1 instance drop; \
  >     pglift2 instance drop; \
  >     pglift1 site-configure uninstall; \
  >     pglift2 site-configure uninstall; \
  >     port-for -u pg1; port-for -u pg2" \
  >     EXIT

Create a primary instance

  $ cat > $TMPDIR/primary.yaml <<EOF
  > name: pg1
  > port: $PG1PORT
  > surole_password: s3per
  > replrole_password: r3pl
  > data_checksums: true
  > EOF
  $ pglift1 instance apply -f $TMPDIR/primary.yaml
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/primary/run/postgresql
  INFO starting PostgreSQL 1\d\/pg1 (re)
  INFO creating role 'replication'
  INFO creating instance dumps directory: \$TMPDIR\/primary\/srv\/dumps\/1\d-pg1 (re)

Create a standby instance

  $ pglift2 instance create pg2 \
  >   --data-checksums \
  >   --standby-for="host=$RUN_PREFIX1/postgresql port=$PG1PORT user=replication" \
  >   --standby-password=r3pl \
  >   --port=$PG2PORT \
  >   --surole-password=s3per
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/secondary/run/postgresql
  INFO starting PostgreSQL 1\d\/pg2 (re)
  INFO creating instance dumps directory: \$TMPDIR\/secondary\/srv\/dumps\/1\d-pg2 (re)

Show standby information and pause/resume WAL replay on secondary

  $ pglift2 instance get --output-format=json | jq -r '.standby.wal_replay_pause_state'
  not paused
  $ pglift2 wal pause-replay
  INFO pausing WAL replay
  $ pglift2 instance get --output-format=json | jq -r '.standby.wal_replay_pause_state'
  paused
  $ pglift2 wal resume-replay
  INFO resuming WAL replay

Try to pause/resume WAL replay on primary

  $ pglift1 wal pause-replay
  Error: 1\d\/pg1 is not a standby (re)
  [1]
  $ pglift1 wal resume-replay
  Error: 1\d\/pg1 is not a standby (re)
  [1]

(Cleanup)

  INFO dropping instance 1\d\/pg1 (re)
  INFO stopping PostgreSQL 1\d\/pg1 (re)
  INFO deleting PostgreSQL data and WAL directories
  INFO dropping instance 1\d\/pg2 (re)
  INFO stopping PostgreSQL 1\d\/pg2 (re)
  INFO deleting PostgreSQL data and WAL directories
  INFO deleting PostgreSQL log directory
  INFO deleting PostgreSQL socket directory
  INFO deleting PostgreSQL log directory
  INFO deleting PostgreSQL socket directory (no-eol)
