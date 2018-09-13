#!/bin/sh

rootpath=`pwd`
match_files=`find ./ -maxdepth 3 -name "data.yml"`

for com_file in $match_files
do
    echo "[+] Handing: $com_file"
    DIR=$(dirname $com_file)
    . /home/ubuntu/env.sh && python $1 "$rootpath/$com_file"
    echo "[+] $com_file have DONE"
done

echo "[+] Import All Matches DONE!"
