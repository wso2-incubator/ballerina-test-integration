# Copyright (c) 2018, WSO2 Inc. (http://wso2.com) All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# importing required modules
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import os
import stat
import sys
from pathlib import Path
import shutil
import logging
from const import ZIP_FILE_EXTENSION, NS, SURFACE_PLUGIN_ARTIFACT_ID, CARBON_NAME, VALUE_TAG, \
    DEFAULT_ORACLE_SID, DATASOURCE_PATHS, MYSQL_DB_ENGINE, ORACLE_DB_ENGINE, LIB_PATH, PRODUCT_STORAGE_DIR_NAME, \
    DISTRIBUTION_PATH, MSSQL_DB_ENGINE, M2_PATH

datasource_paths = None
database_url = None
database_user = None
database_pwd = None
database_drive_class_name = None
dist_name = None
storage_dist_abs_path = None
target_dir_abs_path = None
database_config = None
storage_dir_abs_path = None
workspace = None
sql_driver_location = None
product_id = None
database_names = []

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ZipFileLongPaths(ZipFile):
    def _extract_member(self, member, targetpath, pwd):
        targetpath = winapi_path(targetpath)
        return ZipFile._extract_member(self, member, targetpath, pwd)


def winapi_path(dos_path, encoding=None):
    path = os.path.abspath(dos_path)

    if path.startswith("\\\\"):
        path = "\\\\?\\UNC\\" + path[2:]
    else:
        path = "\\\\?\\" + path

    return path


def extract_product(path, ws):
    """Extract the zip file(product zip) which is located in the given @path.
    """
    if Path.exists(path):
        storage_dir_abs_path = Path(ws + "/" + PRODUCT_STORAGE_DIR_NAME)
        logger.info("Extracting the product  into " + str(storage_dir_abs_path))
        if sys.platform.startswith('win'):
            with ZipFileLongPaths(path, "r") as zip_ref:
                zip_ref.extractall(storage_dir_abs_path)
        else:
            with ZipFile(str(path), "r") as zip_ref:
                zip_ref.extractall(storage_dir_abs_path)
    else:
        raise FileNotFoundError("File is not found to extract, file path: " + str(path))


def add_distribution_to_m2(storage, name, product_version):
    """Add the distribution zip into local .m2.
    """
    home = Path.home()
    m2_rel_path = ".m2/repository/org/wso2/" + M2_PATH[product_id]
    linux_m2_path = home / m2_rel_path / product_version / name
    windows_m2_path = Path("/Documents and Settings/Administrator/" + m2_rel_path + "/" + product_version + "/" + name)
    if sys.platform.startswith('win'):
        windows_m2_path = winapi_path(windows_m2_path)
        storage = winapi_path(storage)
        compress_distribution(windows_m2_path, storage)
        shutil.rmtree(windows_m2_path, onerror=on_rm_error)
    else:
        compress_distribution(linux_m2_path, storage)
        shutil.rmtree(linux_m2_path, onerror=on_rm_error)



