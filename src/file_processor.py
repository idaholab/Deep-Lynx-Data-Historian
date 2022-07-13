# Copyright 2022, Battelle Energy Alliance, LLC

from importlib.metadata import metadata
import os
import json
import logging
import pandas as pd
import deep_lynx

import src


class Processor:

    def __init__(self, api_client):
        self.api_client = src.api_client

    def file_processor(self, file, transformation, metadata=None):
        """
        Processes a given file for ingestion to Deep Lynx

        Args
            file: the file to process
            transformation (optional): path to the .json file containing the payload that will imported and ingested to the Deep Lynx graph via the typemappings system
            metadata (optional): path to the .json file for metadata to be sent with the file
        Return
            boolean indicating successful ingestion or failure
        """

        # Apply transformations if provided
        if transformation != "":

            # Determine file type
            split_tup = os.path.splitext(file)

            # Loads .csv or .json file
            json_data = {}
            if split_tup[1] == '.csv':
                json_data = self.read_csv(file)
            elif split_tup[1] == '.json':
                json_data = self.read_json(file)
            else:
                print(f"WARNING: Unsupported file type supplied: {file}")
                logging.warning(f"Unsupported file type supplied: {file}")
                return False

            # Read transformation file containing the payload that will imported and ingested to the Deep Lynx graph via the typemappings system
            try:
                result = self.read_json(transformation)
            except Exception:
                print(
                    f"ERROR: Supplied file {transformation} is not found. Supply a .json file for the transformation.")
                logging.error(
                    f"ERROR: Supplied file {transformation} is not found. Supply a .json file for the transformation.")

            # Send processed file to DeepLynx for ingestion
            try:
                datasources_api = deep_lynx.DataSourcesApi(self.api_client)
                import_result = datasources_api.create_manual_import(result, os.getenv("CONTAINER_ID"),
                                                                     os.getenv("DATA_SOURCE_ID"))
                logging.info(f"Import for file {file} to DL: {import_result}")

            except Exception as e:
                print("Error: Could not send data to DeepLynx. See logs for more information.")
                logging.error("Error: Could not send data to DeepLynx.", e)
                return False

        else:

            # No transformation provided, send file directly to Deep Lynx
            try:
                datasources_api = deep_lynx.DataSourcesApi(self.api_client)

                # Upload file whether metadata is supplied or not
                if metadata is not None:
                    file_result = datasources_api.upload_file(container_id=os.getenv("CONTAINER_ID"),
                                                              data_source_id=os.getenv("DATA_SOURCE_ID"),
                                                              file=file,
                                                              metadata=metadata,
                                                              async_req=False)
                else:
                    file_result = datasources_api.upload_file(container_id=os.getenv("CONTAINER_ID"),
                                                              data_source_id=os.getenv("DATA_SOURCE_ID"),
                                                              file=file,
                                                              async_req=False)

                print((f"File {file} sent to DL: {file_result}"))
                logging.info(f"File {file} sent to DL: {file_result}")

            except Exception as e:
                print("Error: Could not send file to DeepLynx. See logs for more information.")
                logging.error("Error: Could not send file to DeepLynx.", e)
                return False

        # At this point, transformations and ingestion to DeepLynx are successful. Delete file if indicated
        delete_file_flag = os.getenv("DELETE_FILE_FLAG")
        if delete_file_flag == 'True':
            if os.path.exists(file):
                os.remove(file)
            logging.info(f"File {file} successfully deleted.")

        return True

    def read_json(self, file):
        """
        Read json file and return json dictionary

        Args
            file: the file to read
        Return
            json dictionary
        """
        f = open(file)
        json_dict = json.load(f)
        f.close()
        return json_dict

    def read_csv(self, file):
        """
        Read csv file and return json dictionary

        Args
            file: the file to read
        Return
            json dictionary
        """
        data = pd.read_csv(file, delimiter=',')
        json_dict = pd.DataFrame.to_json(data, orient='records')
        return json_dict
