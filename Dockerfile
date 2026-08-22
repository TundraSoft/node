ARG ALPINE_VERSION=latest\
    NODE_VERSION

FROM gcr.io/distroless/cc-debian12:latest AS cc

FROM tundrasoft/alpine:${ALPINE_VERSION} AS sym

# Triple COPY pattern for distroless glibc compatibility:
# This pattern extracts glibc and loader libraries from distroless to ensure
# proper compatibility with Node's pre-built binaries which depend on glibc.
# Step 1: Extract ld-linux from distroless (dynamic linker)
COPY --from=cc --chown=root:root --chmod=755 /lib/*-linux-gnu/ld-linux-* /usr/local/lib/

RUN mkdir -p /tmp/lib \
    && ln -s /usr/local/lib/ld-linux-* /tmp/lib/

FROM tundrasoft/alpine:${ALPINE_VERSION}

LABEL maintainer="Abhinav A V <36784+abhai2k@users.noreply.github.com>" \
      org.opencontainers.image.title="Node.js Runtime on Alpine Linux" \
      org.opencontainers.image.description="Lightweight Node.js runtime image built on Alpine Linux with S6 overlay, npm, and developer-friendly utilities" \
      org.opencontainers.image.vendor="TundraSoft" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.url="https://github.com/TundraSoft/node" \
      org.opencontainers.image.documentation="https://github.com/TundraSoft/node/blob/main/README.md" \
      org.opencontainers.image.source="https://github.com/TundraSoft/node.git"

ARG NODE_VERSION \
  TARGETPLATFORM

ENV NODE_VERSION=${NODE_VERSION}\
    NODE_ENV=production\
    NODE_OPTIONS=\
    NPM_CONFIG_CACHE=/npm-cache\
    NPM_CONFIG_UPDATE_NOTIFIER=false\
    DEBUG=\
    WATCH=\
    S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0\
    S6_KILL_FINISH_MAXTIME=5000\
    FILE=\
    SCRIPT=\
    LD_LIBRARY_PATH="/usr/local/lib:/lib:/lib64"

# Service Supervision Configuration (S6 Overlay):
# S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0: Infinite startup wait time - prevents premature service timeout.
# S6_KILL_FINISH_MAXTIME=5000: Grace period (milliseconds) for graceful shutdown before hard kill.

COPY --from=cc --chown=root:root --chmod=755 /lib/*-linux-gnu/* /usr/local/lib/
# Node is C++ and also needs libstdc++, which distroless keeps under /usr/lib
# (next to its glibc-linked libssl/libcrypto). Copy only libstdc++ so the musl
# OpenSSL used by apk/wget is not shadowed via LD_LIBRARY_PATH.
COPY --from=cc --chown=root:root --chmod=755 /usr/lib/*-linux-gnu/libstdc++.so.6* /usr/local/lib/
COPY --from=sym --chown=root:root --chmod=755 /tmp/lib /lib
COPY --from=sym --chown=root:root --chmod=755 /tmp/lib /lib64

RUN set -eux; \
  case "${TARGETPLATFORM}" in \
  "linux/amd64"|"linux/x86_64") export NODE_ARCH="x64" ;; \
  "linux/arm64"|"linux/arm/v8") export NODE_ARCH="arm64" ;; \
  "linux/arm/v7") echo "ERROR: This image does not support 32-bit ARM (armv7). Only x86_64 and arm64 are supported." && exit 1 ;; \
  *) echo "Unsupported platform: ${TARGETPLATFORM}" ; exit 1 ;; \
  esac; \
  wget -qO /tmp/node.tar.xz https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.xz; \
  tar -xJf /tmp/node.tar.xz -C /tmp; \
  NODE_SRC="/tmp/node-v${NODE_VERSION}-linux-${NODE_ARCH}"; \
  mv ${NODE_SRC}/bin/node /usr/local/bin/node; \
  mkdir -p /usr/local/lib/node_modules; \
  mv ${NODE_SRC}/lib/node_modules/npm /usr/local/lib/node_modules/npm; \
  ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm; \
  ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx; \
  mkdir -p ${NPM_CONFIG_CACHE}; \
  chmod 0755 /usr/local/bin/node; \
  setgroup /usr/local/bin/node ${NPM_CONFIG_CACHE}; \
  rm -rf /tmp/*;


COPY /rootfs /

# nosemgrep: dockerfile.security.missing-user.missing-user
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s CMD ["/usr/bin/healthcheck.sh"]

WORKDIR /app
