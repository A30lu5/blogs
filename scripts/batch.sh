#!/bin/sh

rootpath=`pwd`
match_files=`find ./ -name "data.yml"`

for com_file in $match_files
do
    echo "[+] Handing: $com_file"
    DIR=$(dirname $com_file)
    cd $rootpath/$DIR
    . /home/ubuntu/env.sh && python /home/ubuntu/CTFd-swarm/import2chal.py -p $rootpath/$DIR
    echo "[+] $com_file have DONE"
    # docker-compose build
    # docker-compose push
done

echo "[+] Import All Matches DONE!"
