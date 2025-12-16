#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2025 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
From the Gitlab CI/CD pipeline: download files and dirs from the S3 buckets.
"""
import concurrent.futures
import logging
import os
import os.path as osp
import shutil
import sys
from pathlib import Path

# Please install "aiobotocore[boto3]" to preserve compatility with s3fs, using:
#   python -m pip install "aiobotocore[boto3]"
import boto3

# The access keys are defined in Gitlab -> Settings -> CI/CD -> Variables

# Global thread pool for archive extraction
_archive_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def check_and_download(bucket, key: str, dest: Path):
    """
    do not download file "key" if it already exists, save bandwith
    * https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
    * https://docs.python.org/3/library/hashlib.html#hashlib.md5
    * https://stackoverflow.com/a/75933922
    """
    if not dest.exists():
        logging.debug("Downloading '%s'", dest)
        parent = dest.parent
        if not parent.exists():
            parent.mkdir(parents=True)

        # bucket: boto3.resources.factory.s3.Bucket
        # download_file: boto3.s3.transfer.S3Transfer.download_file
        try:
            bucket.download_file(key, dest)
            logging.info("Downloaded '%s'", dest)
            return dest.exists()
        except Exception:
            return False
    else:
        # TODO # Check file size and MD5 checksum
        # s3_obj = bucket.Object(key)
        # s3_size = s3_obj.content_length
        # s3_etag = s3_obj.e_tag.strip('"')
        # local_size = os.path.getsize(dest)
        # def md5sum(filename):
        #     hash_md5 = hashlib.md5()
        #     with open(filename, "rb") as f:
        #         for chunk in iter(lambda: f.read(4096), b""):
        #             hash_md5.update(chunk)
        #     return hash_md5.hexdigest()
        # local_md5 = md5sum(dest)
        # if local_size != s3_size or local_md5 != s3_etag:
        #     logging.info("Local file '%s' differs from S3 (size or checksum), re-downloading.", dest)
        #     bucket.download_file(key, dest)
        # else:
        #     logging.debug("Skip '%s' already exists and matches S3", dest)
        logging.debug("Skip '%s' already exists", dest)
        return True


def download_and_extract(bucket, key, dest: Path, extract_dir: Path = None):
    """do not download archive if it was already extracted, save bandwith"""
    if extract_dir is None:
        extract_dir = dest.parent
    # bucket: boto3.resources.factory.s3.Bucket
    # dest.parent: The logical parent of the path
    # dest.stem: The final path component, minus its last suffix
    # stem: dest, minus its last suffix
    stem: Path = dest.parent / dest.stem
    # check ".tar" extension in case of dest = "/path/to/archive.tar.gz"
    if dest.stem.endswith(".tar"):
        stem: Path = dest.parent / stem.stem
    if not stem.exists():
        if check_and_download(bucket, key, dest):
            _archive_executor.submit(extract_archive, dest, extract_dir)
        else:
            return False
    else:
        logging.debug("Skip '%s' already exists", stem)
    return True


def extract_archive(archive_path: Path, extract_dir: Path):
    """Uncompress archive"""
    logging.info("Extract %r archive", archive_path)
    # Should take care of: https://peps.python.org/pep-0706/ & CVE-2007-4559
    shutil.unpack_archive(archive_path, extract_dir)


# Single thread function, as boto3' s3transfer is multi-threaded
# https://gitlab.eopf.copernicus.eu/geolib/asgard/-/issues/312
def _download_s3_dir(bucket, directory: str, destination: Path):
    target = destination / directory
    if target.exists():
        logging.debug("Skip downloading directory '%s' into '%s' as it already exists", directory, destination)
        return
    zip_file = f"{directory}.zip"
    logging.debug("Check if '%s' exists", zip_file)
    if download_and_extract(bucket, zip_file, destination / zip_file, target):
        return
    logging.warning("Could not find a zip version of '%s'. Please consider uploading one", directory)
    objects = [str(obj.key) for obj in bucket.objects.filter(Prefix=directory)]
    logging.info("Downloading all files from '%s' into '%s'", directory, destination)
    length = len(objects)
    percent = 100.0 / length
    for indice, obj in enumerate(objects, start=1):
        logging.info("Download %3.1f %% (%4i / %4i) %r", indice * percent, indice, length, obj)
        check_and_download(bucket, obj, destination / obj)


def _download_common(destination: Path):
    """
    Download resources from "common" bucket.

    :param destination: Where the resource will be downloaded to
    :param targets:     Filter to specify which exact (file) resource will be downloaded.
                        Possible values are:
                        - None: download everything: files **AND** directories
                        - S3ASLSTRdataset: only S3ASLSTRdataset/*.zip, no directory
                        - S3AOLCIdataset: only S3AOLCIdataset/*.zip, no directory
    """
    s3_common = boto3.resource(
        service_name="s3",
        region_name="sbg",
        endpoint_url="https://s3.sbg.perf.cloud.ovh.net",
        aws_access_key_id=os.environ["S3_DPR_COMMON_ACCESS"],
        aws_secret_access_key=os.environ["S3_DPR_COMMON_SECRET"],
    )
    bucket = s3_common.Bucket("dpr-common")

    location = "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr"
    _download_s3_dir(bucket, location, destination)

    location = "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr"
    _download_s3_dir(bucket, location, destination)

    # location = "S3ASLSTRdataset/S3A_SL_0_SLT____20221101T204936_20221101T205436_20221101T212249_0299_091_314______PS1_O_NR_004.SEN3.zip"  # noqa E501
    # download_and_extract(bucket, location, destination / location)

    # location = "S3AOLCIdataset/S3__AX___DEM_AX_20000101T000000_20991231T235959_20151214T120000___________________MPC_O_AL_001.SEN3.tgz"  # noqa E501
    # download_and_extract(bucket, location, destination / location)

    # location = "S1ASARdataset/S1A_EW_RAW__0SDH_20221111T114657_20221111T114758_045846_057C1E_9592.SAFE.zip"
    # download_and_extract(bucket, location, destination / location)

    location = "ADFdynamic/S0__ADF_IERSB_19920101T000000_20220630T000000_20220701T101100.txt"
    check_and_download(bucket, location, destination / location)


def _download_geolib_input(destination: Path, slow: bool):
    geolib_input = boto3.resource(
        service_name="s3",
        region_name="sbg",
        endpoint_url="https://s3.sbg.perf.cloud.ovh.net",
        aws_access_key_id=os.environ["S3_DPR_GEOLIB_INPUT_RO_ACCESS"],
        aws_secret_access_key=os.environ["S3_DPR_GEOLIB_INPUT_RO_SECRET"],
    )
    bucket = geolib_input.Bucket("dpr-geolib-input")

    location = "S2MSIdataset/S2MSIdataset_flat.tgz"
    logging.debug("Download from S3: %s to %s", location, destination)
    download_and_extract(bucket, location, destination / location)

    location = osp.join("DEM_natif", "legacy", "GETASSE30")
    _download_s3_dir(bucket, location, destination)

    location = "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20230428T185052.zarr"
    _download_s3_dir(bucket, location, destination)

    location = "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240325T113307.zarr"
    _download_s3_dir(bucket, location, destination)

    if slow:
        locations = [
            "S2MSIdataset/S2MSI_TDS1",
            "S2MSIdataset/S2MSI_TDS2",
            # "S2MSIdataset/S2MSI_TDS3",
            # "S2MSIdataset/S2MSI_TDS4",
            "S2MSIdataset/S2MSI_TDS5",
            # "S2MSIdataset/S2MSI_TDS1_INVLOC",
            # "S2MSIdataset/S2MSI_TDS2_INVLOC",
            # "S2MSIdataset/S2MSI_TDS3_INVLOC",
            # "S2MSIdataset/S2MSI_TDS4_INVLOC",
            # "S2MSIdataset/S2MSI_TDS5_INVLOC",
        ]
    else:
        locations = [
            "S2MSIdataset/S2MSI_TDS1",
            # "S2MSIdataset/S2MSI_TDS2",
            # "S2MSIdataset/S2MSI_TDS3",
            # "S2MSIdataset/S2MSI_TDS4",
            # "S2MSIdataset/S2MSI_TDS5",
            # "S2MSIdataset/S2MSI_TDS1_INVLOC",
            # "S2MSIdataset/S2MSI_TDS2_INVLOC",
            # "S2MSIdataset/S2MSI_TDS3_INVLOC",
            # "S2MSIdataset/S2MSI_TDS4_INVLOC",
            # "S2MSIdataset/S2MSI_TDS5_INVLOC",
        ]
    for location in locations:
        logging.debug("Download from S3: %s to %s", location, destination)
        _download_s3_dir(bucket, location, destination)


def _download_validation_input(destination: Path):
    geolib_input = boto3.resource(
        service_name="s3",
        region_name="sbg",
        endpoint_url="https://s3.sbg.perf.cloud.ovh.net",
        aws_access_key_id=os.environ["S3_DPR_GEOLIB_INPUT_RO_ACCESS"],
        aws_secret_access_key=os.environ["S3_DPR_GEOLIB_INPUT_RO_SECRET"],
    )
    bucket = geolib_input.Bucket("dpr-geolib-input")

    locations = ["OLCI_validation", "OLCI_RAC_validation", "SLSTR_validation", "SRAL_validation", "MWR_validation"]

    for location in locations:
        _download_s3_dir(bucket, location, destination)

    olci_dirs = ["OLCI_TDS1", "OLCI_TDS2"]
    slstr_dirs = ["SLSTR_TDS1", "SLSTR_TDS2", "SLSTR_TDS3"]

    logging.debug("Downloading directory OLCI_TDS* from 'S3AOLCIdataset' into '%s'", destination)
    for olci_dir in olci_dirs:
        _download_s3_dir(bucket, osp.join("S3AOLCIdataset", olci_dir), destination)

    logging.debug("Downloading directory SLSTR_TDS* from 'S3ASLSTRdataset' into '%s'", destination)
    for slstr_dir in slstr_dirs:
        _download_s3_dir(bucket, osp.join("S3ASLSTRdataset", slstr_dir), destination)

    olci_files = {
        "S3A_OL_1_INS_AX_20201030T120000_20991231T235959_20220505T120000___________________MPC_O_AL_009.SEN3.tgz",
        "S3A_OL_1_CAL_AX_20230620T000000_20991231T235959_20230616T120000___________________MPC_O_AL_028.SEN3.tgz",
        "S3A_AX___OSF_AX_20160216T192404_99991231T235959_20220330T090651___________________EUM_O_AL_001.SEN3.tgz",
    }

    slstr_files = [
        "S3A_AX___FRO_AX_20221030T000000_20221109T000000_20221102T065450___________________EUM_O_AL_001.SEN3.zip",
        "S3A_SL_1_GEC_AX_20190101T000000_20991231T235959_20191010T120000___________________MPC_O_AL_009.SEN3.zip",
        "S3A_SL_1_GEO_AX_20160216T000000_20991231T235959_20190912T120000___________________MPC_O_AL_008.SEN3.zip",
        # "S3A_SL_0_SLT____20221101T204936_20221101T205436_20221101T212249_0299_091_314______PS1_O_NR_004.SEN3.zip",
    ]

    sral_files = [
        "S3B_AX___FRO_AX_20200708T000000_20200718T000000_20200711T065100___________________EUM_O_AL_001.SEN3.zip"
    ]

    mwr_files = [
        "S3A_AX___FRO_AX_20221030T000000_20221109T000000_20221102T065450___________________EUM_O_AL_001.SEN3.zip",
        "S3A_MW___CHDNAX_20160216T000000_20991231T235959_20210929T120000___________________MPC_O_AL_005.SEN3.zip",
    ]

    logging.debug("Downloading all files from 'S3AOLCIdataset' into '%s'", destination)
    for file in olci_files:
        loc = osp.join("S3AOLCIdataset", file)
        download_and_extract(bucket, loc, destination / loc)

    logging.debug("Downloading all files from 'S3ASLSTRdataset' into '%s'", destination)
    for file in slstr_files:
        loc = osp.join("S3ASLSTRdataset", file)
        download_and_extract(bucket, loc, destination / loc)

    logging.debug("Downloading all files from 'S3BSRALdataset' into '%s'", destination)
    for file in sral_files:
        loc = osp.join("S3BSRALdataset", file)
        download_and_extract(bucket, loc, destination / loc)

    logging.debug("Downloading all files from 'S3AMWRdataset' into '%s'", destination)
    for file in mwr_files:
        loc = osp.join("S3AMWRdataset", file)
        download_and_extract(bucket, loc, destination / loc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # Download files into the current directory. They will be extracted by the gitlab CI.
    DESTINATION = Path(os.environ.get("ASGARD_DATA", "ASGARD_DATA"))
    logging.info("Downloading ASGARD data into %s", DESTINATION.absolute())

    if "--debug" in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)

    # For the CI "test" stage
    if "test" in sys.argv:
        _download_common(DESTINATION)
        _download_geolib_input(DESTINATION, "slow" in sys.argv)
        _download_validation_input(DESTINATION)

    logging.info("All downloads submitted, waiting for archive extraction to complete...")
    # Wait for archive extraction to complete
    _archive_executor.shutdown(wait=True)
    logging.info("All extractions completed.")
