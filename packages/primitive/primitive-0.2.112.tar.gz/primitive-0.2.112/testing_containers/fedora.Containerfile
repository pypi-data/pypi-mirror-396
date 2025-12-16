FROM fedora:latest
USER root

ARG PRIMITIVE_CLI_VERSION=0.2.71

RUN dnf update -y
RUN dnf install git -y && \
    dnf install -y python3.12 python3-pip && \
    dnf clean all

RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"

RUN pip install --upgrade pip

COPY ./dist/primitive-$PRIMITIVE_CLI_VERSION-py3-none-any.whl primitive-$PRIMITIVE_CLI_VERSION-py3-none-any.whl
RUN pip install primitive-$PRIMITIVE_CLI_VERSION-py3-none-any.whl

CMD [bash]