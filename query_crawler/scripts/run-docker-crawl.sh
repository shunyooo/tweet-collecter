# docker run クロール
cmd=''

while [ "$1" != "" ]
do
  cmd="${cmd} $1"
  shift
done

SCRIPT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
sh ${SCRIPT_DIR}/run-docker.sh python main.py ${cmd}