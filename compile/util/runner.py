import docker
import os
import hashlib
import multiprocessing
from compile.service import get_command, get_extension, get_target_method
from config import LOCAL_DIR, CONTAINER_TIMEOUT
from distutils.dir_util import copy_tree
import string
import random
import shutil


def id_generator(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def run_submission_file(file_name, host_folder_path, language, version, network_enabled):
    client = docker.from_env()
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    container_name = str(hashlib.sha1(os.urandom(128)).hexdigest())[:10]
    run_folder = id_generator()

    result, command_string = get_command(language, version)

    if not result:
        return_dict['result'] = command_string
        return return_dict

    # copy files over
    write_file_path = LOCAL_DIR + '/' + run_folder
    copy_tree(host_folder_path, write_file_path)

    target_method = get_target_method(language)
    process = multiprocessing.Process(target=target_method,
                                      args=(client, file_name, container_name, command_string, return_dict, run_folder, network_enabled))

    process.start()

    # setting the timeout for the process
    process.join(CONTAINER_TIMEOUT)

    # if the process/container is still alive kill the process
    if process.is_alive():
        process.terminate()
        process.join()
        return_dict['result'] = 'Time limit Exceeded'

    # check if the container is still running. if yes, kill the container
    running_containers = client.containers.list(filters={'name': container_name}, all=True)
    if running_containers:
        running_containers[0].remove(force=True)

    # remove the folder
    shutil.rmtree(write_file_path)
    return return_dict
