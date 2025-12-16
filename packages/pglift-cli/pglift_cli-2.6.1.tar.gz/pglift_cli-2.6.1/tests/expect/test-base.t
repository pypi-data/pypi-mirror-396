# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

Base tests for the command line interface

  $ pglift --version
  pglift version (\d\.).* (re)

Create an invalid configuration file and adapt PGLIFT_CONFIG_DIR to use it

  $ export PGLIFT_CONFIG_DIR=$TMPDIR/test-base/
  $ mkdir $PGLIFT_CONFIG_DIR
  $ echo "in va lid" > $PGLIFT_CONFIG_DIR/settings.yaml

Calling --version does not load site settings

  $ pglift --version
  pglift version (\d\.).* (re)

Calling 'site-settings' loads site settings

  $ pglift site-settings
  Error: invalid site settings
  invalid site settings: dictionary update sequence element #0 has length 1; 2 is required
  [1]

Calling --help load site settings (because all commands need to be collected)

  $ pglift --help
  Error: invalid site settings
  invalid site settings: dictionary update sequence element #0 has length 1; 2 is required
  [1]
