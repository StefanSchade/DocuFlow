FROM node:14-buster

RUN apt-get update && \
    apt-get install -y \
    ruby \
    ruby-dev \
    build-essential && \
    gem install --no-document asciidoctor --source http://rubygems.org/ --trust-policy NoSecurity && \
    npm install -g livereloadx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /documents
CMD livereloadx -s . -p 4000
