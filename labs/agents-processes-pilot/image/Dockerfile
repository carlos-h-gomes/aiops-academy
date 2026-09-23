FROM python:3.14.7-alpine3.24@sha256:5e0ede45886712ce95b0e66232f743cc3d69ff6c2f62cc0d63778e1e894f8bd4 AS patched
ADD --checksum=sha256:8306e5bb577696c9069fe1dfd9e1dcc39d2d481c6a1b0e707fd03c3e21aa6aa2 https://dl-cdn.alpinelinux.org/alpine/v3.24/main/x86_64/libuuid-2.42.3-r1.apk /tmp/libuuid.apk
RUN --network=none ["apk", "add", "--no-network", "--upgrade", "/tmp/libuuid.apk"]
COPY strip_installer.py /tmp/strip_installer.py
RUN --network=none ["python", "-I", "-B", "/tmp/strip_installer.py"]

# Flatten the patched filesystem: removed installer bytes are not retained in lower layers.
FROM scratch
COPY --from=patched / /
ENV PATH=/usr/local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TMPDIR=/work
LABEL org.opencontainers.image.title="AIOps Academy agents-05 runtime" \
      org.opencontainers.image.version="2026-09-15.2" \
      academy.runtime.platform="linux/amd64"
USER 65532:65532
WORKDIR /work
CMD ["python", "--version"]
