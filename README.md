# Deep Lynx Data Historian Adapter

Deep Lynx Data Historian Adapter

This software is intended to facilitate the ingestion of data from some data historian into [Deep Lynx](https://github.com/idaholab/Deep-Lynx). A data historian in this instance is any location where sensor and operational data from some live asset is gathered. The data can be either manual retrieved by this software or the data historian source can push to a listening endpoint provided by this software.

## Data Historian Overview

Deep Lynx Data Historian facilitates the ingestion of data from some data historian into Deep Lynx via manual retrieval or a listening endpoint. Two modes for data retrieval:
1. Manual Retrieval
    * Data is manually retrieved by reading a file located on an external file system (i.e. server). Note: Current implementation
2. Listening Endpoint
    * The data historian source pushes data to a listening endpoint provided by this software (i.e. `/historian`). Note: Architecture exists, but the responsibility is on the user to implement. See the `file_handler()` function in `src/__init__.py`

## Data Historian: Manual Retrieval

Data is manually retrieved by reading a file located on an external file system, such as a server, using a mount point. A mount point is a directory (typically an empty one) in the currently accessible filesystem on which an additional filesystem is mounted (i.e., logically attached). To create this mount point, the `REPOSITORY_MOUNT_DIRECTORY`, `SERVER_DIRECTORY_PATH`, and `SERVER_FILE_PATH` environment variables must be set. See the `Environment Variables` section for more details.

There are two ways to ingest data into Deep Lynx:
1. Upload File
    * A file is attached to the payload (metadata) provided for insertion into Deep Lynx. The `METADATA_FILES` environment variable must be set (leave `FILE_TRANSFORMATIONS` empty). Note: Current implementation
2. Transformations
    * The JSON payload is provided that will imported and ingested to the Deep Lynx graph via the typemappings system. Create a script to build your payload in the `transformations/` directory. The `FILE_TRANSFORMATIONS` environment variable must be set (leave `METADATA_FILES` empty). 

## Environment Variables (.env file)
To run this code, first copy the `.env_sample` file and rename it to `.env`. Several parameters must be present:
* DEEP_LYNX_URL: The base URL at which calls to Deep Lynx should be sent
* CONTAINER_NAME: The container name within Deep Lynx
* DATA_SOURCE_NAME: A name for this data source to be registered with Deep Lynx
* REPOSITORY_MOUNT_DIRECTORY: A given location (mount point) where a file system is mounted to
* SERVER_DIRECTORY_PATH: The location of the external file system
* SERVER_FILE_PATH: The path to a file located on the external file system to read from
* COLUMNS_KEEP: Column headers within file to keep
* METADATA_FILES: Paths to .json file(s) containing the payload (metadata) that a file will be attached to in Deep Lynx 
* FILE_TRANSFORMATIONS: Paths to .json file(s) containing the payload that will imported and ingested to the Deep Lynx graph via the typemappings system
* FILE_SECONDS: Number of seconds to wait between attempts to locate a file. 
* DELETE_FILE_FLAG: Set to True to delete files after they are successfully processed and ingested to Deep Lynx

## Getting Started 
* Complete the [Poetry installation](https://python-poetry.org/) 
* All following commands are run in the root directory of the project:
    * Run `poetry update` to install the defined dependencies for the project.
    * Run `poetry shell` to spawns a shell.
    * Finally, run the project with the command `flask run`

Logs will be written to a log file, stored in the root directory of the project. The log filename is set in `src/__init__.py` and is called `DataHistorianAdapter.log`. 

## Contributing

This project uses [yapf](https://github.com/google/yapf) for formatting. Please install it and apply formatting before submitting changes.
1. `poetry shell`
2. `yapf --in-place --recursive . --style={column_limit:120}`)

## Other Software
Idaho National Laboratory is a cutting edge research facility which is a constantly producing high quality research and software. Feel free to take a look at our other software and scientific offerings at:

[Primary Technology Offerings Page](https://www.inl.gov/inl-initiatives/technology-deployment)

[Supported Open Source Software](https://github.com/idaholab)

[Raw Experiment Open Source Software](https://github.com/IdahoLabResearch)

[Unsupported Open Source Software](https://github.com/IdahoLabUnsupported)

## License

Copyright 2022 Battelle Energy Alliance, LLC

Licensed under the LICENSE TYPE (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://opensource.org/licenses/MIT  

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.



Licensing
-----
This software is licensed under the terms you may find in the file named "LICENSE" in this directory.


Developers
-----
By contributing to this software project, you are agreeing to the following terms and conditions for your contributions:

You agree your contributions are submitted under the MIT license. You represent you are authorized to make the contributions and grant the license. If your employer has rights to intellectual property that includes your contributions, you represent that you have received permission to make contributions and grant the required license on behalf of that employer.

