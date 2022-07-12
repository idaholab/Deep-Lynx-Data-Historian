# Copyright 2022, Battelle Energy Alliance, LLC

import os
import logging
from flask import Flask, request, Response, json
import deep_lynx
import threading
import environs
import time

from .data_historian import main

# Global variables
api_client = None
lock_ = threading.Lock()
threads = list()
thread_counter = 1
env = environs.Env()

# Configure logging. to overwrite the log file for each run, add option: filemode='w'
logging.basicConfig(filename='DataHistorianAdapter.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    datefmt='%m/%d/%Y %H:%M:%S')

print('Application started. Logging to file DataHistorianAdapter.log')


def create_app():
    global api_client
    """ This file and aplication is the entry point for the `flask run` command """
    app = Flask(os.getenv('FLASK_APP'), instance_relative_config=True)

    # Purpose to run flask once (not twice)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Instantiate deep_lynx
        container_id, data_source_id, api_client = deep_lynx_init()
        os.environ["CONTAINER_ID"] = container_id
        os.environ["DATA_SOURCE_ID"] = data_source_id
        if api_client is None:
            # Connection to DeepLynx unsuccessful
            print("ERROR: Cannot connect to DeepLynx. Please see logs. Exiting...")
            logging.error("Cannot connect to DeepLynx. Exiting...")

        # A mount point is a directory (typically an empty one) in the currently accessible filesystem on which an additional filesystem is mounted (i.e., logically attached).
        mount_point = os.getenv("REPOSITORY_MOUNT_DIRECTORY")
        print("Repository mount directory exists", os.path.exists(mount_point))
        # Create mount point if does not exist
        if not os.path.exists(mount_point):
            os.makedirs(mount_point)

        # Unmount moint point
        unmount_command = "umount " + mount_point
        unmount_return = os.system(unmount_command)
        print("Un-mount return", unmount_return)

        # "mount_smbfs" command mounts a share from a remote server
        mount_command = "mount_smbfs " + os.getenv("SERVER_DIRECTORY_PATH") + " " + mount_point
        mount_return = os.system(mount_command)
        print("Mount return", mount_return)

        # Create thread object
        # Thread object: activity that is run in a separate thread of control
        # Daemon: a process that runs in the background. A daemon thread will shut down immediately when the program exits.
        historian_thread = threading.Thread(target=initiate_file_processor, daemon=True, name="historian_thread")
        print("Created historian_thread")
        threads.append(historian_thread)
        # Start the thread’s activity
        historian_thread.start()

    @app.route('/historian', methods=['POST'])
    def file_handler():
        # TODO: Implementation for receiving files
        # Return successful response
        return Response(response=json.dumps({'received': True}), status=200, mimetype='application/json')

    return app


def deep_lynx_init():
    """ 
    Returns the container id, data source id, and api client for use with the DeepLynx SDK.
    Assumes token authentication. 

    Args
        None
    Return
        container_id (str): container ID for Deep Lynx 
        data_source_id (str): data source ID for Deep Lynx
        api_client (ApiClient): api client for Deep Lynx 
    """
    # Initialize an ApiClient for use with deep_lynx APIs
    configuration = deep_lynx.configuration.Configuration()
    configuration.host = os.getenv('DEEP_LYNX_URL')
    api_client = deep_lynx.ApiClient(configuration)

    # Perform API token authentication only if values are provided
    if os.getenv('DEEP_LYNX_API_KEY') != '' and os.getenv('DEEP_LYNX_API_KEY') is not None:

        # Authenticate via an API key and secret
        auth_api = deep_lynx.AuthenticationApi(api_client)

        try:
            token = auth_api.retrieve_o_auth_token(x_api_key=os.getenv('DEEP_LYNX_API_KEY'),
                                                   x_api_secret=os.getenv('DEEP_LYNX_API_SECRET'),
                                                   x_api_expiry='12h')
        except TypeError:
            print("ERROR: Cannot connect to Dee pLynx.")
            logging.error("Cannot connect to Deep Lynx.")
            return '', '', None

        # Update header
        api_client.set_default_header('Authorization', 'Bearer {}'.format(token))

    # Get container ID
    container_id = None
    containers = None
    container_api = deep_lynx.ContainersApi(api_client)

    try:
        containers = container_api.list_containers()
    except TypeError or Exception:
        print("ERROR: Cannot connect to DeepLynx.")
        logging.error("Cannot connect to DeepLynx.")
        return '', '', None

    for container in containers.value:
        if container.name == os.getenv('CONTAINER_NAME'):
            container_id = container.id
            continue

    if container_id is None:
        print("ERROR: Container not found")
        logging.error("ERROR: Container not found")
        return '', '', None

    # Get data source ID, create if necessary
    data_source_id = None
    datasources_api = deep_lynx.DataSourcesApi(api_client)

    datasources = datasources_api.list_data_sources(container_id)
    for datasource in datasources.value:
        if datasource.name == os.getenv('DATA_SOURCE_NAME'):
            data_source_id = datasource.id
    if data_source_id is None:
        datasource = datasources_api.create_data_source(
            deep_lynx.CreateDataSourceRequest(os.getenv('DATA_SOURCE_NAME'), 'standard', True), container_id)
        data_source_id = datasource.value.id

    return container_id, data_source_id, api_client


def initiate_file_processor():
    """
    Initiates the processing the files in the data historian file
    Args
        None
    Return
        None
    """
    global thread_counter

    start_time = time.time()
    while True:
        end_time = time.time()
        if int(end_time - start_time) == int(os.getenv("FILE_SECONDS")):
            start_time = time.time()
            file_handler_name = "file_handler_thread_" + str(thread_counter)
            # Thread object: activity that is run in a separate thread of control
            file_handler_thread = threading.Thread(target=main, name=file_handler_name)
            print("Created ", file_handler_name)
            threads.append(file_handler_thread)
            thread_counter += 1
            # Start the thread’s activity
            file_handler_thread.start()
            # Join: Wait until the thread terminates. This blocks the calling thread until the thread whose join() method is called terminates.
            file_handler_thread.join()
            print(file_handler_name, " is done")
