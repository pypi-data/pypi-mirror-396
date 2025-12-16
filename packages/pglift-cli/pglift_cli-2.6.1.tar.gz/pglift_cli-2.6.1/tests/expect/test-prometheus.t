# SPDX-FileCopyrightText: 2023 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

  $ export PGLIFT_CLI__LOG_FORMAT="%(levelname)-4s %(message)s"
  $ export PGLIFT_PREFIX=$TMPDIR
  $ export PGLIFT_RUN_PREFIX=$TMPDIR/run
  $ export PGLIFT_POSTGRESQL__AUTH__PASSFILE="null"
  $ export PGLIFT_PROMETHEUS__EXECPATH=$(command -v postgres_exporter || command -v prometheus-postgres-exporter)
  $ PGEPORT=$(port-for prometheus)

  $ alias pglift="pglift --log-level=info"

  $ pglift site-configure install
  INFO creating PostgreSQL log directory: $TMPDIR/log/postgresql
  $ trap "pglift --non-interactive site-configure uninstall; \
  >   port-for -u prometheus" \
  >   EXIT

  $ pglift postgres_exporter install test dbname=monitoring $PGEPORT
  INFO configuring Prometheus postgres_exporter test
  INFO starting Prometheus postgres_exporter test
  $ pglift postgres_exporter stop test
  INFO stopping Prometheus postgres_exporter test
  $ pglift postgres_exporter start test
  INFO starting Prometheus postgres_exporter test
  $ cat > $TMPDIR/prometheus.yaml <<EOF
  > name: test
  > port: $PGEPORT
  > dsn: dbname=monitoring user=prometheus
  > EOF
  $ pglift postgres_exporter apply -f $TMPDIR/prometheus.yaml -o json --dry-run
  {
    "change_state": null,
    "diff": null
  }
  $ pglift postgres_exporter apply -f $TMPDIR/prometheus.yaml --ansible-diff -o json
  INFO reconfiguring Prometheus postgres_exporter test
  INFO restarting Prometheus postgres_exporter test
  INFO starting Prometheus postgres_exporter test
  {
    "change_state": "changed",
    "diff": [
      {
        "before_header": "$TMPDIR/etc/prometheus/postgres_exporter-test.conf",
        "after_header": "$TMPDIR/etc/prometheus/postgres_exporter-test.conf",
        "before": "DATA_SOURCE_NAME=postgresql://:5432/monitoring\nPOSTGRES_EXPORTER_OPTS='--web.listen-address :* --log.level info'", (glob)
        "after": "DATA_SOURCE_NAME=postgresql://prometheus@:5432/monitoring\nPOSTGRES_EXPORTER_OPTS='--web.listen-address :* --log.level info'" (glob)
      },
      {
        "before_header": "$TMPDIR/run/prometheus/test.pid deleted",
        "after_header": "/dev/null",
        "before": "\d+" (re)
      },
      {
        "before_header": "/dev/null",
        "after_header": "$TMPDIR/run/prometheus new directory"
      },
      {
        "before_header": "/dev/null",
        "after_header": "$TMPDIR/run/prometheus/test.pid created",
        "after": "\d+" (re)
      }
    ]
  }

Check port conflicts

  $ cat > $TMPDIR/prometheus.yaml <<EOF
  > name: conflictingport
  > port: $PGEPORT
  > dsn: dbname=monitoring
  > EOF
  $ pglift postgres_exporter apply -f $TMPDIR/prometheus.yaml -o json
  [
    {
      "type": "value_error",
      "loc": [
        "port"
      ],
      "msg": "Value error, port \d+ already in use", (re)
      "input": \d+ (re)
    }
  ]
  Error: 1 validation error for PostgresExporter
  port
    Value error, port \d+ already in use .+ (re)
      For further information visit * (glob)
  [1]
  $ pglift postgres_exporter install conflictingport dbname=monitoring $PGEPORT
  Usage: pglift postgres_exporter install [OPTIONS] NAME DSN PORT
  Try 'pglift postgres_exporter install --help' for help.
  
  Error: Invalid value for 'PORT': port \d+ already in use (re)
  [2]

  $ pglift postgres_exporter uninstall test
  INFO dropping postgres_exporter service 'test'
  INFO stopping Prometheus postgres_exporter test
  INFO deconfiguring Prometheus postgres_exporter test

(cleanup)
  INFO deleting PostgreSQL log directory (no-eol)
