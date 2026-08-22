# HANDOFF — tundrasoft/node

Status as of 2026-08-23: repo created, image builds and passes its smoke suite locally on
`linux/arm64` (plus a `linux/amd64` cross-build probe). Nothing has run in GitHub Actions yet.

## What this is

`tundrasoft/node` is the Node.js sibling of `tundrasoft/deno` and `tundrasoft/bun`: official
Node.js LTS binaries on `tundrasoft/alpine` (Alpine + s6-overlay + unprivileged `tundra`
UID/GID 1000). The repo tree, workflows, templates, and scripts mirror `TundraSoft/deno`
one-for-one; only runtime-specific parts differ (listed below).

## Why the glibc shim (the one real design decision)

Node's official Linux tarballs are glibc-linked, exactly like Deno's. Alpine ships musl. The
Dockerfile therefore follows the **deno** pattern, not bun's (bun ships native musl builds):

1. `FROM gcr.io/distroless/cc-debian12 AS cc` — source of glibc.
2. Stage `sym`: copy `ld-linux-*` into `/usr/local/lib` and create loader symlinks in `/tmp/lib`.
3. Final stage: `COPY /lib/*-linux-gnu/* -> /usr/local/lib/` (glibc + libgcc_s), then
   `/tmp/lib -> /lib` and `/lib64` (so the ELF interpreter path resolves), with
   `LD_LIBRARY_PATH=/usr/local/lib:/lib:/lib64`.

**Node-specific addition (not in deno):** Node is C++ and needs `libstdc++.so.6`, which
distroless keeps under `/usr/lib/*-linux-gnu/` (deno, being Rust, only needed `libgcc_s` from
`/lib`). The Dockerfile adds one targeted line:

```dockerfile
COPY --from=cc --chown=root:root --chmod=755 /usr/lib/*-linux-gnu/libstdc++.so.6* /usr/local/lib/
```

Do **not** widen that to `/usr/lib/*-linux-gnu/*`: that directory also holds distroless's
glibc-linked `libssl.so.3`/`libcrypto.so.3`, which would shadow Alpine's musl OpenSSL through
`LD_LIBRARY_PATH` and break `apk` and `wget https://` inside the image. Verified: with the
targeted copy, `apk --version` and `wget -qO- https://nodejs.org/...` both work.

## Install layout

- `/usr/local/bin/node` (from the tarball's `bin/node`, chmod 0755, chowned via `setgroup` as
  deno does for `/bin/deno`)
- `/usr/local/lib/node_modules/npm` + symlinks `/usr/local/bin/npm` and `/usr/local/bin/npx`
  (same relative targets as the tarball: `../lib/node_modules/npm/bin/{npm,npx}-cli.js`)
- `/npm-cache` = `NPM_CONFIG_CACHE`, created at build and chowned to `tundra` at boot by the
  `config-node` oneshot (mirrors `config-deno` / `DENO_DIR`)
- Deliberately **not** installed: `corepack`, `include/node` headers, `share/` man pages.

## Run contract (`rootfs/etc/s6-overlay/s6-rc.d/node/run`, mirrors bun's)

| Env | Effect |
|-----|--------|
| `SCRIPT=<name>` | `exec s6-setuidgid tundra npm run <name>` (wins over `FILE`) |
| `FILE=<path>` | `exec s6-setuidgid tundra node [--watch] <path>` |
| neither | writes `/app/app.js` (http server on `PORT ?? 8080`, "Welcome to Node 🟢") and runs it |
| `WATCH=1` | adds `--watch` on the FILE/fallback paths only; SCRIPT mode prints a warning (npm run does not forward node flags) |
| `DEBUG=1` | `[DEBUG]` echo lines + `set -x` |

Image ENV: `NODE_VERSION`, `NODE_ENV=production`, `NODE_OPTIONS=`, `NPM_CONFIG_CACHE=/npm-cache`,
`NPM_CONFIG_UPDATE_NOTIFIER=false`, `FILE=`, `SCRIPT=`, `DEBUG=`, `WATCH=`,
`S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0`, `S6_KILL_FINISH_MAXTIME=5000`, `LD_LIBRARY_PATH`.

## Build and test locally

```bash
NODE_VERSION=$(curl -s https://nodejs.org/dist/index.json | jq -r '[.[] | select(.lts != false) | .version] | .[0] | ltrimstr("v")')
docker build --build-arg NODE_VERSION=$NODE_VERSION -t tundrasoft/node:test .
bash tests/smoke.sh tundrasoft/node:test $NODE_VERSION
# cross-arch sanity
docker build --platform linux/amd64 --build-arg NODE_VERSION=$NODE_VERSION -t tundrasoft/node:test-amd64 .
docker run --rm --platform linux/amd64 --entrypoint="" tundrasoft/node:test-amd64 node --version
```

Local results on 2026-08-23 with Node 24.19.0 (arm64 host): image 164 MB; smoke suite 6/6 PASS
(version, npm runs, default HTTP on 8080, FILE mode, runs as uid 1000, SCRIPT mode); amd64
cross-build reports `v24.19.0 x64 linux`. Every `docker run` / Dockerfile example in the README
was also executed against `tundrasoft/node:test` and served the expected response.

## Workflows — identical to deno except for the runtime bits

`build-docker.yml`, `preview.yml`, `security-scan.yml`, `dependabot.yml`, issue/PR templates and
`.github/scripts/*` are copies of deno's; a `diff` against `TundraSoft/deno` shows only:

- version discovery: `curl -s https://nodejs.org/dist/index.json | jq '[.[] | select(.lts != false) | .version] | .[0:5]'`
  (5 newest **LTS**, newest first, leading `v` stripped) instead of the denoland releases API;
- renames `deno-versions`/`latest-deno-version`/`deno-version`/`DENO_VERSION`/`TEST_TAG: deno`
  → `node-…`/`NODE_VERSION`/`TEST_TAG: node`, and "Deno on Alpine Linux" labels → "Node.js …".

Tag rules, matrix shape, Alpine-branch discovery, ghcr.io + docker.io publishing, `ci-gate`, and
the README/CHANGELOG chore job are byte-identical.

### Secrets / settings needed before the first green CI run

Referenced by the workflows (these are **not** repo-level secrets on `TundraSoft/deno`, so they
are org-level secrets — confirm the new repo is in their visibility scope):

| Secret | Used by |
|--------|---------|
| `DOCKER_USERNAME`, `DOCKER_PASSWORD` | Docker Hub login (`build`), Docker Hub description sync (`chore`) |
| `GIT_HUB_TOKEN` | admin PAT for the `update-readme` job to push `chore: Update README and CHANGELOG [skip ci]` past the branch ruleset |
| `GITLEAKS_KEY` | `GITLEAKS_LICENSE` for the GitLeaks step in `security-scan.yml` |
| `GITHUB_TOKEN` | built-in (GHCR login, SARIF upload) |

Also needed, copied from deno's setup: a Docker Hub repository `tundrasoft/node`; a branch ruleset
`protect-main` on `main` (deno's: block deletion + non-fast-forward, require PR, required checks
`ci-gate` and `Container Security Scan`, bypass for Organization admins and Repository admin);
Actions default workflow permissions = read/write (deno has `write`).

## Deviations from the deno template (with reasons)

| Deviation | Reason |
|-----------|--------|
| Extra `COPY … libstdc++.so.6*` line in the Dockerfile | Node needs libstdc++; deno (Rust) does not. Without it `node` fails to load. |
| `node/finish` is executable (deno's `finish` is mode 644) | s6 only runs an executable `finish`; 644 is a latent bug in deno. |
| Run script mirrors **bun**'s (SCRIPT/FILE/fallback, no ALLOW_* flags) | Node has no permission flags; per task brief. |
| Fallback demo is an HTTP server (bun style) rather than deno's sleep loop | Per task brief; lets the smoke test prove port 8080. |
| README has no "Permission Flags" section; env table is Node's | Nothing to document. |
| README pins examples to `tundrasoft/node:24`, not `:22` | With "5 newest LTS" discovery every built version is currently 24.x and only the newest LTS gets the `<major>` tag, so a `22` tag would never be published. Docs must be true. |
| `LICENSE` year 2026 (deno: 2023) | New repo, same choice bun made. |
| `.github/scripts/update_readme_tags.py` usage example string says `tundrasoft/node` | Cosmetic; logic unchanged. |
| `.trivyignore`, `SECURITY.md` (only the version-policy paragraph reworded for LTS), `.gitignore`, `.dockerignore`, `dependabot.yml`, issue/PR templates | Copied; config.yml URL repointed to TundraSoft/node. |

## Open items

1. **LTS window vs. tag coverage.** "5 newest LTS releases" are all on the current LTS line, so
   the previous LTS line (22.x) is never built and never gets `22`/`22.x` tags. If multi-line
   coverage is wanted, change the discovery to "newest release of each of the last N LTS
   lines" (group by major in jq) and revisit the `<major>`/`<major>.<minor>` tag-enable rules,
   which currently only fire for `latest-node-version`.
2. `corepack`, Node headers, and man pages are intentionally dropped. Add `corepack` if
   pnpm/yarn-via-corepack is wanted (`lib/node_modules/corepack` + `bin/corepack` symlink).
3. The `tundra` service process inherits `HOME=/root` from the container env (same as deno/bun).
   `npm run` works (verified as uid 1000), but `~/.npmrc` lookups hit `/root/.npmrc` and are
   ignored; set `HOME` or `NPM_CONFIG_USERCONFIG` if per-user npm config is ever needed.
4. Inherited from the base image: s6 prints `defining user bundles in /etc/s6-overlay/s6-rc.d
   is deprecated` at boot. Fix belongs in `tundrasoft/alpine` (move the `user` bundle to
   `/etc/s6-overlay/user-bundles.d`).
5. Create the Docker Hub repo, verify org-secret visibility, and add the `protect-main` ruleset
   (see above) before/after the first push; then trigger the weekly build or push to `main`.
