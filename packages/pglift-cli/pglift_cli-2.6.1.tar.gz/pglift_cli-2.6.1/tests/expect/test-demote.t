# SPDX-FileCopyrightText: 2021 Dalibo
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

  $ PREFIX1=$TMPDIR/1
  $ PREFIX2=$TMPDIR/2
  $ RUN_PREFIX1=$PREFIX1/run
  $ RUN_PREFIX2=$PREFIX2/run
  $ PG1PORT=$(port-for pg1)
  $ PG2PORT=$(port-for pg2)
  $ alias pglift1="env PGLIFT_PREFIX=$PREFIX1 PGLIFT_RUN_PREFIX=$RUN_PREFIX1 pglift --log-level=INFO --non-interactive"
  $ alias pglift2="env PGLIFT_PREFIX=$PREFIX2 PGLIFT_RUN_PREFIX=$RUN_PREFIX2 pglift --log-level=INFO --non-interactive"

  $ pglift1 site-configure install
  INFO creating PostgreSQL log directory: $TMPDIR/1/log/postgresql
  $ pglift2 site-configure install
  INFO creating PostgreSQL log directory: $TMPDIR/2/log/postgresql

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
  > settings:
  >   log_line_prefix: ' ~ '
  > EOF
  $ pglift1 instance apply -f $TMPDIR/primary.yaml
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/1/run/postgresql
  INFO starting PostgreSQL 1\d\/pg1 (re)
  INFO creating role 'replication'
  INFO creating instance dumps directory: \$TMPDIR\/1\/srv\/dumps\/1\d-pg1 (re)

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
  INFO creating PostgreSQL socket directory directory: $TMPDIR/2/run/postgresql
  INFO starting PostgreSQL 1\d\/pg2 (re)
  INFO creating instance dumps directory: \$TMPDIR\/2\/srv\/dumps\/1\d-pg2 (re)

Add some data to the primary, check replication

  $ pglift1 database run -d postgres \
  >   "CREATE TABLE t AS (SELECT generate_series(1, 3) i)"
  INFO running "CREATE TABLE t AS \(SELECT generate_series\(1, 3\) i\)" on postgres database of 1\d\/pg1 (re)
  INFO SELECT 3
  $ pglift2 -Lerror database run -o json -d postgres "SELECT i FROM t"
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
  >   | jq '.standby.slot, .standby.replication_lag, .standby.wal_sender_state, .state'
  null
  "0"
  "streaming"
  "started"

Prepare the primary for rewind connection by creating a rewind user (and resp.
connection database), on the primary (to be demoted)

  $ pglift1 -Lerror role create rwd --login --replication --password=rwdpw
  $ pglift1 -Lerror database create rwdb --owner rwd
  $ pglift1 -Lerror database run -d rwdb \
  >   "GRANT EXECUTE ON function pg_catalog.pg_ls_dir(text, boolean, boolean) TO rwd"
  $ pglift1 -Lerror database run -d rwdb \
  >   "GRANT EXECUTE ON function pg_catalog.pg_stat_file(text, boolean) TO rwd"
  $ pglift1 -Lerror database run -d rwdb \
  >   "GRANT EXECUTE ON function pg_catalog.pg_read_binary_file(text) TO rwd"
  $ pglift1 -Lerror database run -d rwdb \
  >   "GRANT EXECUTE ON function pg_catalog.pg_read_binary_file(text, bigint, bigint, boolean) TO rwd"

Check this role from the standby
  $ pglift2 -Lerror role get rwd -o json
  {
    "name": "rwd",
    "has_password": true,
    "inherit": true,
    "login": true,
    "superuser": false,
    "createdb": false,
    "createrole": false,
    "replication": true,
    "connection_limit": null,
    "valid_until": null,
    "validity": null,
    "memberships": [],
    "hba_records": []
  }

Promote the standby

  $ pglift1 -Lerror instance stop
  $ pglift2 instance status
  PostgreSQL: running
  $ pglift2 instance promote
  INFO promoting PostgreSQL instance

Check connection to the new primary

  $ psql -t -d "host=$RUN_PREFIX2/postgresql port=$PG2PORT user=rwd password=rwdpw dbname=rwdb" -c 'show cluster_name'
   pg2
  

Demote (rewind) the primary as a standby

  $ pglift1 instance demote pg1 \
  >   --from="host=$RUN_PREFIX2/postgresql port=$PG2PORT user=rwd dbname=rwdb" \
  >   --password=rwdpw \
  >   -- --no-ensure-shutdown
  INFO demoting PostgreSQL instance
  INFO configuring PostgreSQL
  INFO starting PostgreSQL 1\d\/pg1 (re)

Check we can connect to the standby with the replication user

  $ psql -t -d "host=$RUN_PREFIX1/postgresql port=$PG1PORT user=replication password=r3pl dbname=postgres" -c 'show cluster_name'
   pg1
  

Check that the instance is really a standby

  $ ls $PREFIX1/srv/pgsql/1*/pg1/data/standby.signal
  $TMPDIR/1/srv/pgsql/1*/pg1/data/standby.signal (glob)
  $ pglift1 -Lerror database run -d postgres 'SHOW primary_conninfo' -o json
  {
    "postgres": [
      {
        "primary_conninfo": "user=rwd password=rwdpw channel_binding=prefer host='$TMPDIR/2/run/postgresql' port=* sslmode=prefer *" (glob)
      }
    ]
  }
  $ pglift1 instance get -o json \
  >   | jq '.standby.slot, .standby.replication_lag, .standby.wal_sender_state, .state'
  null
  "0"
  null
  "started"

And finally check replication is functional

  $ pglift2 -Lerror database create rewindme
  $ pglift2 -Lerror database run -d rewindme "CREATE TABLE t AS (SELECT * FROM generate_series(1, 3) v)"

  $ pglift1 -Lerror database run -d rewindme "TABLE t" -o json
  {
    "rewindme": [
      {
        "v": 1
      },
      {
        "v": 2
      },
      {
        "v": 3
      }
    ]
  }

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
