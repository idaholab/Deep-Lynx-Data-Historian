# Copyright 2022, Battelle Energy Alliance, LLC

import os
import glob
import json
import logging
import datetime
import sys
import time
import deep_lynx

from .file_processor import *
import src


def process_files(files: list = None):
    """ 
    Sends files to be processed and ingested to Deep Lynx

    Args
        files (list): a list of files to be processed
    Return
        None
    """

    # A list of .json file(s) containing the payload that will imported and ingested to the Deep Lynx graph via the typemappings system
    file_transformations = json.loads(os.getenv("FILE_TRANSFORMATIONS"))
    # A list of .json file(s) containing the payload (metadata) that a file will be attached to in Deep Lynx
    metadata_files = json.loads(os.getenv("METADATA_FILES"))

    processor = Processor(src.api_client)

    # For each file provided, parse and send to Deep Lynx
    for i, file in enumerate(files):
        # Assign metadata file if provided
        metadata_file = None
        if metadata_files and len(metadata_files) >= i:
            metadata_file = metadata_files[i]

        # Handle wildcard characters and directories
        if file[-1] == '*':
            file_search = glob.glob(file)

            # Process all matching files
            for file_search_entry in file_search:
                print(f"Sending {file} to be processed")
                logging.info(f"Sending {file_search_entry} to be processed")
                processor.file_processor(file_search_entry, file_transformations[i], metadata_file)

        elif file[-1] == '/' or file[-1] == '\\':
            file_search = os.listdir(file)

            # Process all files found in the directory
            for file_search_entry in file_search:
                full_path = os.path.join(file, file_search_entry)

                print(f"Sending {file} to be processed")
                logging.info(f"Sending {full_path} to be processed")
                processor.file_processor(full_path, file_transformations[i], metadata_file)

        else:
            print(f"Sending {file} to be processed")
            logging.info(f"Sending {file} to be processed")
            processor.file_processor(file, file_transformations[i], metadata_file)


def main():
    """ 
    Data Historian start of execution
    
    Args
        None
    Return
        None
    """
    # TODO: Change according to user's file
    # Read file
    file_df = pd.read_csv(os.getenv("SERVER_FILE_PATH"))

    # Drop un-needed columns
    keep_columns = json.loads(os.getenv("COLUMNS_KEEP"))
    if keep_columns:
        file_columns = file_df.columns.values.tolist()
        file_drop_columns = list()
        for column in file_columns:
            if not any(column_name in column for column_name in keep_columns):
                file_drop_columns.append(column)
        file_df.drop(file_drop_columns, axis=1, inplace=True)

    # Drop un-needed rows
    file_seconds = float(os.getenv("FILE_SECONDS"))
    total_row_length = file_df.shape[0] - 1
    start_row = int(total_row_length - file_seconds)
    file_drop_rows = [i for i in range(0, start_row + 1)]
    file_df.drop(file_drop_rows, axis=0, inplace=True)

    # Rename the file
    # TODO: Change to custom file name. Note extension is .csv
    date = datetime.datetime.now()
    date_name = date.strftime('%Y-%m-%d--%H-%M-%S')
    file_name = os.getenv("CONTAINER_NAME") + date_name + ".csv"
    local_file_path = os.path.abspath(os.path.join("data", file_name))

    # Write csv
    file_df.to_csv(local_file_path, index=False)

    # Process files
    files = list()
    files.append(local_file_path)
    process_files(files)


if __name__ == '__main__':
    main()
