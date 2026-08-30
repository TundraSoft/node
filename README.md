# 🟢 TundraSoft Node.js Runtime Image

<!-- DESCRIPTION-START -->
A lightweight Node.js runtime image built on Alpine Linux with S6 overlay, npm, and developer-friendly utilities.
<!-- DESCRIPTION-END -->

Built on [`tundrasoft/alpine`](https://github.com/TundraSoft/alpine): Alpine Linux, [s6-overlay](https://github.com/just-containers/s6-overlay) process supervision, and an unprivileged `tundra` user (UID/GID 1000) that your application runs as. Node's official Linux binaries are linked against glibc, which Alpine does not ship, so the image layers in the glibc loader and runtime libraries from `gcr.io/distroless/cc-debian12` (the same approach as [`tundrasoft/deno`](https://github.com/TundraSoft/deno)) rather than relying on a separately compiled musl build.

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TundraSoft/node/build-docker.yml?event=push&logo=github&label=build)](https://github.com/TundraSoft/node/actions/workflows/build-docker.yml)
[![Security Scan](https://img.shields.io/github/actions/workflow/status/TundraSoft/node/security-scan.yml?logo=adguard&label=security)](https://github.com/TundraSoft/node/actions/workflows/security-scan.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/tundrasoft/node.svg?logo=docker)](https://hub.docker.com/r/tundrasoft/node)
[![License](https://img.shields.io/github/license/TundraSoft/node.svg)](https://github.com/TundraSoft/node/blob/main/LICENSE)

---

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [🏷️ Available Tags](#️-available-tags)
- [✨ Features](#-features)
- [📖 Usage](#-usage)
  - [Basic Usage](#basic-usage)
  - [Running Applications](#-running-applications)
  - [Environment Variables](#environment-variables)
  - [Volumes](#volumes)
- [🏗️ Build-Time Optimization](#-build-time-optimization)
- [🔧 Development Mode](#-development-mode)
- [⚙️ Service Management](#️-service-management)
- [⏰ Cron Jobs](#-cron-jobs)
- [🔧 Building](#-building)
- [🔒 Security](#-security)
- [📚 Components](#-components)
- [📖 Reference](#reference)
- [📝 Changelog](#-changelog)
- [🤝 Contributing](#-contributing)

---

## 🚀 Quick Start

### 📦 Available Registries

This image is available on multiple registries:

- **Docker Hub**: `tundrasoft/node`
- **GitHub Container Registry**: `ghcr.io/tundrasoft/node`

```bash
# Pull from Docker Hub (recommended)
docker pull tundrasoft/node:latest

# Pull from GitHub Container Registry
docker pull ghcr.io/tundrasoft/node:latest

# Run a local Node.js application (mount your code into /app)
docker run -d \
  -p 8080:8080 \
  -e FILE=/app/server.js \
  -v $(pwd):/app \
  --name node-app \
  tundrasoft/node:latest

# Run a package.json script with a custom timezone
docker run -d \
  -e TZ=Asia/Kolkata \
  -e SCRIPT=start \
  -v $(pwd):/app \
  --name my-node-app \
  tundrasoft/node:latest
```

With no `FILE` or `SCRIPT` set, the container runs a small built-in demo server on port `8080` so you can confirm the image works.

--- 
## 🏷️ Available Tags

<!-- TAGS-START -->
## Tags

| Version | Tags |
|---------|------|
| [latest](https://hub.docker.com/r/tundrasoft/node/tags?name=latest) | Latest stable release |
| [edge](https://hub.docker.com/r/tundrasoft/node/tags?name=edge) | Edge/development version |
| [24.20](https://hub.docker.com/r/tundrasoft/node/tags?name=24.20) | [24.20.0](https://hub.docker.com/r/tundrasoft/node/tags?name=24.20.0) |
| [24.19](https://hub.docker.com/r/tundrasoft/node/tags?name=24.19) | [24.19.0](https://hub.docker.com/r/tundrasoft/node/tags?name=24.19.0) |
| [24.18](https://hub.docker.com/r/tundrasoft/node/tags?name=24.18) | [24.18.1](https://hub.docker.com/r/tundrasoft/node/tags?name=24.18.1), [24.18.0](https://hub.docker.com/r/tundrasoft/node/tags?name=24.18.0) |
| [24.17](https://hub.docker.com/r/tundrasoft/node/tags?name=24.17) | [24.17.0](https://hub.docker.com/r/tundrasoft/node/tags?name=24.17.0) |
| [24.16](https://hub.docker.com/r/tundrasoft/node/tags?name=24.16) | [24.16.0](https://hub.docker.com/r/tundrasoft/node/tags?name=24.16.0) |

<!-- TAGS-END -->

Images are built weekly for the five newest Node.js **LTS** releases (from `nodejs.org/dist/index.json`) on each supported Alpine branch (the three newest stable branches plus `edge`):

| Tag | Meaning |
|-----|---------|
| `latest` | Newest LTS release on the latest stable Alpine branch |
| `<major>.<minor>.<patch>` (e.g. `24.19.0`) | Each built LTS release, on the latest stable Alpine branch |
| `<major>.<minor>`, `<major>` (e.g. `24.19`, `24`) | Newest LTS release only, on the latest stable Alpine branch |
| `alpine-<branch>-<major>.<minor>.<patch>` (e.g. `alpine-3.22-24.19.0`) | Each built LTS release on a specific Alpine branch (including `edge`) |

---

## ✨ Features

- 🟢 **Node.js LTS Runtime** - Official Node.js binaries with `npm` and `npx`
- 🐧 **Alpine Linux Base** - Minimal, secure base OS
- 🔧 **S6 Overlay** - Advanced process supervision and service management
- 👤 **Pre-configured User** - Non-root `tundra` user (UID/GID: 1000)
- 📦 **glibc compatibility shim** - Node's official glibc binaries run on Alpine via a distroless glibc layer
- 🌍 **Timezone Support** - Easy timezone configuration
- ⏰ **Cron Support** - Dynamic cron job loading with environment variables
- 📊 **Health Monitoring** - Built-in health checks for application monitoring
- 🔄 **envsubst** - Environment variable substitution in config files

---

## 📖 Usage

### Basic Usage

Use as a base image in your Dockerfile. The application runs as the unprivileged `tundra` user (UID/GID 1000), so copy files with that ownership; otherwise the container recursively chowns `/app` at every boot, which is slow for a large `node_modules`.

**Single-file app:**
```dockerfile
FROM tundrasoft/node:24

COPY --chown=tundra:tundra server.js /app/

ENV FILE=/app/server.js
```

**package.json app:**
```dockerfile
FROM tundrasoft/node:24

COPY --chown=tundra:tundra package.json package-lock.json /app/
RUN npm ci && chown -R tundra:tundra /app
COPY --chown=tundra:tundra . /app

ENV SCRIPT=start
```

Pin the base image as tightly as you need:
```dockerfile
FROM ghcr.io/tundrasoft/node:24            # GitHub Container Registry mirror
FROM tundrasoft/node:24.19.0               # exact Node.js release
FROM tundrasoft/node:alpine-3.22-24.19.0   # exact Node.js release on a specific Alpine branch
```

### 🎯 Running Applications

The image decides what to run based on two environment variables:

- `SCRIPT` — run a script defined in `package.json` (`npm run <SCRIPT>`)
- `FILE` — run a single file directly (`node <FILE>`)

`SCRIPT` takes precedence over `FILE`. If neither is set, a minimal demo server is started on port `8080`.

**Run a file:**
```bash
docker run -p 8080:8080 \
  -e FILE=/app/server.js \
  -v $(pwd):/app \
  tundrasoft/node:latest
```

**Run a package.json script:**
```bash
docker run -v $(pwd):/app \
  -e SCRIPT=start \
  tundrasoft/node:latest
```

**Run with environment variables:**
```bash
docker run -d \
  -e FILE=/app/server.js \
  -e NODE_OPTIONS=--max-old-space-size=512 \
  -e PUID=1001 \
  -e PGID=1001 \
  -e TZ=America/New_York \
  -v $(pwd):/app \
  tundrasoft/node:latest
```

### Environment Variables

<!-- ENV-VARS-START -->
| Variable | Description | Default |
|----------|-------------|---------|
| `SCRIPT` | Run a script from `package.json` via `npm run` (takes precedence over `FILE`) | N/A |
| `FILE` | The file to run directly with `node` | N/A |
| `NODE_ENV` | Node.js environment hint; also makes `npm install`/`npm ci` skip devDependencies | `production` |
| `NODE_OPTIONS` | Extra Node.js CLI flags applied to every `node` process (e.g. `--max-old-space-size=512`) | empty |
| `NPM_CONFIG_CACHE` | npm cache directory | `/npm-cache` |
| `NPM_CONFIG_UPDATE_NOTIFIER` | npm "new version available" notice | `false` |
| `PUID` | User ID for the `tundra` user | `1000` |
| `PGID` | Group ID for the `tundra` group | `1000` |
| `TZ` | Timezone (e.g., `Asia/Kolkata`, `America/New_York`) | `UTC` |
| `DEBUG` | Enable debug mode with verbose output (1 to enable) | N/A |
| `WATCH` | Restart on file changes via `node --watch` (1 to enable; `FILE` and demo modes only) | N/A |
| `S6_CMD_WAIT_FOR_SERVICES_MAXTIME` | Max time (ms) to wait for services to start (0 = infinite) | `0` |
| `S6_KILL_FINISH_MAXTIME` | Grace period (ms) for graceful shutdown | `5000` |
<!-- ENV-VARS-END -->

Any other `NPM_CONFIG_*` variable is honoured by npm as usual (for example `NPM_CONFIG_LOGLEVEL=warn`).

> 📚 **Reference:** [Node.js CLI options](https://nodejs.org/api/cli.html) · [npm config](https://docs.npmjs.com/cli/using-npm/config)

### Volumes

| Path | Description |
|------|-------------|
| `/app` | Application root directory (recommended to mount as volume) |
| `/crons` | Directory for cron job files (automatically loaded) |
| `/npm-cache` | npm cache directory (`NPM_CONFIG_CACHE`, for persisting downloads) |

---

## 🏗️ Build-Time Optimization

### Install dependencies during the build

Install dependencies while building the image to eliminate cold-start downloads:

**Install from a lockfile (best layer caching):**
```dockerfile
FROM tundrasoft/node:24

# Copy manifests first so this layer is cached until they change
COPY --chown=tundra:tundra package.json package-lock.json /app/
RUN npm ci && chown -R tundra:tundra /app

COPY --chown=tundra:tundra . /app

ENV FILE=/app/index.js
```

`NODE_ENV=production` is set in the image, so `npm ci` installs only production dependencies. Pass `--include=dev` when a build step needs devDependencies.

**Build with devDependencies, ship without them:**
```dockerfile
FROM tundrasoft/node:24 AS build

COPY package.json package-lock.json /app/
RUN npm ci --include=dev
COPY . /app
RUN npm run build

FROM tundrasoft/node:24

COPY --chown=tundra:tundra package.json package-lock.json /app/
RUN npm ci && chown -R tundra:tundra /app
COPY --from=build --chown=tundra:tundra /app/dist /app/dist

ENV FILE=/app/dist/index.js
```

### Benefits

- ⚡ **Faster cold starts** - No dependency downloads at runtime
- 📦 **Reproducible builds** - `npm ci` pins exact versions from the lockfile
- 🔒 **Offline compatible** - Works in isolated environments
- 🎯 **Layer caching** - Separate install layer for better Docker caching
- 🚀 **Production ready** - No surprise downloads in production

---

## 🔧 Development Mode

### Development setup

Development mode combines `DEBUG`, `WATCH`, and a volume mount for a fast feedback loop:

**Development setup:**
```bash
docker run -it \
  -e DEBUG=1 \
  -e WATCH=1 \
  -e NODE_ENV=development \
  -e FILE=/app/main.js \
  -v $(pwd):/app \
  -p 8080:8080 \
  tundrasoft/node:latest
```

**What this enables:**
- 🐛 `DEBUG=1`: Verbose startup output with argument inspection
- 👁️ `WATCH=1`: File watching with auto-restart on changes (`node --watch`)
- 📋 `NODE_ENV=development`: Overrides the production default for frameworks that key off it

**With a package.json script:**

`npm run` does not forward `--watch` to `node`, so `WATCH=1` is ignored in `SCRIPT` mode. Put the flag in the script instead:

```json
{
  "scripts": {
    "dev": "node --watch src/main.js"
  }
}
```

```bash
docker run -it \
  -e DEBUG=1 \
  -e SCRIPT=dev \
  -v $(pwd):/app \
  -p 8080:8080 \
  tundrasoft/node:latest
```

---

## ⚙️ Service Management

This image uses [S6 Overlay](https://github.com/just-containers/s6-overlay) for advanced process supervision and service management. S6 is a lightweight init system that provides reliable service supervision, dependency management, and graceful shutdown handling.

The Node service runs your application via the S6 system, ensuring:
- Automatic restart on failure
- Graceful shutdown handling
- Proper signal handling
- Logging integration
- Health monitoring

### Service Startup & Shutdown Configuration

Control S6 service supervision timeouts:

```bash
# Custom startup timeout (30 seconds max wait)
docker run -d \
  -e S6_CMD_WAIT_FOR_SERVICES_MAXTIME=30000 \
  -e FILE=/app/server.js \
  tundrasoft/node:latest

# Extended graceful shutdown (10 seconds)
docker run -d \
  -e S6_KILL_FINISH_MAXTIME=10000 \
  -e FILE=/app/server.js \
  tundrasoft/node:latest

# Infinite startup wait (for slow-starting apps)
docker run -d \
  -e S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0 \
  -e FILE=/app/server.js \
  tundrasoft/node:latest
```

### 🎯 Service Triggers

S6 provides dependency management through trigger points:

| Trigger | Description |
|---------|-------------|
| `os-ready` | Container booted, basic setup complete |
| `config-start` | Start configuration changes |
| `config-ready` | Configuration complete |
| `service-start` | Application services begin |
| `service-ready` | All services initialized |

### Adding Custom Services

You can extend the Node image with additional services:

```dockerfile
FROM tundrasoft/node:latest

# Install additional tools
RUN apk add --no-cache redis

# Create Redis service
RUN mkdir -p /etc/s6-overlay/s6-rc.d/redis/dependencies.d
RUN echo "longrun" > /etc/s6-overlay/s6-rc.d/redis/type

RUN cat > /etc/s6-overlay/s6-rc.d/redis/run << 'EOF'
#!/command/with-contenv sh
exec 2>&1
exec redis-server --bind 127.0.0.1
EOF

RUN chmod +x /etc/s6-overlay/s6-rc.d/redis/run
RUN touch /etc/s6-overlay/s6-rc.d/redis/dependencies.d/service-start
RUN touch /etc/s6-overlay/s6-rc.d/user/contents.d/redis
```

---

## ⏰ Cron Jobs

### Dynamic Cron Setup

This image provides dynamic cron job loading with environment variable substitution support:

1. **Create cron files** in the `/crons` directory
2. **Use environment variables** with `$VARIABLE_NAME` syntax
3. **Pass environment variables** when running the container
4. **S6 automatically** loads and installs jobs at startup

### Cron Examples

#### Example 1: Basic Scheduled Task

**File:** `/crons/daily-cleanup`
```bash
# Run cleanup at 3 AM daily
0 3 * * * find /tmp -type f -mtime +7 -delete
```

**Run container:**
```bash
docker run -d \
  -v /host/crons:/crons:ro \
  tundrasoft/node:latest
```

#### Example 2: Application Health Check

**File:** `/crons/health-check`
```bash
# Check application health every 5 minutes
*/5 * * * * wget -q -O /dev/null http://127.0.0.1:8080/health || exit 1
```

**Run container:**
```bash
docker run -d \
  -p 8080:8080 \
  -e FILE=/app/server.js \
  -v /host/crons:/crons:ro \
  -v $(pwd):/app \
  tundrasoft/node:latest
```

#### Example 3: Complex Configuration

**File:** `/crons/maintenance-jobs`
```bash
# Database backup
$BACKUP_TIME /usr/local/bin/backup.sh >> /var/log/cron-backup.log 2>&1

# Log rotation
$LOG_ROTATE_TIME logrotate /etc/logrotate.conf

# Cleanup caches
$CLEANUP_TIME rm -rf /npm-cache/_logs/*
```

**Run container with environment substitution:**
```bash
docker run -d \
  -e BACKUP_TIME='0 2 * * *' \
  -e LOG_ROTATE_TIME='0 0 * * *' \
  -e CLEANUP_TIME='0 4 * * 0' \
  -v /host/crons:/crons:ro \
  tundrasoft/node:latest
```

---

## 🔧 Building

### 🏗️ Build Command

```bash
docker build \
  --build-arg ALPINE_VERSION=latest \
  --build-arg NODE_VERSION=24.19.0 \
  -t my-node-image .
```

### ⚙️ Build Arguments

<!-- BUILD-ARGS-START -->
| Argument | Description | Example |
|----------|-------------|---------|
| `ALPINE_VERSION` | Alpine Linux version (base image) | `latest`, `3.22`, `3.21` |
| `NODE_VERSION` | Node.js runtime version (official linux tarball) | `24.19.0`, `22.18.0` |
<!-- BUILD-ARGS-END -->

Node's official Linux binaries are linked against glibc, so the image layers in the dynamic linker and runtime libraries from `gcr.io/distroless/cc-debian12` (`/usr/local/lib`, with `/lib` and `/lib64` loader symlinks and `LD_LIBRARY_PATH` set). 32-bit ARM (armv7) is not supported.

### 🧪 Testing

```bash
docker build --build-arg NODE_VERSION=24.19.0 -t tundrasoft/node:test .
tests/smoke.sh tundrasoft/node:test 24.19.0
```

---

## 🔒 Security

This repository implements comprehensive security scanning:

- 🛡️ **Multi-layered scanning** with Trivy, CodeQL, Semgrep, and Grype
- 🔍 **Secret detection** with GitLeaks (runs early in build process)
- 📊 **Automated reporting** to GitHub Security tab
- 🔄 **Daily security scans** and vulnerability monitoring

### Security Model

Node.js has no built-in permission sandbox enabled by default, so isolation is enforced at the container level rather than by the runtime. Node's experimental [permission model](https://nodejs.org/api/permissions.html) can be opted into via `NODE_OPTIONS` when your application supports it.

For security issues, please use [GitHub's private vulnerability reporting](https://github.com/TundraSoft/node/security/advisories/new).

### 🛡️ Security Best Practices

**Container Runtime Security:**
```bash
# Run with read-only root filesystem
docker run --read-only --tmpfs /tmp --tmpfs /run tundrasoft/node:latest

# Use specific user and drop capabilities
docker run --user 1000:1000 --cap-drop=ALL tundrasoft/node:latest

# Limit resources
docker run --memory=512m --cpus=1 --pids-limit=100 tundrasoft/node:latest
```

**File System Security:**
```bash
# Mount application files as read-only
docker run -v $(pwd):/app:ro tundrasoft/node:latest

# Mount secrets securely
docker run -v /host/secrets:/secrets:ro,Z tundrasoft/node:latest
```

**Production Deployment:**
```bash
# Always use specific version tags
docker run tundrasoft/node:24.19.0 # Not 'latest'

# Use custom networks
docker network create --driver bridge secure-app-net
docker run --network secure-app-net tundrasoft/node:24.19.0

# Enable logging
docker run --log-driver=json-file --log-opt max-size=10m tundrasoft/node:24.19.0
```

For security issues, please use [GitHub's private vulnerability reporting](https://github.com/TundraSoft/node/security/advisories/new).

---

## 📚 Components

### Base System
- **Alpine Linux** - Minimal, secure, and reliable
- **S6 Overlay v3** - Process supervision with lifecycle management
- **OpenSSL 3.x** - Cryptographic and TLS support

### Runtime
- **Node.js LTS** - Official `nodejs.org` Linux binaries
- **npm / npx** - Bundled package manager (`/usr/local/lib/node_modules/npm`)
- **glibc shim** - Loader and runtime libraries from `gcr.io/distroless/cc-debian12`

### Utilities
- **wget** - HTTP client (from the base image)
- **Bash/sh** - Shell scripting
- **Healthcheck script** - S6-integrated service monitoring

---

## 📖 Reference

### Container Lifecycle

| Stage | Description | Services |
|-------|-------------|----------|
| Boot | Initialize system and user | `os-ready` → `service-ready` |
| Config | Load configuration | `config-start` → `config-ready` |
| Main | Run application/cron | `node` or `crond` |
| Shutdown | Clean termination | S6 async handlers |

### Directory Structure

```
/npm-cache/       - npm cache directory (mounted volume)
/app/             - Application code
/usr/local/bin/   - node, npm, npx
/usr/local/lib/   - glibc shim + node_modules/npm
/etc/s6-overlay/  - S6 service definitions
/etc/crontabs/    - Cron jobs (if using cron)
/etc/timezone     - TZ configuration
/run/s6/          - S6 runtime (temporary)
```

### Docker Compose Example

```yaml
services:
  app:
    image: tundrasoft/node:latest
    environment:
      - FILE=/app/src/main.js
      - TZ=UTC
    volumes:
      - ./src:/app
      - npm-cache:/npm-cache
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "/usr/bin/healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  npm-cache:
```

### Troubleshooting

#### Application not starting

**Symptoms:** Container exits immediately or hangs

**Debug steps:**
```bash
# View logs to see startup errors
docker logs <container-id>

# Run with DEBUG mode for verbose output
docker run -it -e DEBUG=1 -e FILE=/app/main.js tundrasoft/node:latest

# Check healthcheck status
docker exec <container-id> /usr/bin/healthcheck.sh

# Verify file exists and is readable
docker exec <container-id> ls -la /app/main.js
```

#### "Cannot find module" errors

**Symptoms:** `Error: Cannot find module 'express'` (or any dependency)

**Solutions:**
```bash
# Ensure dependencies are installed into /app/node_modules
docker run -v $(pwd):/app -w /app --entrypoint="" tundrasoft/node:latest npm ci
```
```dockerfile
# Or install dependencies during the build
FROM tundrasoft/node:24
COPY --chown=tundra:tundra package.json package-lock.json /app/
RUN npm ci && chown -R tundra:tundra /app
COPY --chown=tundra:tundra . /app
ENV FILE=/app/main.js
```

#### Missing devDependencies

**Symptoms:** A build tool (e.g. `tsc`, `vite`) is not found during `npm run build`

**Cause:** `NODE_ENV=production` is set in the image, so `npm ci`/`npm install` skip devDependencies.

**Solution:**
```dockerfile
RUN npm ci --include=dev
```

#### Slow cold start

**Symptoms:** First run takes a long time to download dependencies

**Solution:**
```bash
# Persist the npm cache using a volume
docker run -v npm-cache:/npm-cache \
  -e SCRIPT=start tundrasoft/node:latest
```

#### Watch mode not restarting

**Symptoms:** File changes don't trigger app restart with WATCH=1

**Check:**
```bash
# Verify watch mode is working (FILE mode only)
docker run -it -e WATCH=1 -e DEBUG=1 \
  -e FILE=/app/main.js \
  -v $(pwd):/app \
  tundrasoft/node:latest

# Look for "Restarting" messages in logs. In SCRIPT mode, add --watch to the
# script in package.json instead; WATCH=1 is ignored there.
```

---

## 🤝 Contributing

1. 🍴 **Fork** the repository
2. 🌟 **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. 💾 **Commit** changes: `git commit -m 'Add amazing feature'`
4. 📤 **Push** to branch: `git push origin feature/amazing-feature`
5. 🔄 **Open** a Pull Request

### 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes and [CHANGELOG-GUIDE.md](CHANGELOG-GUIDE.md) for contribution guidelines.

---

**Built with ❤️ by [TundraSoft](https://github.com/TundraSoft)**

[View on GitHub](https://github.com/TundraSoft/node) • [Docker Hub](https://hub.docker.com/r/tundrasoft/node) • [Report Issue](https://github.com/TundraSoft/node/issues)
