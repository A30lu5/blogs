#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import click
import os
import yaml
import hashlib
import shutil
import subprocess
import logging
import logging.handlers
import json
import traceback
import codecs
import threading
import datetime
import fnmatch

CONCURRENT_THREAD_NUM = 4

logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_file = "/tmp/docker_build.log"
if not os.path.exists(log_file):
    codecs.open(log_file, 'a', encoding='utf-8').close()
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
root_log = logging.handlers.RotatingFileHandler(log_file, maxBytes=100000)
console_log = logging.StreamHandler()
root_log.setFormatter(formatter)
console_log.setFormatter(formatter)
logger.addHandler(root_log)
logger.addHandler(console_log)


def list2dict(info_list):
    dict_info = {}
    for info in info_list:
        info_key = info.keys()[0]
        dict_info[info_key] = info[info_key]
    return dict_info


def build_and_push(filepath):
    try:
        print threading.currentThread().getName()
        logger.info("begin docker-compose build,push, filepath: %s" % filepath)
        subprocess.check_call(['docker-compose', '-f', filepath, 'build'])
        subprocess.check_call(['docker-compose', '-f', filepath, 'push'])
        logger.info("end docker-compose build,push, filepath: %s" % filepath)
    except subprocess.CalledProcessError, e:
        logger.error("Error occured when build image or push:" + filepath)
        raise e


def handle_chal(chal, match_path):
    # 获取题目名称
    chal_name = chal.keys()[0]
    chal_info = list2dict(chal[chal_name])
    # chal_info = chal[chal_name]

    if chal_info.has_key('env') and chal_info['env'] is not None:

        env_path = os.path.join(match_path, chal_info['env'])

        if os.path.exists(env_path):
            # build_and_push(env_path)
            return env_path
        else:
            logger.error("%s does not exist" % env_path)
            raise Exception


def div_list(ls, n):
	if not isinstance(ls, list) or not isinstance(n, int):
		return []
	ls_len = len(ls)
	if n <= 0 or 0 == ls_len:
		return []
	if n > ls_len:
		return []
	elif n == ls_len:
		return [[i] for i in ls]
	else:
		ls_return = [[] for i in range(n)]
        for i, v in enumerate(ls):
            ls_return[i % n].append(v)
        return ls_return


def handle_build_push(list):
    for env_path in list:
        build_and_push(env_path)


def docker_update(yml_path):
    logger.info("begin to docker update:" + yml_path)
    start = datetime.datetime.now()
    if not os.path.exists(yml_path):
        logger.error("yml file dose not exist:" + yml_path)
        return
    if not os.path.isfile(yml_path):
        logger.error("path is not a file:" + yml_path)
        return
    with codecs.open(yml_path, 'r', encoding='utf-8') as f:
        try:
            matches = yaml.safe_load(f.read())
        except yaml.YAMLError, e:
            logger.error('Error parsing YAML file:' + yml_path)
            raise e
        for match_name in matches:
            try:
                all_env_list = []
                # 获取所有比赛
                has_exception = False
                match = matches[match_name]
                for match_info in match:
                    # 获取比赛中分类下的内容
                    if match_info != '_meta_':
                        chals_in_cat = match[match_info]
                        # 获取具体题目信息
                        for chal in chals_in_cat:
                            try:
                                result = handle_chal(
                                    chal, os.path.dirname(yml_path))
                                if result:
                                    all_env_list.append(result)
                            except Exception:
                                has_exception = True
                div_result = div_list(all_env_list, CONCURRENT_THREAD_NUM)
                thread_list = []
                for rs in div_result:
                    t = threading.Thread(target=handle_build_push, args=(rs,))
                    thread_list.append(t)
                for t in thread_list:
                    t.start()
                for t in thread_list:
                    t.join()

            except Exception, e:
                logger.error("Error occured during docker update")
            else:
                if not has_exception:
                    logger.info("docker update succeed in math:" + match_name)
                else:
                    logger.error("tracebacks exception detail:" +
                                 traceback.format_exc())
    end = datetime.datetime.now()
    logger.info("cost time %f s" % (end - start).seconds)


def find_files_under_path(path, file_match):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, file_match):
            matches.append(os.path.join(root, filename))
    return matches

if __name__ == '__main__':
    current_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../'))
    # print current_root
    data_yml_files = find_files_under_path(current_root, "data.yml")
    for one_yml in data_yml_files:
        print "[+] Phasing {}".format(one_yml)
        docker_update(one_yml)
