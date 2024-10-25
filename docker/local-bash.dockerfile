FROM python:3.10

# mac bash version is 3.2
ARG VERSION=3.2

RUN apt-get update
RUN apt-get install -y build-essential

# Download and install bash ${VERSION} from source using curl
RUN curl -s -O http://ftp.gnu.org/gnu/bash/bash-${VERSION}.tar.gz && \
    tar xzf bash-${VERSION}.tar.gz && \
    cd bash-${VERSION} && \
    ./configure && \
    make && \
    make install

# Set bash ${VERSION} as the default shell
RUN mv /bin/bash /bin/bash_backup && \
    ln -s /usr/local/bin/bash /bin/bash

# Verify bash version
RUN bash --version

CMD ["bash"]