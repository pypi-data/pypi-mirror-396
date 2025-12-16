# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

Two instances on localhost managed with pglift invoked with different site
settings (with custom prefix and run_prefix for each configuration) in order
to emulate different hosts. The password file is common, as well as the
pgbackrest repository path (emulating a shared storage for backup). Both
instances use the same stanza.

Site settings and configuration

  $ PASSWORDS=$TMPDIR/passwords.json
  $ cat > $PASSWORDS << 'EOF'
  > {
  >   "postgres": "s3per",
  >   "replication": "r3pl",
  >   "pgbackrest": "b@ckUp"
  > }
  > EOF

  $ export PGLIFT_CLI__LOG_FORMAT="%(levelname)-4s %(message)s"
  $ export PGLIFT_POSTGRESQL='{
  >       "auth": {
  >           "local": "md5",
  >           "passfile": null,
  >           "password_command": ["jq", "-r", ".{role}", "'$PASSWORDS'"]
  >       },
  >       "backuprole": {"name": "pgbackrest"},
  >       "replrole": "replication"
  > }'
  $ export PGLIFT_PGBACKREST='{
  >       "repository": {
  >           "mode": "path",
  >           "path": "'$TMPDIR'/test-standby-pgbackrest/backups"
  >       }
  > }'

  $ mkdir $TMPDIR/postgresql
  $ PGHBA=$TMPDIR/postgresql/pg_hba.conf
  $ cat > $PGHBA << 'EOF'
  > local   all             {surole}                                {auth.local}
  > local   all             all                                     {auth.local}
  > host    all             all             127.0.0.1/32            {auth.host}
  > host    all             all             ::1/128                 {auth.host}
  > local   replication     {replrole}                              {auth.local}
  > host    replication     {replrole}      127.0.0.1/32            {auth.host}
  > host    replication     {replrole}      ::1/128                 {auth.host}
  > EOF
  $ PGLIFT_CONFIG_DIR=$TMPDIR
  $ touch $PGLIFT_CONFIG_DIR/settings.yaml

  $ PREFIX1=$TMPDIR/1
  $ PREFIX2=$TMPDIR/2
  $ RUN_PREFIX1=$PREFIX1/run
  $ RUN_PREFIX2=$PREFIX2/run
  $ alias pglift1="env PGLIFT_CONFIG_DIR=$PGLIFT_CONFIG_DIR PGLIFT_PREFIX=$PREFIX1 PGLIFT_RUN_PREFIX=$RUN_PREFIX1 pglift --log-level=INFO --non-interactive"
  $ alias pglift2="env PGLIFT_CONFIG_DIR=$PGLIFT_CONFIG_DIR PGLIFT_PREFIX=$PREFIX2 PGLIFT_RUN_PREFIX=$RUN_PREFIX2 pglift --log-level=INFO --non-interactive"

  $ pglift1 site-configure install
  INFO creating base pgBackRest configuration directory: $TMPDIR/1/etc/pgbackrest
  INFO installing base pgBackRest configuration
  INFO creating pgBackRest include directory
  INFO creating pgBackRest repository backups and archive directory: $TMPDIR/test-standby-pgbackrest/backups
  INFO creating pgBackRest log directory: $TMPDIR/1/log/pgbackrest
  INFO creating pgBackRest spool directory: $TMPDIR/1/srv/pgbackrest/spool
  INFO creating PostgreSQL log directory: $TMPDIR/1/log/postgresql
  $ pglift2 site-configure install
  INFO creating base pgBackRest configuration directory: $TMPDIR/2/etc/pgbackrest
  INFO installing base pgBackRest configuration
  INFO creating pgBackRest include directory
  INFO creating pgBackRest log directory: $TMPDIR/2/log/pgbackrest
  INFO creating pgBackRest spool directory: $TMPDIR/2/srv/pgbackrest/spool
  INFO creating PostgreSQL log directory: $TMPDIR/2/log/postgresql

Define ports

  $ PG1PORT=$(port-for pg1)
  $ PG2PORT=$(port-for pg2)
  $ PG3PORT=$(port-for pg3)

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
  > pgbackrest:
  >   stanza: app
  >   password: b@ckUp
  > surole_password: s3per
  > replrole_password: r3pl
  > replication_slots:
  >   - slot1
  >   - slot2
  > EOF
  $ pglift1 instance apply -f $TMPDIR/primary.yaml -o json --dry-run
  {
    "change_state": null,
    "diff": null,
    "pending_restart": false
  }
  $ pglift1 instance apply -f $TMPDIR/primary.yaml
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/1/run/postgresql
  INFO starting PostgreSQL 1\d\/pg1 (re)
  INFO creating role 'replication'
  INFO creating role 'pgbackrest'
  INFO configuring pgBackRest stanza 'app' for pg1-path=\$TMPDIR\/1\/srv\/pgsql\/1\d\/pg1\/data (re)
  INFO creating pgBackRest stanza 'app'
  INFO checking pgBackRest configuration for stanza 'app'
  INFO creating instance dumps directory: \$TMPDIR\/1\/srv\/dumps\/1\d-pg1 (re)
  INFO creating replication slot 'slot1'
  INFO creating replication slot 'slot2'
  $ pglift1 instance alter --drop-slot=slot1
  INFO configuring PostgreSQL
  INFO dropping replication slot 'slot1'
  $ pglift1 instance get -o json \
  >   | jq '.name, .replication_slots, .pgbackrest'
  "pg1"
  [
    {
      "name": "slot2"
    }
  ]
  {
    "stanza": "app"
  }

Cannot create a standby with --slot option
  $ pglift2 instance create pg2 \
  >   --pgbackrest-stanza=stnz \
  >   --standby-for="host=hst" \
  >   --slot=slt
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--slot': replication slots cannot be set on a standby instance
  [2]


Modify some parameters in primary instance
  $ pglift1 pgconf -i pg1 set max_connections=150
  INFO configuring PostgreSQL
  WARNING instance 1\d\/pg1 needs restart due to parameter changes: max_connections (re)
  max_connections: None -> 150
  $ pglift1 instance restart
  INFO restarting instance 1\d\/pg1 (re)
  INFO restarting PostgreSQL
  INFO stopping PostgreSQL 1\d\/pg1 (re)
  INFO starting PostgreSQL 1\d\/pg1 (re)

Create a standby instance

  $ pglift2 instance create pg2 \
  >   --standby-for="host=$RUN_PREFIX1/postgresql port=$PG1PORT user=replication" \
  >   --standby-password=r3pl \
  >   --standby-slot=slot2 \
  >   --port=$PG2PORT --pgbackrest-stanza=app \
  >   --surole-password=s3per --pgbackrest-password=b@ckUp
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/2/run/postgresql
  INFO starting PostgreSQL 1\d\/pg2 (re)
  INFO configuring pgBackRest stanza 'app' for pg1-path=\$TMPDIR\/2\/srv\/pgsql\/1\d\/pg2\/data (re)
  INFO creating pgBackRest stanza 'app'
  WARNING not checking pgBackRest configuration on a standby
  INFO creating instance dumps directory: \$TMPDIR\/2\/srv\/dumps\/1\d-pg2 (re)

Try to create primary instance with same stanza

  $ pglift1 instance create err \
  >   --port=$PG3PORT --pgbackrest-stanza=app \
  >   --surole-password=s3per --pgbackrest-password=b@ckUp
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--pgbackrest-stanza': Stanza 'app' already bound to another instance \(datadir=\$TMPDIR\/1\/srv\/pgsql\/1\d\/pg1\/data\) (re)
  [2]

Add some data to the primary, check replication

  $ pglift1 database run -d postgres \
  >   "CREATE TABLE t AS (SELECT generate_series(1, 3) i)"
  INFO running "CREATE TABLE t AS \(SELECT generate_series\(1, 3\) i\)" on postgres database of 1\d\/pg1 (re)
  INFO SELECT 3
  $ pglift2 database run -o json -d postgres "SELECT i FROM t"
  INFO running "SELECT i FROM t" on postgres database of 1\d\/pg2 (re)
  INFO SELECT 3
  {
    "postgres": [
      {
        "i": 1
      },
      {
        "i": 2
      },
      {
        "i": 3
      }
    ]
  }
  $ pglift2 instance get -o json \
  >   | jq '.standby.slot, .standby.replication_lag, .standby.wal_sender_state, .state, .pgbackrest'
  "slot2"
  "0"
  "streaming"
  "started"
  {
    "stanza": "app"
  }

Backup the primary

  $ pglift1 instance backup
  INFO backing up instance 1\d\/pg1 with pgBackRest (re)
  $ pglift1 instance backups -o json | jq '.[] | .type, .databases'
  "full"
  [
    "postgres"
  ]
  $ pglift1 pgbackrest info --output json | jq '.[0].status.message'
  "ok"

Attempt to backup from the standby

  $ pglift2 instance backup --type=diff 2>&1 | grep ERROR
  ERROR: [056]: unable to find primary cluster - cannot proceed

Switchover

  $ pglift1 instance stop
  INFO stopping PostgreSQL 1\d\/pg1 (re)
  $ pglift2 instance promote
  INFO promoting PostgreSQL instance
  INFO checking pgBackRest configuration for stanza 'app'

  $ pglift2 database run -d postgres \
  >   "INSERT INTO t VALUES (42)"
  INFO running "INSERT INTO t VALUES \(42\)" on postgres database of 1\d\/pg2 (re)
  INFO INSERT 0 1
  $ pglift2 database run -d postgres "SELECT pg_switch_wal()" > /dev/null
  INFO running "SELECT pg_switch_wal\(\)" on postgres database of 1\d\/pg2 (re)
  INFO SELECT 1

  $ pglift2 instance get -o json \
  >   | jq '.standby.slot, .standby.replication_lag, .standby.wal_sender_state, .state, .pgbackrest'
  null
  null
  null
  "started"
  {
    "stanza": "app"
  }

Check backup on the new primary (the one from the old primary is there, and we
can make a new one)

  $ pglift2 instance backups -o json | jq '.[] | .type, .databases'
  "full"
  [
    "postgres"
  ]

  $ pglift2 instance backup
  INFO backing up instance 1\d\/pg2 with pgBackRest (re)
  $ pglift2 instance backups -o json | jq '.[] | .type, .databases'
  "incr"
  [
    "postgres"
  ]
  "full"
  [
    "postgres"
  ]

Rebuild the old primary as a standby (using the pgBackRest backup), using a
new slot on the new primary

  $ pglift2 instance get -o json \
  >   | jq '.name, .replication_slots'
  "pg2"
  []
  $ pglift2 instance alter --create-slot=slot3
  INFO configuring PostgreSQL
  WARNING instance 1\d/pg2 needs restart due to parameter changes: max_connections (re)
  INFO creating replication slot 'slot3'
  $ pglift1 instance drop
  INFO dropping instance 1\d\/pg1 (re)
  WARNING instance 1\d\/pg1 is already stopped (re)
  INFO deconfiguring pgBackRest stanza 'app'
  INFO deleting PostgreSQL data and WAL directories
  $ pglift1 instance create pg3 \
  >   --standby-for="host=$RUN_PREFIX2/postgresql port=$PG2PORT user=replication" \
  >   --standby-password=r3pl \
  >   --standby-slot=slot3 \
  >   --port=$PG1PORT --pgbackrest-stanza=app \
  >   --surole-password=s3per --pgbackrest-password=b@ckUp
  INFO initializing PostgreSQL
  INFO restoring from a pgBackRest backup
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO starting PostgreSQL 1\d\/pg3 (re)
  INFO configuring pgBackRest stanza 'app' for pg1-path=\$TMPDIR\/1\/srv\/pgsql\/1\d\/pg3\/data (re)
  INFO creating pgBackRest stanza 'app'
  WARNING not checking pgBackRest configuration on a standby
  INFO creating instance dumps directory: \$TMPDIR\/1\/srv\/dumps\/1\d-pg3 (re)
  $ pglift1 instance get -o json \
  >   | jq '.standby.slot, .standby.replication_lag, .standby.wal_sender_state, .state, .pgbackrest'
  "slot3"
  "0"
  "streaming"
  "started"
  {
    "stanza": "app"
  }
  $ pglift1 instance backups -o json | jq '.[] | .type, .databases'
  "incr"
  [
    "postgres"
  ]
  "full"
  [
    "postgres"
  ]

Restore on (new) primary:

  $ FULLBACKUP=$(pglift2 instance backups -o json | jq -r '.[] | select(.type == "full") | .label')
  $ pglift2 instance restore --label=$FULLBACKUP
  Error: instance is running
  [1]
  $ pglift2 instance stop
  INFO stopping PostgreSQL 1\d\/pg2 (re)
  $ pglift2 instance restore --label=$FULLBACKUP
  INFO restoring instance 1\d\/pg2 with pgBackRest (re)

(Cleanup)

  INFO dropping instance 1\d\/pg3 (re)
  INFO stopping PostgreSQL 1\d\/pg3 (re)
  INFO deconfiguring pgBackRest stanza 'app'
  INFO deleting PostgreSQL data and WAL directories
  INFO dropping instance 1\d\/pg2 (re)
  WARNING instance 1\d\/pg2 is already stopped (re)
  INFO deconfiguring pgBackRest stanza 'app'
  INFO deleting PostgreSQL data and WAL directories
  INFO deleting pgBackRest include directory
  INFO uninstalling base pgBackRest configuration
  INFO deleting pgBackRest log directory
  INFO deleting pgBackRest spool directory
  INFO deleting PostgreSQL log directory
  INFO deleting PostgreSQL socket directory
  INFO deleting pgBackRest include directory
  INFO uninstalling base pgBackRest configuration
  INFO deleting pgBackRest log directory
  INFO deleting pgBackRest spool directory
  INFO deleting PostgreSQL log directory
  INFO deleting PostgreSQL socket directory (no-eol)
