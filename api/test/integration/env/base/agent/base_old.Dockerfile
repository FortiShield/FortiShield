FROM ubuntu:18.04

RUN apt-get update && apt-get install -y curl apt-transport-https lsb-release gnupg2
RUN curl -s https://fortishield.github.io/packages/key/GPG-KEY-FORTISHIELD | apt-key add - && \
    echo "deb https://fortishield.github.io/packages/3.x/apt/ stable main" | tee /etc/apt/sources.list.d/fortishield.list && \
    apt-get update && apt-get install fortishield-agent=3.13.2-1 -y
