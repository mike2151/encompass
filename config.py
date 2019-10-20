from django.conf import settings
# ----------------------  BASE PARAMETERS ---------------------- #
DOCKER_IMAGE = 'compiler'
if settings.DEBUG:
    LOCAL_DIR = '/Users/mike/Desktop/encompassinterviews/encompassinterviews/temp'
    CONTAINER_DIR = '/data'
else:
    LOCAL_DIR = '/home/django/encompass/temp'
    CONTAINER_DIR = '/home/django/data'
# ----------------------  ADDITIONAL PARAMETERS ---------------------- #
MEMORY_LIMIT = '16000k'  
AUTO_REMOVE = True 
FILE_OPEN_MODE = 'ro' 
CONTAINER_TIMEOUT = 10 
NETWORK_DISABLED = True
