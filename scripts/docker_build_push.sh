#!/bin/sh

rootpath=`pwd`
compose_files=`find ./ -name "docker-compose.yml"`
# compose_files=`find . -name "docker-compose.yml" |grep -v "./site" |grep -v "^./docker-compose.yml"`

for com_file in $compose_files
do
    echo "[+] Handing: $com_file"
    DIR=$(dirname $com_file)
    cd $rootpath/$DIR
    docker-compose build
    docker-compose push
done

echo "[+] Docker Compose build and push done!"
