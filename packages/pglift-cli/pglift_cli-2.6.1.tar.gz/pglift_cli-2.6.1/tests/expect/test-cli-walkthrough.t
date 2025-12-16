# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

Site settings:

  $ export PYTHONIOENCODING=ascii
  $ cat > $TMPDIR/passwords.json << 'EOF'
  > {
  >   "main": {
  >     "postgres": "s3per"
  >   }
  > }
  > EOF
  $ POSTGRES_EXPORTER=$(command -v postgres_exporter || command -v prometheus-postgres-exporter)
  $ export PGLIFT_CONFIG_DIR=$TMPDIR/$TESTFILE.conf.d
  $ mkdir $PGLIFT_CONFIG_DIR
  $ cat > $PGLIFT_CONFIG_DIR/settings.yaml <<EOF
  > cli:
  >   log_format: '%(levelname)-4s %(message)s'
  >   audit:
  >     path: '$TMPDIR/pglift-audit.log'
  >     log_format: '%(levelname)-4s - %(name)s - %(message)s'
  > prefix: '$TMPDIR'
  > run_prefix: '$TMPDIR/run'
  > postgresql:
  >   auth:
  >     local: md5
  >     passfile: '$TMPDIR/.pgpass'
  >     password_command:
  >       - jq
  >       - -r
  >       - '.{instance.name}.{role}'
  >       - '$TMPDIR/passwords.json'
  >   backuprole:
  >     name: pgbackrest
  > pgbackrest:
  >   repository:
  >     mode: path
  >     path: '$TMPDIR/pgbackrest'
  >     retention:
  >       archive: 3
  > powa:
  >   role: pwa
  > prometheus:
  >   execpath: '$POSTGRES_EXPORTER'
  > EOF

  $ mkdir $PGLIFT_CONFIG_DIR/postgresql
  $ cat > $PGLIFT_CONFIG_DIR/postgresql/psqlrc << EOF
  > \set QUIET 1
  > \pset border 0
  > \pset fieldsep '\t'
  > \pset null '(null)'
  > \set QUIET 0
  > EOF

Make sure password_command works:
  $ jq -r ".main.postgres" $TMPDIR/passwords.json
  s3per

  $ pglift site-settings -o json \
  >   | jq '.postgresql.auth, .postgresql.dumps_directory, .prometheus, .run_prefix, .prefix'
  {
    "local": "md5",
    "host": "trust",
    "hostssl": "trust",
    "passfile": "$TMPDIR/.pgpass",
    "password_command": [
      "jq",
      "-r",
      ".{instance.name}.{role}",
      "$TMPDIR/passwords.json"
    ]
  }
  "$TMPDIR/srv/dumps/{version}-{name}"
  {
    "execpath": ".*postgres[-_]exporter", (re)
    "role": "prometheus",
    "configpath": "$TMPDIR/etc/prometheus/postgres_exporter-{name}.conf",
    "pid_file": "$TMPDIR/run/prometheus/{name}.pid"
  }
  "$TMPDIR/run"
  "$TMPDIR"

  $ export PGLIFT_CLI__LOG_LEVEL=info
  $ alias pglift="pglift --non-interactive"

  $ pglift site-configure install
  INFO creating base pgBackRest configuration directory: $TMPDIR/etc/pgbackrest
  INFO installing base pgBackRest configuration
  INFO creating pgBackRest include directory
  INFO creating pgBackRest repository backups and archive directory: $TMPDIR/pgbackrest
  INFO creating pgBackRest log directory: $TMPDIR/log/pgbackrest
  INFO creating pgBackRest spool directory: $TMPDIR/srv/pgbackrest/spool
  INFO creating PostgreSQL log directory: $TMPDIR/log/postgresql

  $ trap "pglift --non-interactive instance drop main; \
  >   pglift --non-interactive site-configure uninstall; \
  >   port-for -u postgres; \
  >   port-for -u prometheus; \
  >   port-for -u prometheus1" \
  >   EXIT

Define ports:

  $ PGPORT=$(port-for postgres)
  $ PGEPORT=$(port-for prometheus)
  $ PGEPORT1=$(port-for prometheus1)

Audit log:

  $ cat $TMPDIR/pglift-audit.log
  INFO - pglift_cli.audit - command: .+\/pglift --non-interactive site-configure install (re)
  DEBUG - pglift.pgbackrest - loading pgbackrest.conf template
  DEBUG - pglift.util - using 'pgbackrest/pgbackrest.conf' configuration file from distribution
  INFO - pglift.util - creating base pgBackRest configuration directory: $TMPDIR/etc/pgbackrest
  INFO - pglift.pgbackrest - installing base pgBackRest configuration
  INFO - pglift.pgbackrest - creating pgBackRest include directory
  INFO - pglift.util - creating pgBackRest repository backups and archive directory: $TMPDIR/pgbackrest
  INFO - pglift.util - creating pgBackRest log directory: $TMPDIR/log/pgbackrest
  INFO - pglift.util - creating pgBackRest spool directory: $TMPDIR/srv/pgbackrest/spool
  INFO - pglift.util - creating PostgreSQL log directory: $TMPDIR/log/postgresql
  INFO - pglift_cli.audit - command completed \(\d+.\d+ seconds\) (re)

Create an instance

  $ pglift instance create main \
  >   --data-checksums \
  >   --auth-host=ident \
  >   --port=$PGPORT --surole-password=s3per \
  >   --pgbackrest-stanza=main --pgbackrest-password='b@ck up!' \
  >   --prometheus-port=$PGEPORT
  INFO initializing PostgreSQL
  INFO configuring PostgreSQL authentication
  INFO configuring PostgreSQL
  INFO creating PostgreSQL socket directory directory: $TMPDIR/run/postgresql
  INFO starting PostgreSQL 1\d\/main (re)
  INFO creating role 'pwa'
  INFO creating role 'prometheus'
  INFO creating role 'pgbackrest'
  INFO creating 'powa' database in 1\d\/main (re)
  INFO creating extension 'btree_gist' in database powa
  INFO creating extension 'pg_qualstats' in database powa
  INFO creating extension 'pg_stat_statements' in database powa
  INFO creating extension 'pg_stat_kcache' in database powa
  INFO creating extension 'powa' in database powa
  INFO configuring Prometheus postgres_exporter 1\d-main (re)
  INFO configuring pgBackRest stanza 'main' for pg1-path=\$TMPDIR\/srv\/pgsql\/1\d\/main\/data (re)
  INFO creating pgBackRest stanza 'main'
  INFO checking pgBackRest configuration for stanza 'main'
  INFO creating instance dumps directory: \$TMPDIR\/srv\/dumps\/1\d-main (re)
  INFO starting Prometheus postgres_exporter 1\d-main (re)

Try editing a parameter that already has a value defined in the pgbackrest template:

  $ pglift pgconf set wal_level='logical'
  INFO configuring PostgreSQL
  INFO parameter 'wal_level' is overwritten by 'pgbackrest' configuration, 'replica' will be used instead of 'logical'
  changes in 'wal_level' not applied
   hint: either these changes have no effect (values already set) or specified parameters are already defined in an un-managed file (e.g. 'postgresql.conf')

Error cases for instance operations

  $ pglift instance create main --pgbackrest-stanza=st --surole-password=s3per
  Error: instance already exists
  [1]
  $ pglift instance create 'in/va/lid' --pgbackrest-stanza=xxx --surole-password=s3per
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for 'NAME': String should match pattern '^[^/-]+$'
  [2]
  $ pglift instance create stdby --standby-for='port 1234' --pgbackrest-stanza=stddy --surole-password=s3per
  Usage: pglift instance create [OPTIONS] NAME
  Try 'pglift instance create --help' for help.
  
  Error: Invalid value for '--standby-for': missing "=" after "port" in connection info string
  
  [2]
  $ pglift instance apply
  Usage: pglift instance apply [OPTIONS]
  Try 'pglift instance apply --help' for help.
  
  Error: Missing option '-f' / '--file'.
  [2]
  $ pglift instance alter notfound --port=1234
  Usage: pglift instance alter [OPTIONS] [INSTANCE]
  Try 'pglift instance alter --help' for help.
  
  Error: Invalid value for '[INSTANCE]': instance 'notfound' not found
  [2]
  $ pglift instance status notfound
  Usage: pglift instance status [OPTIONS] [INSTANCE]
  Try 'pglift instance status --help' for help.
  
  Error: Invalid value for '[INSTANCE]': instance 'notfound' not found
  [2]
  $ pglift instance drop notfound
  Usage: pglift instance drop [OPTIONS] [INSTANCE]...
  Try 'pglift instance drop --help' for help.
  
  Error: Invalid value for '[INSTANCE]...': instance 'notfound' not found
  [2]

  $ grep 'pglift_cli.audit' $TMPDIR/pglift-audit.log
  INFO - pglift_cli.audit - command: .*\/pglift --non-interactive site-configure install (re)
  INFO - pglift_cli.audit - command completed \(\d+(\.\d+)? seconds\) (re)
  INFO - pglift_cli.audit - command: .*\/pglift --non-interactive instance create main --data-checksums --auth-host=ident --port=\d+ --surole-password=s3per --pgbackrest-stanza=main '--pgbackrest-password=b@ck up!' --prometheus-port=\d+ (re)
  INFO - pglift_cli.audit - command completed \(\d+(\.\d+)? seconds\) (re)
  INFO - pglift_cli.audit - command: .*\/pglift --non-interactive pgconf set wal_level=logical (re)
  INFO - pglift_cli.audit - command completed \(\d+(\.\d+)? seconds\) (re)
  INFO - pglift_cli.audit - command: .*\/pglift --non-interactive instance create main --pgbackrest-stanza=st --surole-password=s3per (re)
  ERROR - pglift_cli.audit - command failed \(\d+(\.\d+)? seconds\) (re)

List instances

  $ pglift instance list -o json | jq '.[] | .name, .status'
  "main"
  "running"
  $ pglift instance list --version=14

Get the status of an instance:

  $ pglift -L debug -l $TMPDIR/pglift.log instance status main
  PostgreSQL: running
  prometheus: running
  $ grep -v "DEBUG instance 'main' not found in version" $TMPDIR/pglift.log
  DEBUG debug logging at \$TMPDIR/pglift-\w+-\d+.\d+.log (re)
  DEBUG looking for 'postgres_exporter@1\d-main' service status by its PID at \$TMPDIR\/run\/prometheus\/1\d-main.pid (re)
  DEBUG get status of PostgreSQL instance 1\d\/main (re)
  DEBUG \/usr\/.+1\d\/bin\/pg_ctl status -D \$TMPDIR\/srv\/pgsql\/1\d\/main\/data (re)

Reload, restart:

  $ pglift instance reload
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  $ pglift instance restart
  INFO restarting instance 1\d\/main (re)
  INFO stopping Prometheus postgres_exporter 1\d-main (re)
  INFO restarting PostgreSQL
  INFO stopping PostgreSQL 1\d\/main (re)
  INFO starting PostgreSQL 1\d\/main (re)
  INFO starting Prometheus postgres_exporter 1\d-main (re)

Stop, alter, (re)start an instance:

  $ pglift instance stop
  INFO stopping PostgreSQL 1\d\/main (re)
  INFO stopping Prometheus postgres_exporter 1\d-main (re)
  $ pglift instance alter --no-data-checksums
  INFO configuring PostgreSQL
  INFO disabling data checksums
  $ pglift instance alter --prometheus-port=$PGEPORT1 --state=started --powa-password=p0W@ --diff
  INFO configuring PostgreSQL
  INFO starting PostgreSQL 1\d\/main (re)
  INFO reconfiguring Prometheus postgres_exporter 1\d-main (re)
  INFO restarting Prometheus postgres_exporter 1\d-main (re)
  INFO starting Prometheus postgres_exporter 1\d-main (re)
  --- $TMPDIR/etc/prometheus/postgres_exporter-1*-main.conf (glob)
  +++ $TMPDIR/etc/prometheus/postgres_exporter-1*-main.conf (glob)
  @@ -1,2 +1,2 @@
   DATA_SOURCE_NAME=postgresql://prometheus@:*/postgres?host=* (glob)
  *%2Fpostgresql&sslmode=disable (glob)
  -POSTGRES_EXPORTER_OPTS='--web.listen-address :\d+ --log.level info' (re)
  \+POSTGRES_EXPORTER_OPTS='--web.listen-address :\d+ --log.level info' (re)
  --- /dev/null
  +++ $TMPDIR/run/prometheus/1*-main.pid (glob)
  @@ -0,0 +1 @@
  \+\d+ (re)
  $ pglift -Lwarning instance start
  WARNING instance 1\d\/main is already started (re)
  $ pglift instance get -o json \
  >   | jq '.data_checksums, .port, .prometheus, .settings.unix_socket_directories, .state'
  false
  \d+ (re)
  {
    "port": \d+ (re)
  }
  "$TMPDIR/run/postgresql"
  "started"

  $ cat > $TMPDIR/main.yaml << EOF
  > name: main
  > port: $PGPORT
  > settings:
  >   work_mem: 5MB
  > prometheus:
  >   port: $PGEPORT1
  > pgbackrest:
  >   stanza: main
  > roles:
  >   - name: arole
  >     password: Ar0le
  >     createdb: true
  >     hba_records:
  >       - database: adb
  >         method: trust
  >     pgpass: false
  > EOF
  $ pglift instance apply -f $TMPDIR/main.yaml --diff
  INFO configuring PostgreSQL
  INFO instance 1\d\/main needs reload due to parameter changes: work_mem (re)
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  INFO starting Prometheus postgres_exporter 1\d-main (re)
  INFO creating role 'arole'
  INFO HBA configuration updated
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  --- $TMPDIR/srv/pgsql/1*/main/data/postgresql.conf (glob)
  +++ $TMPDIR/srv/pgsql/1*/main/data/postgresql.conf (glob)
  @@ -*,* +*,* @@ (glob)
                                          # (change requires restart)
   # Caution: it is not advisable to set max_prepared_transactions nonzero unless
   # you actively intend to use prepared transactions.
  -#work_mem = 4MB                                # min 64kB
  +work_mem = '5MB'  # min 64kB
   #hash_mem_multiplier = *.0             # * (glob)
  work_mem
   #maintenance_work_mem = 64MB           # * (glob)
   #autovacuum_work_mem = -1              # * (glob)
  maintenance_work_mem
  --- $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  +++ $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  \@\@ -\d+,3 \+\d+,4 \@\@ (re)
   local   all             all                                     md5
   host    all             all             127.0.0.1/32            ident
   host    all             all             ::1/128                 ident
  +local   adb             arole                                   trust

Instance environment, and program execution:

  $ pglift instance env | grep PASSFILE
  PGPASSFILE=$TMPDIR/.pgpass
  $ pglift instance env -o json | jq '.PGBACKREST_STANZA, .PGHOST, .PGPASSWORD'
  "main"
  "$TMPDIR/run/postgresql"
  "s3per"
  $ pglift instance exec main
  Usage: pglift instance exec [OPTIONS] INSTANCE COMMAND...
  Try 'pglift instance exec --help' for help.
  
  Error: Missing argument 'COMMAND...'.
  [2]
  $ pglift instance exec main -- psql -t -c 'SELECT 1'
         1
  

PostgreSQL configuration

  $ pglift pgconf show port logging_collector
  port = \d+ (re)
  logging_collector = on
  $ pglift pgconf set invalid
  Usage: pglift pgconf set [OPTIONS] <PARAMETER>=<VALUE>...
  Try 'pglift pgconf set --help' for help.
  
  Error: Invalid value for '<PARAMETER>=<VALUE>...': invalid
  [2]
  $ pglift --non-interactive pgconf set --dry-run log_statement=ddl
  WARNING failed to get data_checksums status: 'Data page checksum version' not found in controldata
  INFO configuring PostgreSQL
  INFO instance 1\d\/main needs reload due to parameter changes: log_statement (re)
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  log_statement: None -> ddl
  DRY RUN: no changes made
  $ pglift --non-interactive pgconf set log_statement=ddl log_line_prefix=' ~ '
  INFO configuring PostgreSQL
  INFO instance 1\d\/main needs reload due to parameter changes: log_line_prefix, log_statement (re)
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  log_line_prefix: None ->  ~ 
  log_statement: None -> ddl
  $ pglift --non-interactive pgconf set log_statement=ddl
  INFO configuring PostgreSQL
  changes in 'log_statement' not applied
   hint: either these changes have no effect (values already set) or specified parameters are already defined in an un-managed file (e.g. 'postgresql.conf')
  $ pglift pgconf show log_statement
  log_statement = 'ddl'
  $ pglift --non-interactive pgconf remove fsync
  Error: 'fsync' not found in managed configuration
  [1]
  $ pglift --non-interactive pgconf remove --dry-run log_statement
  WARNING failed to get data_checksums status: 'Data page checksum version' not found in controldata
  INFO configuring PostgreSQL
  INFO instance 1\d\/main needs reload due to parameter changes: log_statement (re)
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  log_statement: ddl -> None
  DRY RUN: no changes made
  $ pglift --non-interactive pgconf remove log_statement
  INFO configuring PostgreSQL
  INFO instance 1\d\/main needs reload due to parameter changes: log_statement (re)
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  log_statement: ddl -> None
  $ pglift pgconf show log_statement
  # log_statement = 'ddl'
  $ pglift --non-interactive pgconf set port=1234 --dry-run
  WARNING failed to get data_checksums status: 'Data page checksum version' not found in controldata
  INFO configuring PostgreSQL
  INFO reconfiguring Prometheus postgres_exporter 1\d-main (re)
  INFO restarting Prometheus postgres_exporter 1\d-main (re)
  INFO configuring pgBackRest stanza 'main' for pg1-path=\$TMPDIR\/srv\/pgsql\/1\d\/main\/data (re)
  port: \d+ -> 1234 (re)
  DRY RUN: no changes made

HBA configuration management:

  $ version=$(pglift instance list -o json | jq -r '.[] | .version')
  $ # Adding a comment in the file
  $ printf "\n# a comment" >> $TMPDIR/srv/pgsql/${version}/main/data/pg_hba.conf
  $ pglift pghba add --user bob --method trust
  INFO entry added to HBA configuration
  $ pglift pghba add --dry-run --diff --user bob --method trust \
  >     --connection-type host --connection-address 127.0.0.1
  INFO entry added to HBA configuration
  --- $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  +++ $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  @@ -*,3 +*,4 @@ (glob)
   local   adb             arole                                   trust
   # a comment
   local   all             bob                                     trust
  +host    all             bob             127.0.0.1               trust
  DRY RUN: no changes made
  $ pglift pghba add --user bob --method trust \
  >     --connection-type host --connection-address 127.0.0.1
  INFO entry added to HBA configuration
  $ pglift pghba add --user bob --method trust \
  >     --connection-address 192.168.12.10/32 \
  >     --database mydb
  INFO entry added to HBA configuration
  $ pglift pghba add --diff --user bob --method trust \
  >     --connection-type host --connection-address 192.168.12.10 --connection-netmask 255.255.255.255 \
  >     --database myotherdb
  INFO entry added to HBA configuration
  --- $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  +++ $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  @@ -*,3 +*,4 @@ (glob)
   local   all             bob                                     trust
   host    all             bob             127.0.0.1               trust
   host    mydb            bob             192.168.12.10/32         trust
  +host    myotherdb       bob             192.168.12.10   255.255.255.255 trust
  $ pglift pghba add --user bob,peter --method trust \
  >     --connection-address 192.168.12.10/32 \
  >     --database mybd,myotherdb
  INFO entry added to HBA configuration
  $ grep 'bob' $TMPDIR/srv/pgsql/${version}/main/data/pg_hba.conf
  local   all             bob                                     trust
  host    all             bob             127.0.0.1               trust
  host    mydb            bob             192.168.12.10/32         trust
  host    myotherdb       bob             192.168.12.10   255.255.255.255 trust
  host    mybd,myotherdb  bob,peter       192.168.12.10/32         trust
  $ pglift pghba remove --user bob --method trust \
  >     --connection-type host --connection-address 192.168.12.10/32 \
  >     --database mydb
  INFO entry removed from HBA configuration
  $ pglift pghba remove --dry-run --diff --user bob --method trust \
  >     --connection-type host --connection-address 192.168.12.10 --connection-netmask 255.255.255.255 \
  >     --database myotherdb
  INFO entry removed from HBA configuration
  --- $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  +++ $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  @@ -*,5 +*,4 @@ (glob)
   # a comment
   local   all             bob                                     trust
   host    all             bob             127.0.0.1               trust
  -host    myotherdb       bob             192.168.12.10   255.255.255.255 trust
   host    mybd,myotherdb  bob,peter       192.168.12.10/32         trust
  DRY RUN: no changes made
  $ pglift pghba remove --user bob --method trust \
  >     --connection-type host --connection-address 192.168.12.10 --connection-netmask 255.255.255.255 \
  >     --database myotherdb
  INFO entry removed from HBA configuration
  $ pglift pghba remove --diff --user bob,peter --method trust \
  >     --connection-type host --connection-address 192.168.12.10/32 \
  >     --database mybd,myotherdb
  INFO entry removed from HBA configuration
  --- $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  +++ $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  @@ -*,4 +*,3 @@ (glob)
   # a comment
   local   all             bob                                     trust
   host    all             bob             127.0.0.1               trust
  -host    mybd,myotherdb  bob,peter       192.168.12.10/32         trust
  $ pglift pghba remove --user alice --method trust \
  >     --connection-type host --connection-address somehost
  ERROR entry not found in HBA configuration
  $ grep 'bob' $TMPDIR/srv/pgsql/${version}/main/data/pg_hba.conf
  local   all             bob                                     trust
  host    all             bob             127.0.0.1               trust

Instance logs:

  $ pglift instance logs --no-follow | grep -v GMT
  INFO reading logs of instance 1\d\/main from \$TMPDIR\/log\/postgresql\/1\d-main-.+.log (re)
   ~ LOG:  parameter "log_line_prefix" changed to " ~ "
   ~ LOG:  parameter "log_statement" changed to "ddl"
   ~ LOG:  received SIGHUP, reloading configuration files
   ~ LOG:  parameter "log_statement" removed from configuration file, reset to default


Roles

Add and manipulate roles:

  $ pglift role -i main create dba --login --pgpass --password=qwerty --in-role=pg_read_all_stats --dry-run
  INFO creating role 'dba'
  INFO adding an entry for 'dba' in \$TMPDIR\/.pgpass \(port=\d+\) (re)
  DRY RUN: no changes made

  $ pglift role -i main create dba --login --pgpass --password=qwerty --in-role=pg_read_all_stats
  INFO creating role 'dba'
  INFO adding an entry for 'dba' in \$TMPDIR\/.pgpass \(port=\d+\) (re)

  $ cat $TMPDIR/.pgpass
  \*:\d+:\*:dba:qwerty (re)

  $ pglift role get dba
                                                         conne                    
         has_p                                     repl  ction  vali  membe       
         asswo  inher         super  creat  creat  icat  _limi  d_un  rship  pgpa 
   name  rd     it     login  user   edb    erole  ion   t      til   s      ss   
   dba   True   True   True   False  False  False  Fals               pg_re  True 
                                                   e                  ad_al       
                                                                      l_sta       
                                                                      ts          

  $ pglift role -i main create dba --dry-run
  Error: role already exists
  [1]

  $ pglift role -i main create dba
  Error: role already exists
  [1]

  $ PGDATABASE=postgres PGUSER=dba PGPASSWORD= \
  >   pglift instance exec main -- psql -c "SELECT current_user;"
  current_user 
  ------------
  dba
  (1 row)
  
  $ pglift role alter dba --connection-limit=10 --inherit --no-pgpass --no-login --revoke=pg_read_all_stats --grant=pg_monitor --valid-until=2026-01-01 --dry-run
  INFO altering role 'dba'
  INFO removing entry for 'dba' in \$TMPDIR\/.pgpass \(port=\d+\) (re)
  INFO removing now empty $TMPDIR/.pgpass
  DRY RUN: no changes made

  $ pglift role -i main create dba --password=qwerty --encrypted-password=md5azerty
  Usage: pglift role create [OPTIONS] NAME
  Try 'pglift role create --help' for help.
  
  Error: '--password' and '--encrypted-password' can't be used together
  [2]

  $ pglift role alter dba --connection-limit=10 --inherit --no-pgpass --no-login --revoke=pg_read_all_stats --grant=pg_monitor --valid-until=2026-01-01
  INFO altering role 'dba'
  INFO removing entry for 'dba' in \$TMPDIR\/.pgpass \(port=\d+\) (re)
  INFO removing now empty $TMPDIR/.pgpass

  $ pglift role get dba -o json
  {
    "name": "dba",
    "has_password": true,
    "inherit": true,
    "login": false,
    "superuser": false,
    "createdb": false,
    "createrole": false,
    "replication": false,
    "connection_limit": 10,
    "valid_until": "2026-01-01T00:00:00Z",
    "validity": "2026-01-01T00:00:00Z",
    "memberships": [
      {
        "role": "pg_monitor"
      }
    ],
    "hba_records": [],
    "pgpass": false
  }

  $ cat > $TMPDIR/role.yaml <<EOF
  > name: test
  > connection_limit: 3
  > login: false
  > memberships: ['pg_monitor']
  > hba_records:
  > - database: mydb
  >   method: trust
  > - connection:
  >     address: 192.168.12.10/32
  >   database: mydb
  >   method: trust
  > - connection:
  >     address: 127.0.0.1
  >     netmask: 255.255.255.255
  >   database: otherdb
  >   method: trust
  > - connection:
  >     type: hostssl
  >     address: samenet
  >   database: otherdb
  >   method: trust
  > EOF
  $ pglift role apply -f $TMPDIR/role.yaml --dry-run
  INFO creating role 'test'
  INFO HBA configuration updated
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  DRY RUN: no changes made
  $ grep 'test' $TMPDIR/srv/pgsql/${version}/main/data/pg_hba.conf
  [1]
  $ pglift role get test
  Error: role 'test' not found
  [1]
  $ pglift role apply -f $TMPDIR/role.yaml --diff
  INFO creating role 'test'
  INFO HBA configuration updated
  INFO reloading PostgreSQL configuration for 1\d\/main (re)
  --- $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  +++ $TMPDIR/srv/pgsql/1*/main/data/pg_hba.conf (glob)
  \@\@ -\d+,3 \+\d+,7 \@\@ (re)
   # a comment
   local   all             bob                                     trust
   host    all             bob             127.0.0.1               trust
  +local   mydb            test                                    trust
  +host    mydb            test            192.168.12.10/32         trust
  +host    otherdb         test            127.0.0.1       255.255.255.255 trust
  +hostssl otherdb         test            samenet                 trust
  $ version=$(pglift instance list -o json | jq -r '.[] | .version')
  $ grep 'test' $TMPDIR/srv/pgsql/${version}/main/data/pg_hba.conf
  local   mydb            test                                    trust
  host    mydb            test            192.168.12.10/32         trust
  host    otherdb         test            127.0.0.1       255.255.255.255 trust
  hostssl otherdb         test            samenet                 trust
  $ cat >> $TMPDIR/role.yaml <<EOF
  > createdb: true
  > EOF
  $ pglift role apply -f $TMPDIR/role.yaml
  INFO altering role 'test'
  $ pglift role get test -o json
  {
    "name": "test",
    "has_password": false,
    "inherit": true,
    "login": false,
    "superuser": false,
    "createdb": true,
    "createrole": false,
    "replication": false,
    "connection_limit": 3,
    "valid_until": null,
    "validity": null,
    "memberships": [
      {
        "role": "pg_monitor"
      }
    ],
    "hba_records": [
      {
        "connection": null,
        "database": "mydb",
        "method": "trust"
      },
      {
        "connection": {
          "type": "host",
          "address": "192.168.12.10/32",
          "netmask": null
        },
        "database": "mydb",
        "method": "trust"
      },
      {
        "connection": {
          "type": "host",
          "address": "127.0.0.1",
          "netmask": "255.255.255.255"
        },
        "database": "otherdb",
        "method": "trust"
      },
      {
        "connection": {
          "type": "hostssl",
          "address": "samenet",
          "netmask": null
        },
        "database": "otherdb",
        "method": "trust"
      }
    ],
    "pgpass": false
  }

  $ pglift role list -o json | jq '[.[] | select(.name | contains("powa_") | not)]'
  [
    {
      "name": "arole",
      "has_password": true,
      "inherit": true,
      "login": false,
      "superuser": false,
      "createdb": true,
      "createrole": false,
      "replication": false,
      "connection_limit": null,
      "valid_until": null,
      "validity": null,
      "memberships": [],
      "hba_records": []
    },
    {
      "name": "dba",
      "has_password": true,
      "inherit": true,
      "login": false,
      "superuser": false,
      "createdb": false,
      "createrole": false,
      "replication": false,
      "connection_limit": 10,
      "valid_until": "2026-01-01T00:00:00Z",
      "validity": "2026-01-01T00:00:00Z",
      "memberships": [
        {
          "role": "pg_monitor"
        }
      ],
      "hba_records": []
    },
    {
      "name": "pgbackrest",
      "has_password": true,
      "inherit": true,
      "login": true,
      "superuser": true,
      "createdb": false,
      "createrole": false,
      "replication": false,
      "connection_limit": null,
      "valid_until": null,
      "validity": null,
      "memberships": [],
      "hba_records": []
    },
    {
      "name": "postgres",
      "has_password": true,
      "inherit": true,
      "login": true,
      "superuser": true,
      "createdb": true,
      "createrole": true,
      "replication": true,
      "connection_limit": null,
      "valid_until": null,
      "validity": null,
      "memberships": [],
      "hba_records": []
    },
    {
      "name": "prometheus",
      "has_password": false,
      "inherit": true,
      "login": true,
      "superuser": false,
      "createdb": false,
      "createrole": false,
      "replication": false,
      "connection_limit": null,
      "valid_until": null,
      "validity": null,
      "memberships": [
        {
          "role": "pg_monitor"
        }
      ],
      "hba_records": []
    },
    {
      "name": "pwa",
      "has_password": false,
      "inherit": true,
      "login": true,
      "superuser": true,
      "createdb": false,
      "createrole": false,
      "replication": false,
      "connection_limit": null,
      "valid_until": null,
      "validity": null,
      "memberships": [],
      "hba_records": []
    },
    {
      "name": "test",
      "has_password": false,
      "inherit": true,
      "login": false,
      "superuser": false,
      "createdb": true,
      "createrole": false,
      "replication": false,
      "connection_limit": 3,
      "valid_until": null,
      "validity": null,
      "memberships": [
        {
          "role": "pg_monitor"
        }
      ],
      "hba_records": []
    }
  ]
  $ pglift role get notfound
  Error: role 'notfound' not found
  [1]
  $ pglift role drop notfound
  Error: role 'notfound' not found
  [1]

Databases

  $ pglift database create test --dry-run
  INFO creating 'test' database in 1\d\/main (re)
  DRY RUN: no changes made
  $ pglift database create test --owner test
  INFO creating 'test' database in 1\d\/main (re)
  $ pglift database create myapp --owner dba --schema app
  INFO creating 'myapp' database in 1\d\/main (re)
  INFO creating schema 'app' in database myapp with owner 'dba'

  $ cat > $TMPDIR/other.yaml <<EOF
  > name: other
  > extensions:
  >   - name: pg_stat_statements
  > EOF
  $ pglift database apply -f $TMPDIR/other.yaml --dry-run
  INFO creating 'other' database in 1\d/main (re)
  INFO creating extension 'pg_stat_statements' in database other
  DRY RUN: no changes made
  $ pglift database create other
  INFO creating 'other' database in 1\d/main (re)
  $ pglift database apply -f $TMPDIR/other.yaml --dry-run
  INFO altering 'other' database on instance 1\d\/main (re)
  INFO creating extension 'pg_stat_statements' in database other
  DRY RUN: no changes made
  $ pglift database run -d other "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements')"
  INFO running "SELECT EXISTS \(SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'\)" on other database of 1\d\/main (re)
  INFO SELECT 1
   Database 
    other   
  +--------+
  | exists |
  |--------|
  | False  |
  +--------+
  $ pglift database apply -f $TMPDIR/other.yaml -o json --diff
  INFO altering 'other' database on instance 1\d\/main (re)
  INFO creating extension 'pg_stat_statements' in database other
  {
    "change_state": "changed",
    "diff": []
  }
  $ pglift database run -d other "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements')"
  INFO running "SELECT EXISTS \(SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'\)" on other database of 1\d\/main (re)
  INFO SELECT 1
   Database 
    other   
  +--------+
  | exists |
  |--------|
  | True   |
  +--------+
  $ cat > $TMPDIR/other.yaml <<EOF
  > name: other
  > state: absent
  > EOF
  $ pglift database apply -f $TMPDIR/other.yaml --dry-run
  INFO dropping 'other' database
  DRY RUN: no changes made
  $ pglift database drop other --dry-run
  INFO dropping 'other' database
  DRY RUN: no changes made
  $ pglift database get other
                   setting           extensio          publica  subscrip  tablesp 
   name   owner    s        schemas  ns        locale  tions    tions     ace     
   other  postgre           public   pg_stat_  C                          pg_defa 
          s                          statemen                             ult     
                                     ts                                           
  $ pglift database create other
  Error: database already exists
  [1]

  $ pglift database alter other --owner=test --add-extension=unaccent --add-schema=myschema --dry-run
  INFO altering 'other' database on instance 1\d\/main (re)
  INFO creating schema 'myschema' in database other with owner 'test'
  INFO creating extension 'unaccent' in database other
  DRY RUN: no changes made

  $ pglift database alter other --owner=test --add-extension=unaccent --add-schema=myschema
  INFO altering 'other' database on instance 1\d\/main (re)
  INFO creating schema 'myschema' in database other with owner 'test'
  INFO creating extension 'unaccent' in database other

  $ pglift database alter other --owner=test --remove-extension=unaccent --remove-schema=myschema
  INFO altering 'other' database on instance 1\d\/main (re)
  INFO dropping schema myschema from database other
  INFO dropping extension 'unaccent'

  $ pglift database get nosuchdb
  Error: database 'nosuchdb' not found
  [1]
  $ pglift database get myapp -o json
  {
    "name": "myapp",
    "owner": "dba",
    "settings": null,
    "schemas": [
      {
        "name": "app",
        "owner": "dba"
      },
      {
        "name": "public",
        "owner": ".+" (re)
      }
    ],
    "extensions": [],
    "locale": "C",
    "publications": [],
    "subscriptions": [],
    "tablespace": "pg_default"
  }

  $ pglift database run -d myapp \
  >     "CREATE SCHEMA hollywood CREATE TABLE films (title text, release date, awards text[]) CREATE VIEW winners AS SELECT title, release FROM films WHERE awards IS NOT NULL;"
  INFO running "CREATE SCHEMA hollywood CREATE TABLE films \(title text, release date, awards text\[\]\) CREATE VIEW winners AS SELECT title, release FROM films WHERE awards IS NOT NULL;" on myapp database of 1\d\/main (re)
  INFO CREATE SCHEMA

  $ pglift database run -d myapp \
  >     "ALTER DEFAULT PRIVILEGES IN SCHEMA hollywood GRANT DELETE, INSERT, SELECT ON TABLES TO dba"
  INFO running "ALTER DEFAULT PRIVILEGES IN SCHEMA hollywood GRANT DELETE, INSERT, SELECT ON TABLES TO dba" on myapp database of 1\d\/main (re)
  INFO ALTER DEFAULT PRIVILEGES

  $ pglift instance privileges main --default -o json
  [
    {
      "database": "myapp",
      "schema": "hollywood",
      "object_type": "TABLE",
      "role": "dba",
      "privileges": [
        "DELETE",
        "INSERT",
        "SELECT"
      ]
    }
  ]
  $ pglift instance privileges main -d myapp -r dba --default -o json
  [
    {
      "database": "myapp",
      "schema": "hollywood",
      "object_type": "TABLE",
      "role": "dba",
      "privileges": [
        "DELETE",
        "INSERT",
        "SELECT"
      ]
    }
  ]
  $ pglift instance privileges main -d postgres --default -o json
  []
  $ pglift database privileges myapp -r dba
  $ pglift database privileges myapp --default -o json
  [
    {
      "database": "myapp",
      "schema": "hollywood",
      "object_type": "TABLE",
      "role": "dba",
      "privileges": [
        "DELETE",
        "INSERT",
        "SELECT"
      ]
    }
  ]
  $ pglift role privileges dba -o json
  []
  $ pglift role privileges dba --default -d myapp -o json
  [
    {
      "database": "myapp",
      "schema": "hollywood",
      "object_type": "TABLE",
      "role": "dba",
      "privileges": [
        "DELETE",
        "INSERT",
        "SELECT"
      ]
    }
  ]

  $ pglift database run -d myapp "bad sql"
  INFO running "bad sql" on myapp database of 1\d\/main (re)
  Error: syntax error at or near "bad"
  LINE 1: bad sql
          ^
  [1]
  $ pglift database run -d myapp \
  >     "INSERT INTO hollywood.films VALUES ('Blade Runner', 'June 25, 1982', '{\"Hugo Award\", \"Saturn Award\"}');"
  INFO running "INSERT INTO hollywood.films VALUES \('Blade Runner', 'June 25, 1982', '{"Hugo Award", "Saturn Award"}'\);" on myapp database of 1\d\/main (re)
  INFO INSERT 0 1
  $ pglift database run -d myapp -o json "TABLE hollywood.films;"
  INFO running "TABLE hollywood.films;" on myapp database of 1\d\/main (re)
  INFO SELECT 1
  {
    "myapp": [
      {
        "title": "Blade Runner",
        "release": "1982-06-25",
        "awards": [
          "Hugo Award",
          "Saturn Award"
        ]
      }
    ]
  }

  $ PGDATABASE=myapp pglift instance exec main -- \
  >     psql -c "SELECT * FROM hollywood.winners ORDER BY release ASC;"
     title      release   
  ------------ ----------
  Blade Runner 1982-06-25
  (1 row)
  

  $ pglift database dump nosuchdb
  INFO backing up database 'nosuchdb' on instance 1\d\/main (re)
  Error: .+ database "nosuchdb" does not exist (re)
  [1]
  $ pglift database dump postgres --dry-run
  INFO backing up database 'postgres' on instance 1\d/main (re)
  DRY RUN: no changes made
  $ pglift database dump postgres
  INFO backing up database 'postgres' on instance 1\d/main (re)
  $ ls $TMPDIR/srv/dumps/*-main
  postgres_[0-9-T:+]+.dump (re)
  $ pglift database dump myapp --output $TMPDIR/no-such-directory
  Usage: pglift database dump [OPTIONS] DBNAME
  Try 'pglift database dump --help' for help.
  
  Error: Invalid value for '-o' / '--output': Directory '$TMPDIR/no-such-directory' does not exist.
  [2]
  $ mkdir $TMPDIR/db-backups
  $ pglift database dump myapp
  INFO backing up database 'myapp' on instance 1\d\/main (re)
  $ pglift database dumps myapp -o json | jq '.[] | .id, .dbname'
  "myapp_\S+" (re)
  "myapp"
  $ pglift database dump myapp -o $TMPDIR/db-backups
  INFO backing up database 'myapp' on instance 1\d\/main (re)
  $ ls $TMPDIR/db-backups
  myapp_[0-9-T:+]+.dump (re)
  $ DUMP_ID=$(pglift database dumps myapp -o json | jq '.[] | .id' | grep -Po "(?<=\")(.*)(?=\")")

  $ pglift database drop myapp
  INFO dropping 'myapp' database

  $ pglift database restore doesnt_exist_id --dry-run
  Error: dump 'doesnt_exist_id' not found
  [1]

  $ pglift database restore doesnt_exist_id
  Error: dump 'doesnt_exist_id' not found
  [1]

  $ pglift database restore $DUMP_ID --dry-run
  INFO restoring dump for 'myapp' on instance 1\d\/main (re)
  DRY RUN: no changes made

  $ pglift database restore $DUMP_ID
  INFO restoring dump for 'myapp' on instance 1\d\/main (re)

  $ pglift database create devapp
  INFO creating 'devapp' database in 1\d\/main (re)

  $ pglift database restore $DUMP_ID devapp
  INFO restoring dump for 'myapp' on instance 1\d\/main into 'devapp' (re)

  $ pglift database drop devapp
  INFO dropping 'devapp' database

  $ pglift database list -x template1 -o json | jq '.[] | .name, .owner, .description'
  "myapp"
  "dba"
  null
  "other"
  "test"
  null
  "postgres"
  "postgres"
  "default administrative connection database"
  "powa"
  "postgres"
  null
  "test"
  "test"
  null
  $ pglift database list template1 -o json | jq '.[] | .encoding, .collation, .tablespace.name'
  "UTF8"
  "C"
  "pg_default"
  $ pglift database drop nosuchdb
  Error: database 'nosuchdb' not found
  [1]
  $ pglift database drop myapp
  INFO dropping 'myapp' database

  $ pglift role drop test --dry-run
  INFO dropping role 'test'
  INFO removing entries from HBA configuration
  DRY RUN: no changes made
  $ pglift role drop test
  INFO dropping role 'test'
  Error: role "test" cannot be dropped because some objects depend on it (detail: owner of database test
  owner of database other)
  [1]
  $ pglift role drop test --drop-owned --reassign-owned=postgres
  Usage: pglift role drop [OPTIONS] NAME
  Try 'pglift role drop --help' for help.
  
  Error: '--drop-owned' and '--reassign-owned' can't be used together
  [2]
  $ pglift role drop test --drop-owned --dry-run
  INFO dropping role 'test'
  INFO removing entries from HBA configuration
  DRY RUN: no changes made
  $ pglift role drop test --drop-owned
  INFO dropping role 'test'
  INFO removing entries from HBA configuration
  $ pglift role create doctor
  INFO creating role 'doctor'
  $ pglift database create tardis_db --owner doctor
  INFO creating 'tardis_db' database in 1\d/main (re)
  $ pglift database get tardis_db --output-format=json | jq -r .owner
  doctor
  $ pglift role drop doctor --reassign-owned=postgres
  INFO dropping role 'doctor'
  $ pglift database get tardis_db --output-format=json | jq -r .owner
  postgres
  $ pglift role create who
  INFO creating role 'who'
  $ pglift database create unit_db --owner who
  INFO creating 'unit_db' database in 1\d/main (re)
  $ pglift database get unit_db --output-format=json | jq -r .owner
  who
  $ pglift role drop who --drop-owned --reassign-owned=postgres
  Usage: pglift role drop [OPTIONS] NAME
  Try 'pglift role drop --help' for help.
  
  Error: '--drop-owned' and '--reassign-owned' can't be used together
  [2]
  $ pglift role drop who --no-drop-owned --reassign-owned=postgres
  INFO dropping role 'who'
  $ pglift database get unit_db --output-format=json | jq -r .owner
  postgres

Profiles
  $ pglift role -i main create dba1 --password mySup3rS3cr3t1377 --login
  INFO creating role 'dba1'
  $ pglift database -i main create db2 --owner dba1 --schema v --schema w
  INFO creating 'db2' database in 1\d/main (re)
  INFO creating schema 'v' in database db2 with owner 'dba1'
  INFO creating schema 'w' in database db2 with owner 'dba1'
  $ pglift role -i main create dba2 --login
  INFO creating role 'dba2'
  $ pglift instance exec main -- psql "dbname=db2 password=mySup3rS3cr3t1377 user=dba1" -t -c 'CREATE TABLE v.capital(city VARCHAR(50))'
  CREATE TABLE
  $ pglift role set-profile nosuchrole --database db2 --schema v read-only
  Error: role 'nosuchrole' not found
  [1]
  $ pglift role set-profile dba2 --database db2 --schema v --schema w read-only
  INFO setting profile 'read-only' for role 'dba2' on schema 'v' in database 'db2'
  INFO setting profile 'read-only' for role 'dba2' on schema 'w' in database 'db2'
  $ pglift database privileges db2 --default --output-format json
  [
    {
      "database": "db2",
      "schema": "v",
      "object_type": "FUNCTION",
      "role": "dba2",
      "privileges": [
        "EXECUTE"
      ]
    },
    {
      "database": "db2",
      "schema": "v",
      "object_type": "SEQUENCE",
      "role": "dba2",
      "privileges": [
        "SELECT"
      ]
    },
    {
      "database": "db2",
      "schema": "v",
      "object_type": "TABLE",
      "role": "dba2",
      "privileges": [
        "SELECT"
      ]
    },
    {
      "database": "db2",
      "schema": "v",
      "object_type": "TYPE",
      "role": "dba2",
      "privileges": [
        "USAGE"
      ]
    },
    {
      "database": "db2",
      "schema": "w",
      "object_type": "FUNCTION",
      "role": "dba2",
      "privileges": [
        "EXECUTE"
      ]
    },
    {
      "database": "db2",
      "schema": "w",
      "object_type": "SEQUENCE",
      "role": "dba2",
      "privileges": [
        "SELECT"
      ]
    },
    {
      "database": "db2",
      "schema": "w",
      "object_type": "TABLE",
      "role": "dba2",
      "privileges": [
        "SELECT"
      ]
    },
    {
      "database": "db2",
      "schema": "w",
      "object_type": "TYPE",
      "role": "dba2",
      "privileges": [
        "USAGE"
      ]
    }
  ]
  $ pglift database privileges db2 -r dba2 --output-format json
  [
    {
      "database": "db2",
      "schema": "v",
      "object_type": "TABLE",
      "role": "dba2",
      "privileges": [
        "SELECT"
      ],
      "object_name": "capital",
      "column_privileges": {}
    }
  ]

Cleanup.
  INFO dropping instance 1\d\/main (re)
  INFO stopping PostgreSQL 1\d\/main (re)
  INFO stopping Prometheus postgres_exporter 1\d-main (re)
  INFO deconfiguring Prometheus postgres_exporter 1\d-main (re)
  INFO deleting pgBackRest stanza 'main'
  INFO deconfiguring pgBackRest stanza 'main'
  INFO removing entries matching port=\d+ from \$TMPDIR\/.pgpass (re)
  INFO deleting PostgreSQL data and WAL directories
  INFO deleting pgBackRest include directory
  INFO uninstalling base pgBackRest configuration
  INFO deleting pgBackRest log directory
  INFO deleting pgBackRest spool directory
  INFO deleting PostgreSQL log directory
  INFO deleting PostgreSQL socket directory (no-eol)
