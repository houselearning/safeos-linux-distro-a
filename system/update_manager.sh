#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: safeos-update check|apply" >&2
	exit 64
}

[[ $# -eq 1 ]] || usage
command -v apt-get >/dev/null 2>&1 || {
	echo "safeos-update requires Debian apt-get" >&2
	exit 69
}
if [[ $EUID -ne 0 ]]; then
	echo "Run 'sudo safeos-update $1' to use the Debian package manager" >&2
	exit 77
fi

case "$1" in
	check)
		apt-get update
		apt-get --simulate upgrade
		;;
	apply)
		apt-get update
		apt-get --yes full-upgrade
		;;
	*)
		usage
		;;
esac
