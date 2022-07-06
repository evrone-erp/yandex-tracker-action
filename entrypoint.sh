#!/bin/sh

set -eux

cd "${GITHUB_WORKSPACE}" || exit 1

exec $@
