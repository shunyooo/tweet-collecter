#!/bin/sh
SCRIPT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
BASE_DIR=`dirname $SCRIPT_DIR`
ENV_PATH=${BASE_DIR}"/env/tweet_crawler"
docker build -t tweet-crawler:1.0 ${ENV_PATH}