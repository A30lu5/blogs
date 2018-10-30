#!/bin/bash

rootpath=`pwd`
match_files=`find ./ -maxdepth 3 -name "data.yml"`

# 保存好原来的IFS的值，方便以后还原回来
PRE_IFS=$IFS

# 设置IFS仅包括换行符
IFS=$(echo -en "\n\b")

for com_file in $match_files
do
    echo "[+] Handing: $com_file"
    DIR=$(dirname $com_file)
    # . /home/ubuntu/env.sh && 
    python $1 "$rootpath/$com_file"
    echo "[+] $com_file have DONE"
done

IFS=$PRE_IFS

echo "[+] Import All Matches DONE!"
