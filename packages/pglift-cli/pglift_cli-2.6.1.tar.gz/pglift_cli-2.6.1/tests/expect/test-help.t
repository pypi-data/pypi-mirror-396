# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

Tests for --help options of all commands

Site settings

  $ export PGLIFT_CLI__LOG_FORMAT="%(levelname)-4s %(message)s"
  $ export PGLIFT_CONFIG_DIR=$TMPDIR
  $ export PGLIFT_PREFIX=$TMPDIR
  $ export PGLIFT_RUN_PREFIX=$TMPDIR/run

  $ bindir=$TMPDIR/$TESTFILE/bin
  $ mkdir -p $bindir/pgsql/17/bin
  $ touch $bindir/pgsql/17/bin/pg_ctl
  $ chmod +x $bindir/pgsql/17/bin/pg_ctl
  $ export PGLIFT_POSTGRESQL__BINDIR=$bindir/pgsql/{version}/bin \
  >     PGLIFT_POSTGRESQL__AUTH__PASSFILE="null" \
  >     PGLIFT_POSTGRESQL__REPLROLE="replication"
  $ export PGLIFT_PATRONI__EXECPATH=$bindir/patroni \
  >     PGLIFT_PATRONI__CTLPATH=$bindir/patronictl \
  >     PGLIFT_PGBACKREST__EXECPATH=$bindir/pgbackrest \
  >     PGLIFT_PROMETHEUS__EXECPATH=$bindir/postgres_exporter
  $ touch $PGLIFT_PATRONI__EXECPATH \
  >     $PGLIFT_PATRONI__CTLPATH \
  >     $PGLIFT_PGBACKREST__EXECPATH \
  >     $PGLIFT_PROMETHEUS__EXECPATH
  $ export PGLIFT_PGBACKREST__REPOSITORY__MODE=path \
  >     PGLIFT_PGBACKREST__REPOSITORY__PATH=$TMPDIR/$TESTFILE/backups
  $ mkdir $PGLIFT_PGBACKREST__REPOSITORY__PATH
  $ export PGLIFT_POWA='{}'

  $ pglift site-settings --no-defaults -o json \
  >   | jq '.postgresql, .pgbackrest, .prometheus, .prefix, .run_prefix'
  {
    "bindir": "$TMPDIR/*/bin/pgsql/{version}/bin", (glob)
    "versions": [
      {
        "version": "17",
        "bindir": "$TMPDIR/*/bin/pgsql/17/bin" (glob)
      }
    ],
    "auth": {
      "passfile": null
    },
    "replrole": "replication",
    "datadir": "$TMPDIR/srv/pgsql/{version}/{name}/data",
    "waldir": "$TMPDIR/srv/pgsql/{version}/{name}/wal",
    "logpath": "$TMPDIR/log/postgresql",
    "socket_directory": "$TMPDIR/run/postgresql",
    "dumps_directory": "$TMPDIR/srv/dumps/{version}-{name}"
  }
  {
    "execpath": "$TMPDIR/*/bin/pgbackrest", (glob)
    "configpath": "$TMPDIR/etc/pgbackrest",
    "repository": {
      "mode": "path",
      "path": "$TMPDIR/*/backups" (glob)
    },
    "logpath": "$TMPDIR/log/pgbackrest",
    "spoolpath": "$TMPDIR/srv/pgbackrest/spool",
    "lockpath": "$TMPDIR/run/pgbackrest/lock"
  }
  {
    "execpath": "$TMPDIR/*/bin/postgres_exporter", (glob)
    "configpath": "$TMPDIR/etc/prometheus/postgres_exporter-{name}.conf",
    "pid_file": "$TMPDIR/run/prometheus/{name}.pid"
  }
  "$TMPDIR"
  "$TMPDIR/run"

  $ pglift --help
  Usage: pglift [OPTIONS] COMMAND [ARGS]...
  
    Deploy production-ready instances of PostgreSQL
  
  Options:
    -L, --log-level [debug|info|warning|error|critical]
                                    Set log threshold (default to INFO when
                                    logging to stderr or WARNING when logging to
                                    a file).
    -l, --log-file LOGFILE          Write logs to LOGFILE, instead of stderr.
    --interactive / --non-interactive
                                    Interactively prompt for confirmation when
                                    needed (the default), or automatically pick
                                    the default option for all choices.
    --version                       Show program version.
    --completion [bash|fish|zsh]    Output completion for specified shell and
                                    exit.
    --help                          Show this message and exit.
  
  Commands:
    instance           Manage instances.
    pgconf             Manage configuration of a PostgreSQL instance.
    role               Manage roles.
    database           Manage databases.
    pghba              Manage entries in HBA configuration of a PostgreSQL...
    wal                Manage WAL replay of a PostgreSQL instance.
    patroni            Handle Patroni service for an instance.
    postgres_exporter  Handle Prometheus postgres_exporter


Site configuration

  $ pglift site-configure list
  $TMPDIR/etc/pgbackrest/conf.d
  $TMPDIR/etc/pgbackrest/pgbackrest.conf
  $TMPDIR/*/backups (glob)
  $TMPDIR/log/pgbackrest
  $TMPDIR/srv/pgbackrest/spool
  $TMPDIR/log/postgresql
  $ env PGLIFT_LOGGERS='pglift_cli,pglift,filelock' \
  >     pglift --log-level=debug --log-file=$TMPDIR/check.log site-configure check
  [1]
  $ cat $TMPDIR/check.log
  DEBUG Attempting to acquire lock \d+ on \$TMPDIR\/run\/.pglift.lock (re)
  DEBUG Lock \d+ acquired on \$TMPDIR\/run\/.pglift.lock (re)
  ERROR pgBackRest configuration path $TMPDIR/etc/pgbackrest/conf.d missing
  DEBUG Attempting to release lock \d+ on \$TMPDIR\/run\/.pglift.lock (re)
  DEBUG Lock \d+ released on \$TMPDIR\/run\/.pglift.lock (re)

Instance commands

  $ pglift instance --help
  Usage: pglift instance [OPTIONS] COMMAND [ARGS]...
  
    Manage instances.
  
  Options:
    --schema  Print the JSON schema of instance model and exit.
    --help    Show this message and exit.
  
  Commands:
    alter       Alter PostgreSQL INSTANCE
    backup      Back up PostgreSQL INSTANCE
    backups     List available backups for INSTANCE
    create      Initialize a PostgreSQL instance
    demote      Demote PostgreSQL INSTANCE as standby of specified source...
    drop        Drop PostgreSQL INSTANCE
    env         Output environment variables suitable to handle to...
    exec        Execute COMMAND in the libpq environment for PostgreSQL...
    get         Get the description of PostgreSQL INSTANCE.
    list        List the available instances
    logs        Output PostgreSQL logs of INSTANCE.
    privileges  List privileges on INSTANCE's databases.
    promote     Promote standby PostgreSQL INSTANCE
    reload      Reload PostgreSQL INSTANCE
    restart     Restart PostgreSQL INSTANCE
    restore     Restore PostgreSQL INSTANCE
    shell       Start a shell with instance environment.
    start       Start PostgreSQL INSTANCE
    status      Check the status of instance and all satellite components.
    stop        Stop PostgreSQL INSTANCE
    upgrade     Upgrade INSTANCE using pg_upgrade
  $ pglift instance alter --help
  Usage: pglift instance alter [OPTIONS] [INSTANCE]
  
    Alter PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --port PORT                     TCP port the PostgreSQL instance will be
                                    listening to.
    --data-checksums / --no-data-checksums
                                    Enable or disable data checksums. If
                                    unspecified, fall back to site settings
                                    choice.
    --state [started|stopped]       Runtime state.
    --create-slot SLOT              Replication slots to create in this
                                    instance. (Can be used multiple times.)
    --drop-slot SLOT                Replication slots to drop from this
                                    instance. (Can be used multiple times.)
    --powa-password PASSWORD        Password of PostgreSQL role for PoWA.
    --prometheus-port PORT          TCP port for the web interface and telemetry
                                    of Prometheus.
    --prometheus-password PASSWORD  Password of PostgreSQL role for Prometheus
                                    postgres_exporter.
    --patroni-cluster CLUSTER       Name (scope) of the Patroni cluster.
    --patroni-node NODE             Name of the node (usually the host name).
    --patroni-restapi-connect-address CONNECT_ADDRESS
                                    IP address (or hostname) and port, to access
                                    the Patroni's REST API.
    --patroni-restapi-listen LISTEN
                                    IP address (or hostname) and port that
                                    Patroni will listen to for the REST API.
                                    Defaults to connect_address if not provided.
    --patroni-restapi-authentication-username USERNAME
                                    Basic authentication username for Patroni's
                                    REST API.
    --patroni-restapi-authentication-password PASSWORD
                                    Basic authentication password for Patroni's
                                    REST API.
    --patroni-postgresql-connect-host CONNECT_HOST
                                    Host or IP address through which PostgreSQL
                                    is externally accessible.
    --patroni-postgresql-replication-ssl-cert CERT
                                    Client certificate.
    --patroni-postgresql-replication-ssl-key KEY
                                    Private key.
    --patroni-postgresql-replication-ssl-password PASSWORD
                                    Password for the private key.
    --patroni-postgresql-rewind-ssl-cert CERT
                                    Client certificate.
    --patroni-postgresql-rewind-ssl-key KEY
                                    Private key.
    --patroni-postgresql-rewind-ssl-password PASSWORD
                                    Password for the private key.
    --patroni-etcd-username USERNAME
                                    Username for basic authentication to etcd.
    --patroni-etcd-password PASSWORD
                                    Password for basic authentication to etcd.
    --diff                          Include differences resulting from applied
                                    changes in returned result.
    -o, --output-format [json]      Specify the output format.
    --help                          Show this message and exit.
  $ pglift instance create --help
  Usage: pglift instance create [OPTIONS] NAME
  
    Initialize a PostgreSQL instance
  
  Options:
    --version [17|16|15|14|13]      PostgreSQL version; if unspecified,
                                    determined from site settings or most recent
                                    PostgreSQL installation available on site.
    --standby-for DSN               DSN of primary for streaming replication.
    --standby-password PASSWORD     Password for the replication user.
    --standby-slot SLOT             Replication slot name. Must exist on
                                    primary.
    --port PORT                     TCP port the PostgreSQL instance will be
                                    listening to.
    --data-checksums / --no-data-checksums
                                    Enable or disable data checksums. If
                                    unspecified, fall back to site settings
                                    choice.
    --locale LOCALE                 Default locale.
    --encoding ENCODING             Character encoding of the PostgreSQL
                                    instance.
    --auth-local [trust|reject|md5|password|scram-sha-256|sspi|ident|peer|pam|ldap|radius]
                                    Authentication method for local-socket
                                    connections.
    --auth-host [trust|reject|md5|password|scram-sha-256|gss|sspi|ident|pam|ldap|radius]
                                    Authentication method for local TCP/IP
                                    connections.
    --auth-hostssl [trust|reject|md5|password|scram-sha-256|gss|sspi|ident|pam|ldap|radius|cert]
                                    Authentication method for SSL-encrypted
                                    TCP/IP connections.
    --surole-password PASSWORD      Super-user role password.
    --replrole-password PASSWORD    Replication role password.
    --state [started|stopped]       Runtime state.
    --slot SLOT                     Replication slots in this instance (non-
                                    exhaustive list). (Can be used multiple
                                    times.)
    --powa-password PASSWORD        Password of PostgreSQL role for PoWA.
    --prometheus-port PORT          TCP port for the web interface and telemetry
                                    of Prometheus.
    --prometheus-password PASSWORD  Password of PostgreSQL role for Prometheus
                                    postgres_exporter.
    --patroni-cluster CLUSTER       Name (scope) of the Patroni cluster.
    --patroni-node NODE             Name of the node (usually the host name).
    --patroni-restapi-connect-address CONNECT_ADDRESS
                                    IP address (or hostname) and port, to access
                                    the Patroni's REST API.
    --patroni-restapi-listen LISTEN
                                    IP address (or hostname) and port that
                                    Patroni will listen to for the REST API.
                                    Defaults to connect_address if not provided.
    --patroni-restapi-authentication-username USERNAME
                                    Basic authentication username for Patroni's
                                    REST API.
    --patroni-restapi-authentication-password PASSWORD
                                    Basic authentication password for Patroni's
                                    REST API.
    --patroni-postgresql-connect-host CONNECT_HOST
                                    Host or IP address through which PostgreSQL
                                    is externally accessible.
    --patroni-postgresql-replication-ssl-cert CERT
                                    Client certificate.
    --patroni-postgresql-replication-ssl-key KEY
                                    Private key.
    --patroni-postgresql-replication-ssl-password PASSWORD
                                    Password for the private key.
    --patroni-postgresql-rewind-ssl-cert CERT
                                    Client certificate.
    --patroni-postgresql-rewind-ssl-key KEY
                                    Private key.
    --patroni-postgresql-rewind-ssl-password PASSWORD
                                    Password for the private key.
    --patroni-etcd-username USERNAME
                                    Username for basic authentication to etcd.
    --patroni-etcd-password PASSWORD
                                    Password for basic authentication to etcd.
    --pgbackrest-stanza STANZA      Name of pgBackRest stanza. Something
                                    describing the actual function of the
                                    instance, such as 'app'.
    --pgbackrest-password PASSWORD  Password of PostgreSQL role for pgBackRest.
    --drop-on-error / --no-drop-on-error
                                    On error, drop partially initialized
                                    instance by possibly rolling back operations
                                    (true by default).
    --help                          Show this message and exit.
  $ pglift instance drop --help
  Usage: pglift instance drop [OPTIONS] [INSTANCE]...
  
    Drop PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --help  Show this message and exit.
  $ pglift instance env --help
  Usage: pglift instance env [OPTIONS] [INSTANCE]
  
    Output environment variables suitable to handle to PostgreSQL INSTANCE.
  
    This can be injected in shell using:
  
        export $(pglift instance env myinstance)
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift instance exec --help
  Usage: pglift instance exec [OPTIONS] INSTANCE COMMAND...
  
    Execute COMMAND in the libpq environment for PostgreSQL INSTANCE.
  
    COMMAND parts may need to be prefixed with -- to separate them from options
    when confusion arises.
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
  
  Options:
    --help  Show this message and exit.
  $ pglift instance shell --help
  Usage: pglift instance shell [OPTIONS] [INSTANCE]
  
    Start a shell with instance environment.
  
    Unless --shell option is specified, the $SHELL environment variable is used
    to guess which shell executable to use.
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --shell FILE  Path to shell executable
    --help        Show this message and exit.
  $ pglift instance list --help
  Usage: pglift instance list [OPTIONS]
  
    List the available instances
  
  Options:
    --version [17|16|15|14|13]  Only list instances of specified version.
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift instance logs --help
  Usage: pglift instance logs [OPTIONS] [INSTANCE]
  
    Output PostgreSQL logs of INSTANCE.
  
    This assumes that the PostgreSQL instance is configured to use file-based
    logging (i.e. log_destination amongst 'stderr' or 'csvlog').
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    -f, --follow / --no-follow  Follow log output.
    --help                      Show this message and exit.
  $ pglift instance get --help
  Usage: pglift instance get [OPTIONS] [INSTANCE]
  
    Get the description of PostgreSQL INSTANCE.
  
    Unless --output-format is specified, 'settings' and 'state' fields are not
    shown as well as 'standby' information if INSTANCE is not a standby.
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift instance privileges --help
  Usage: pglift instance privileges [OPTIONS] [INSTANCE]
  
    List privileges on INSTANCE's databases.
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    -d, --database TEXT         Database to inspect. When not provided, all
                                databases are inspected.
    -r, --role TEXT             Role to inspect
    --default                   Display default privileges
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift instance promote --help
  Usage: pglift instance promote [OPTIONS] [INSTANCE]
  
    Promote standby PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --help  Show this message and exit.
  $ pglift instance demote --help
  Usage: pglift instance demote [OPTIONS] [INSTANCE] [REWIND_OPTS]...
  
    Demote PostgreSQL INSTANCE as standby of specified source server using
    pg_rewind.
  
    The instance must not be running and it may be started at the end of the
    "demotion" process.
  
    Extra options can be passed to the pg_rewind command. They may need to be
    prefixed with -- to separate them from the current command options when
    confusion arises. When using extra options, providing the instance
    identifier is required.
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --from TEXT           DSN of source server to synchronize from.  [required]
    --password PASSWORD   Password for the rewind user.
    --start / --no-start  Start the instance at the end of the demotion process
                          [default: start]
    --help                Show this message and exit.
  $ pglift instance reload --help
  Usage: pglift instance reload [OPTIONS] [INSTANCE]...
  
    Reload PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --all   Reload all instances.
    --help  Show this message and exit.
  $ pglift instance restart --help
  Usage: pglift instance restart [OPTIONS] [INSTANCE]...
  
    Restart PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --all   Restart all instances.
    --help  Show this message and exit.
  $ pglift instance start --help
  Usage: pglift instance start [OPTIONS] [INSTANCE]...
  
    Start PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --foreground  Start the program in foreground.
    --all         Start all instances.
    --help        Show this message and exit.
  $ pglift instance status --help
  Usage: pglift instance status [OPTIONS] [INSTANCE]
  
    Check the status of instance and all satellite components.
  
    Output the status string value ('running', 'not running') for each
    component. If not all services are running, the command exit code will be 3.
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --help  Show this message and exit.
  $ pglift instance stop --help
  Usage: pglift instance stop [OPTIONS] [INSTANCE]...
  
    Stop PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --all   Stop all instances.
    --help  Show this message and exit.
  $ pglift instance upgrade --help
  Usage: pglift instance upgrade [OPTIONS] [INSTANCE] [EXTRA_OPTS]...
  
    Upgrade INSTANCE using pg_upgrade
  
    Extra options can be passed to the pg_upgrade command. They may need to be
    prefixed with -- to separate them from the current command options when
    confusion arises. When using extra options, providing the instance
    identifier is required.
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --version [17|16|15|14|13]  PostgreSQL version of the new instance (default
                                to site-configured value).
    --name TEXT                 Name of the new instance (default to old
                                instance name).
    --port INTEGER              Port of the new instance.
    --help                      Show this message and exit.
  $ pglift instance backup --help
  Usage: pglift instance backup [OPTIONS] [INSTANCE]
  
    Back up PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --type [full|incr|diff]  Backup type
    --help                   Show this message and exit.
  $ pglift instance backups --help
  Usage: pglift instance backups [OPTIONS] [INSTANCE]
  
    List available backups for INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift instance restore --help
  Usage: pglift instance restore [OPTIONS] [INSTANCE]
  
    Restore PostgreSQL INSTANCE
  
    INSTANCE identifies target instance as <version>/<name> where the <version>/
    prefix may be omitted if there is only one instance matching <name>.
    Required if there is more than one instance on system.
  
  Options:
    --label TEXT                    Label of backup to restore
    --date [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
                                    Date of backup to restore
    --help                          Show this message and exit.

Role commands

  $ pglift role --help
  Usage: pglift role [OPTIONS] COMMAND [ARGS]...
  
    Manage roles.
  
  Options:
    -i, --instance <version>/<name>
                                    Instance identifier; the <version>/ prefix
                                    may be omitted if there's only one instance
                                    matching <name>. Required if there is more
                                    than one instance on system.
    --schema                        Print the JSON schema of role model and
                                    exit.
    --help                          Show this message and exit.
  
  Commands:
    alter        Alter a role in a PostgreSQL instance
    create       Create a role in a PostgreSQL instance
    drop         Drop a role
    get          Get the description of a role
    list         List roles in instance
    privileges   List privileges of a role.
    set-profile  Set profile (read-only, read-write) for a specific role...
  $ pglift role alter --help
  Usage: pglift role alter [OPTIONS] ROLNAME
  
    Alter a role in a PostgreSQL instance
  
  Options:
    --password PASSWORD             Role password.
    --encrypted-password ENCRYPTED_PASSWORD
                                    Role password, already encrypted.
    --inherit / --no-inherit        Let the role inherit the privileges of the
                                    roles it is a member of.
    --login / --no-login            Allow the role to log in.
    --superuser / --no-superuser    Whether the role is a superuser.
    --createdb / --no-createdb      Whether role can create new databases.
    --createrole / --no-createrole  Whether role can create new roles.
    --replication / --no-replication
                                    Whether the role is a replication role.
    --connection-limit CONNECTION_LIMIT
                                    How many concurrent connections the role can
                                    make.
    --valid-until VALID_UNTIL       Date and time after which the role's
                                    password is no longer valid.
    --validity VALIDITY             DEPRECATED. Use 'valid_until' instead.
    --grant ROLE                    Grant membership of the given role. (Can be
                                    used multiple times.)
    --revoke ROLE                   Revoke membership of the given role. (Can be
                                    used multiple times.)
    --dry-run                       Simulate change operations.
    --help                          Show this message and exit.
  $ pglift role create --help
  Usage: pglift role create [OPTIONS] NAME
  
    Create a role in a PostgreSQL instance
  
  Options:
    --password PASSWORD             Role password.
    --encrypted-password ENCRYPTED_PASSWORD
                                    Role password, already encrypted.
    --inherit / --no-inherit        Let the role inherit the privileges of the
                                    roles it is a member of.
    --login / --no-login            Allow the role to log in.
    --superuser / --no-superuser    Whether the role is a superuser.
    --createdb / --no-createdb      Whether role can create new databases.
    --createrole / --no-createrole  Whether role can create new roles.
    --replication / --no-replication
                                    Whether the role is a replication role.
    --connection-limit CONNECTION_LIMIT
                                    How many concurrent connections the role can
                                    make.
    --valid-until VALID_UNTIL       Date and time after which the role's
                                    password is no longer valid.
    --validity VALIDITY             DEPRECATED. Use 'valid_until' instead.
    --in-role ROLE                  Roles which this role should be a member of.
                                    (Can be used multiple times.)
    --dry-run                       Simulate change operations.
    --help                          Show this message and exit.
  $ pglift role drop --help
  Usage: pglift role drop [OPTIONS] NAME
  
    Drop a role
  
  Options:
    --drop-owned / --no-drop-owned  Drop all PostgreSQL's objects owned by the
                                    role being dropped.
    --reassign-owned REASSIGN_OWNED
                                    Reassign all PostgreSQL's objects owned by
                                    the role being dropped to the specified role
                                    name.
    --dry-run                       Simulate change operations.
    --help                          Show this message and exit.
  $ pglift role get --help
  Usage: pglift role get [OPTIONS] NAME
  
    Get the description of a role
  
  Options:
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift role list --help
  Usage: pglift role list [OPTIONS]
  
    List roles in instance
  
  Options:
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift role privileges --help
  Usage: pglift role privileges [OPTIONS] NAME
  
    List privileges of a role.
  
  Options:
    -d, --database TEXT         Database to inspect
    --default                   Display default privileges
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.

Database commands

  $ pglift database --help
  Usage: pglift database [OPTIONS] COMMAND [ARGS]...
  
    Manage databases.
  
  Options:
    -i, --instance <version>/<name>
                                    Instance identifier; the <version>/ prefix
                                    may be omitted if there's only one instance
                                    matching <name>. Required if there is more
                                    than one instance on system.
    --schema                        Print the JSON schema of database model and
                                    exit.
    --help                          Show this message and exit.
  
  Commands:
    alter       Alter a database in a PostgreSQL instance
    create      Create a database in a PostgreSQL instance
    drop        Drop a database
    dump        Dump a database
    dumps       List the database dumps
    get         Get the description of a database
    list        List databases (all or specified ones)
    privileges  List privileges on a database.
    restore     Restore a database dump
    run         Run given command on databases of a PostgreSQL instance
  $ pglift database alter --help
  Usage: pglift database alter [OPTIONS] DBNAME
  
    Alter a database in a PostgreSQL instance
  
  Options:
    --owner OWNER                 The role name of the user who will own the
                                  database.
    --add-schema SCHEMA           Schemas to add to this database. (Can be used
                                  multiple times.)
    --remove-schema SCHEMA        Schemas to remove from this database. (Can be
                                  used multiple times.)
    --add-extension EXTENSION     Extensions to add to this database. (Can be
                                  used multiple times.)
    --remove-extension EXTENSION  Extensions to remove from this database. (Can
                                  be used multiple times.)
    --tablespace TABLESPACE       The name of the tablespace that will be
                                  associated with the database.
    --dry-run                     Simulate change operations.
    --help                        Show this message and exit.
  $ pglift database create --help
  Usage: pglift database create [OPTIONS] NAME
  
    Create a database in a PostgreSQL instance
  
  Options:
    --owner OWNER                   The role name of the user who will own the
                                    database.
    --schema SCHEMA                 Schemas in this database. (Can be used
                                    multiple times.)
    --extension EXTENSION           Extensions in this database. (Can be used
                                    multiple times.)
    --locale LOCALE                 Locale for this database. Database will be
                                    created from template0 if the locale differs
                                    from the one set for template1.
    --clone-from CONNINFO           Data source name of the database to restore
                                    into this one, specified as a libpq
                                    connection URI.
    --clone-schema-only / --no-clone-schema-only
                                    Only restore the schema (data definitions).
    --tablespace TABLESPACE         The name of the tablespace that will be
                                    associated with the database.
    --dry-run                       Simulate change operations.
    --help                          Show this message and exit.
  $ pglift database drop --help
  Usage: pglift database drop [OPTIONS] NAME
  
    Drop a database
  
  Options:
    --force / --no-force  Force the drop.
    --dry-run             Simulate change operations.
    --help                Show this message and exit.
  $ pglift database dump --help
  Usage: pglift database dump [OPTIONS] DBNAME
  
    Dump a database
  
  Options:
    -o, --output DIRECTORY  Write dump file(s) to DIRECTORY instead of default
                            dumps directory.
    --dry-run               Simulate change operations.
    --help                  Show this message and exit.
  $ pglift database dumps --help
  Usage: pglift database dumps [OPTIONS] [DBNAME]...
  
    List the database dumps
  
    Only dumps created in the default dumps directory are listed.
  
  Options:
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift database restore --help
  Usage: pglift database restore [OPTIONS] DUMP_ID [TARGETDBNAME]
  
    Restore a database dump
  
    DUMP_ID identifies the dump id.
  
    TARGETDBNAME identifies the (optional) name of the database in which the
    dump is reloaded. If provided, the database needs to be created beforehand.
  
    If TARGETDBNAME is not provided, the dump is reloaded using the database
    name that appears in the dump. In this case, the restore command will create
    the database so it needs to be dropped before running the command.
  
  Options:
    --dry-run  Simulate change operations.
    --help     Show this message and exit.
  $ pglift database get --help
  Usage: pglift database get [OPTIONS] NAME
  
    Get the description of a database
  
  Options:
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift database list --help
  Usage: pglift database list [OPTIONS] [DBNAME]...
  
    List databases (all or specified ones)
  
    Only queried databases are shown when DBNAME is specified.
  
  Options:
    -o, --output-format [json]   Specify the output format.
    -x, --exclude-database TEXT  Database to exclude from listing.
    --help                       Show this message and exit.
  $ pglift database privileges --help
  Usage: pglift database privileges [OPTIONS] NAME
  
    List privileges on a database.
  
  Options:
    -r, --role TEXT             Role to inspect
    --default                   Display default privileges
    -o, --output-format [json]  Specify the output format.
    --help                      Show this message and exit.
  $ pglift database run --help
  Usage: pglift database run [OPTIONS] SQL_COMMAND
  
    Run given command on databases of a PostgreSQL instance
  
  Options:
    -d, --database TEXT          Database to run command on
    -x, --exclude-database TEXT  Database to not run command on
    -o, --output-format [json]   Specify the output format.
    --help                       Show this message and exit.

PostgreSQL configuration commands

  $ pglift pgconf --help
  Usage: pglift pgconf [OPTIONS] COMMAND [ARGS]...
  
    Manage configuration of a PostgreSQL instance.
  
  Options:
    -i, --instance <version>/<name>
                                    Instance identifier; the <version>/ prefix
                                    may be omitted if there's only one instance
                                    matching <name>. Required if there is more
                                    than one instance on system.
    --help                          Show this message and exit.
  
  Commands:
    edit    Edit managed configuration.
    remove  Remove configuration items.
    set     Set configuration items.
    show    Show configuration (all parameters or specified ones).
  $ pglift pgconf edit --help
  Usage: pglift pgconf edit [OPTIONS]
  
    Edit managed configuration.
  
  Options:
    --help  Show this message and exit.
  $ pglift pgconf remove --help
  Usage: pglift pgconf remove [OPTIONS] PARAMETERS...
  
    Remove configuration items.
  
  Options:
    --dry-run  Simulate change operations.
    --help     Show this message and exit.
  $ pglift pgconf set --help
  Usage: pglift pgconf set [OPTIONS] <PARAMETER>=<VALUE>...
  
    Set configuration items.
  
  Options:
    --dry-run  Simulate change operations.
    --help     Show this message and exit.
  $ pglift pgconf show --help
  Usage: pglift pgconf show [OPTIONS] [PARAMETER]...
  
    Show configuration (all parameters or specified ones).
  
    Only uncommented parameters are shown when no PARAMETER is specified. When
    specific PARAMETERs are queried, commented values are also shown.
  
  Options:
    --help  Show this message and exit.

pg_hba.conf management commands

  $ pglift pghba --help
  Usage: pglift pghba [OPTIONS] COMMAND [ARGS]...
  
    Manage entries in HBA configuration of a PostgreSQL instance.
  
  Options:
    -i, --instance <version>/<name>
                                    Instance identifier; the <version>/ prefix
                                    may be omitted if there's only one instance
                                    matching <name>. Required if there is more
                                    than one instance on system.
    --help                          Show this message and exit.
  
  Commands:
    add     Add a record in HBA configuration.
    edit    Edit managed HBA records.
    remove  Remove a record from HBA configuration.
  $ pglift pghba add --help
  Usage: pglift pghba add [OPTIONS]
  
    Add a record in HBA configuration.
  
    If no --connection-* option is specified, a 'local' record is added.
  
  Options:
    --connection-type [host|hostssl|hostnossl|hostgssenc|hostnogssenc]
                                    Connection type.
    --connection-address ADDRESS    Client machine address(es); can be either a
                                    hostname, an IP or an IP address range.
    --connection-netmask NETMASK    Client machine netmask.
    --database DATABASE             Database name(s). Multiple database names
                                    can be supplied by separating them with
                                    commas.
    --method TEXT                   Authentication method.  [required]
    --user USER                     User name(s). Multiple user names can be
                                    supplied by separating them with commas.
    --dry-run                       Simulate change operations.
    --diff                          Include differences resulting from applied
                                    changes in returned result.
    --help                          Show this message and exit.
  $ pglift pghba remove --help
  Usage: pglift pghba remove [OPTIONS]
  
    Remove a record from HBA configuration.
  
    If no --connection-* option is specified, a 'local' record is removed.
  
  Options:
    --connection-type [host|hostssl|hostnossl|hostgssenc|hostnogssenc]
                                    Connection type.
    --connection-address ADDRESS    Client machine address(es); can be either a
                                    hostname, an IP or an IP address range.
    --connection-netmask NETMASK    Client machine netmask.
    --database DATABASE             Database name(s). Multiple database names
                                    can be supplied by separating them with
                                    commas.
    --method TEXT                   Authentication method.  [required]
    --user USER                     User name(s). Multiple user names can be
                                    supplied by separating them with commas.
    --dry-run                       Simulate change operations.
    --diff                          Include differences resulting from applied
                                    changes in returned result.
    --help                          Show this message and exit.
  $ pglift pghba edit --help
  Usage: pglift pghba edit [OPTIONS]
  
    Edit managed HBA records.
  
  Options:
    --help  Show this message and exit.

Patroni commands:

  $ pglift patroni --help
  Usage: pglift patroni [OPTIONS] COMMAND [ARGS]...
  
    Handle Patroni service for an instance.
  
  Options:
    -i, --instance <version>/<name>
                                    Instance identifier; the <version>/ prefix
                                    may be omitted if there's only one instance
                                    matching <name>. Required if there is more
                                    than one instance on system.
    --help                          Show this message and exit.
  
  Commands:
    logs  Output Patroni logs.
  $ pglift patroni logs --help
  Usage: pglift patroni logs [OPTIONS]
  
    Output Patroni logs.
  
  Options:
    --help  Show this message and exit.

  $ pglift postgres_exporter --help
  Usage: pglift postgres_exporter [OPTIONS] COMMAND [ARGS]...
  
    Handle Prometheus postgres_exporter
  
  Options:
    --schema  Print the JSON schema of postgres_exporter model and exit.
    --help    Show this message and exit.
  
  Commands:
    apply      Apply manifest as a Prometheus postgres_exporter.
    install    Install the service for a (non-local) instance.
    start      Start postgres_exporter service NAME.
    stop       Stop postgres_exporter service NAME.
    uninstall  Uninstall the service.
  $ pglift postgres_exporter apply --help
  Usage: pglift postgres_exporter apply [OPTIONS]
  
    Apply manifest as a Prometheus postgres_exporter.
  
  Options:
    -f, --file MANIFEST         [required]
    -o, --output-format [json]  Specify the output format.
    --diff                      Include differences resulting from applied
                                changes in returned result.
    --dry-run                   Simulate change operations.
    --help                      Show this message and exit.
  $ pglift postgres_exporter install --help
  Usage: pglift postgres_exporter install [OPTIONS] NAME DSN PORT
  
    Install the service for a (non-local) instance.
  
  Options:
    --password PASSWORD        Connection password.
    --state [started|stopped]  Runtime state.
    --help                     Show this message and exit.
  $ pglift postgres_exporter start --help
  Usage: pglift postgres_exporter start [OPTIONS] NAME
  
    Start postgres_exporter service NAME.
  
    The NAME argument is a local identifier for the postgres_exporter service.
    If the service is bound to a local instance, it should be <version>-<name>.
  
  Options:
    --foreground  Start the program in foreground.
    --help        Show this message and exit.
  $ pglift postgres_exporter stop --help
  Usage: pglift postgres_exporter stop [OPTIONS] NAME
  
    Stop postgres_exporter service NAME.
  
    The NAME argument is a local identifier for the postgres_exporter service.
    If the service is bound to a local instance, it should be <version>-<name>.
  
  Options:
    --help  Show this message and exit.
  $ pglift postgres_exporter uninstall --help
  Usage: pglift postgres_exporter uninstall [OPTIONS] NAME
  
    Uninstall the service.
  
  Options:
    --help  Show this message and exit.

WAL commands

  $ pglift wal --help
  Usage: pglift wal [OPTIONS] COMMAND [ARGS]...
  
    Manage WAL replay of a PostgreSQL instance.
  
  Options:
    -i, --instance <version>/<name>
                                    Instance identifier; the <version>/ prefix
                                    may be omitted if there's only one instance
                                    matching <name>. Required if there is more
                                    than one instance on system.
    --help                          Show this message and exit.
  
  Commands:
    pause-replay   Pause WAL replay on PostgreSQL standby INSTANCE
    resume-replay  Resume WAL replay on PostgreSQL standby INSTANCE
