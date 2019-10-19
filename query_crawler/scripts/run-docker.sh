# docker run
cmd=''

while [ "$1" != "" ]
do
  cmd="${cmd} $1"
  shift
done

SCRIPT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
BASE_DIR=`dirname $SCRIPT_DIR`
ENV_PATH=${BASE_DIR}"/env/tweet_crawler/.env"
python ${BASE_DIR}/env/tweet_crawler/make_env_file.py
docker run --rm -v ${BASE_DIR}:/app --env-file ${ENV_PATH} tweet-crawler:1.0 ${cmd}
