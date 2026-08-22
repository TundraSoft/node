#!/usr/bin/env bash
# Smoke test for the tundrasoft/node image. Boots via the s6 entrypoint, so each
# check also proves s6 came up. Usage: tests/smoke.sh <image> [expected-node-version]
set -euo pipefail

IMG="${1:?usage: smoke.sh <image> [expected-node-version]}"
EXPECTED_NODE="${2:-}"
FIX="$(cd "$(dirname "$0")/fixtures" && pwd)"

fail() { printf '\033[31mFAIL\033[0m %s\n' "$*" >&2; exit 1; }
pass() { printf '\033[32mPASS\033[0m %s\n' "$*"; }

# Poll a container's logs for a pattern, up to <timeout> seconds.
wait_log() {
  cid="$1"; pat="$2"; t="${3:-20}"; i=0
  while [ "$i" -lt "$t" ]; do
    if docker logs "$cid" 2>&1 | grep -qF "$pat"; then return 0; fi
    i=$((i + 1)); sleep 1
  done
  return 1
}

# Boot detached, wait for <marker>, echo the logs, always clean up. Args after
# marker/timeout go to `docker run`.
boot_expect() {
  marker="$1"; timeout="$2"; shift 2
  cid="$(docker run -d -e S6_VERBOSITY=1 "$@" "$IMG")"
  if wait_log "$cid" "$marker" "$timeout"; then
    docker logs "$cid" 2>&1
    docker rm -f "$cid" >/dev/null
    return 0
  fi
  docker logs "$cid" >&2 2>&1 || true
  docker rm -f "$cid" >/dev/null
  return 1
}

# 1. Node version. Bypass the s6 entrypoint (--entrypoint="") so node runs
#    directly with the image's LD_LIBRARY_PATH; s6 does not propagate it to an
#    arbitrary CMD, only to the service via with-contenv.
if [ -n "$EXPECTED_NODE" ]; then
  docker run --rm --entrypoint="" "$IMG" node --version | grep -qF "v$EXPECTED_NODE" \
    || fail "node --version does not report 'v$EXPECTED_NODE'"
  pass "node reports version $EXPECTED_NODE"
else
  docker run --rm --entrypoint="" "$IMG" node --version | grep -q '^v' \
    || fail "node --version produced no output"
  pass "node binary runs"
fi

# npm/npx are symlinks into /usr/local/lib/node_modules/npm with a
# `#!/usr/bin/env node` shebang; this proves the symlink + shebang resolve.
docker run --rm --entrypoint="" "$IMG" npm --version | grep -qE '^[0-9]+\.' \
  || fail "npm --version produced no output"
pass "npm runs"

# 2. Default service boots the welcome app, stays up, and serves HTTP on 8080
cid="$(docker run -d -e S6_VERBOSITY=1 "$IMG")"
if ! wait_log "$cid" 'Welcome to Node' 20; then
  docker logs "$cid" >&2 2>&1 || true
  docker rm -f "$cid" >/dev/null
  fail "default container did not print the welcome banner"
fi
body="$(docker exec "$cid" wget -qO- http://127.0.0.1:8080/ 2>/dev/null || true)"
docker rm -f "$cid" >/dev/null
printf '%s\n' "$body" | grep -qF 'Welcome to Node' \
  || fail "default server did not respond on :8080 (got: '$body')"
pass "default service boots and serves HTTP"

# 3. FILE mode: runs the mounted file with the container env visible, as tundra
logs="$(boot_expect 'ready' 20 -v "$FIX/app:/smoke:ro" -e FILE=/smoke/env.js -e SMOKE_VAR=hello)" \
  || fail "FILE mode produced no marker"
printf '%s\n' "$logs" | grep -qF 'SMOKE_ENV=hello' \
  || fail "FILE mode should see SMOKE_VAR from the environment"
pass "FILE mode runs the file"

printf '%s\n' "$logs" | grep -qF 'SMOKE_UID=1000' \
  || fail "service should run as tundra (uid 1000)"
pass "service runs as tundra (uid 1000)"

# 4. SCRIPT mode: mount package.json read-only into /app. A writable host copy is
#    avoided because the container chowns /app to tundra, which would leave the
#    host tempdir unremovable under a sticky /tmp (breaks CI cleanup).
logs="$(boot_expect 'SMOKE_SCRIPT_OK' 25 -v "$FIX/script/package.json:/app/package.json:ro" -e SCRIPT=start)" \
  || fail "SCRIPT mode did not run the script"
printf '%s\n' "$logs" | grep -qF 'SMOKE_SCRIPT_OK' || fail "SCRIPT mode marker missing"
pass "SCRIPT mode runs npm run"

echo
pass "all smoke tests passed for $IMG"
