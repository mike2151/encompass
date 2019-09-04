import docker
import os
from config import DOCKER_IMAGE, MEMORY_LIMIT, AUTO_REMOVE, FILE_OPEN_MODE, LOCAL_DIR, CONTAINER_DIR


def python_runner(client, file_name, container_name, command, return_dict):
    try:
        local_directory = LOCAL_DIR + '/' + str(file_name)
        container_directory = CONTAINER_DIR + '/' + str(file_name)
        python_run_command = command + ' ' + str(container_directory)

        print(python_run_command)
        print(local_directory)
        print(container_directory)

        if not os.path.exists(local_directory):
            raise Exception('File not found : ' + str(local_directory))

        result = client.containers.run(DOCKER_IMAGE, python_run_command,
                                       remove=AUTO_REMOVE, mem_limit=MEMORY_LIMIT,
                                       name=container_name,
                                       volumes={local_directory: {
                                                'bind': container_directory,
                                                'mode': FILE_OPEN_MODE}
                                                })
        return_dict['result'] = result
    except docker.errors.ContainerError as e:
        try:
            pretty_message = str(e.stderr).split('Traceback (most recent call last):')[1]
            return_dict['result'] = pretty_message
        except:
            return_dict['result'] = e.stderr
    except Exception as e:
        return_dict['result'] = e.stderr
