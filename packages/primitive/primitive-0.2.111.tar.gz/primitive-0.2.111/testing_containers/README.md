Run the following commands, at the root of the project, to test **ubuntu** and/or **fedora** systeminfo.

```sh
make build && \
podman build \
-t ubuntu-with-primitive:latest \
-f ./testing_containers/ubuntu.Containerfile  \
--build-arg PRIMITIVE_CLI_VERSION=(python -c "from src.primitive.__about__ import __version__; print(__version__)") \
. && \
podman run -it --rm ubuntu-with-primitive:latest primitive --json hardware systeminfo
```

```sh
make build && \
podman build \
-t fedora-with-primitive:latest \
-f ./testing_containers/fedora.Containerfile \
--build-arg PRIMITIVE_CLI_VERSION=(python -c "from src.primitive.__about__ import __version__; print(__version__)") \
. && \
podman run -it --rm fedora-with-primitive:latest primitive --json hardware systeminfo
```