FROM ubuntu:latest
USER root

ARG PRIMITIVE_CLI_VERSION=0.2.71

RUN apt update -y
RUN apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev libkrb5-dev

RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"

RUN pyenv install 3.12.5
RUN pyenv global 3.12.5
RUN pip install --upgrade pip

COPY ./dist/primitive-$PRIMITIVE_CLI_VERSION-py3-none-any.whl primitive-$PRIMITIVE_CLI_VERSION-py3-none-any.whl
RUN pip install primitive-$PRIMITIVE_CLI_VERSION-py3-none-any.whl

CMD [bash]