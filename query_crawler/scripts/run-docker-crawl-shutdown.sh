# docker run クロール shutdown
cmd=''

while [ "$1" != "" ]
do
  cmd="${cmd} $1"
  shift
done

SCRIPT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
sh ${SCRIPT_DIR}/run-docker-crawl.sh ${cmd}

echo shutdown
sudo shutdown -h now