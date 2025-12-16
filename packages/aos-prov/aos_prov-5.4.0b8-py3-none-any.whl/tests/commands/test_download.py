#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import os
import tarfile
import tempfile
from pytest import raises
from pathlib import Path
from unittest import mock

from aos_prov.commands.download import download_and_save_multinode
from aos_prov.utils.common import NODE_MAIN_IMAGE_FILENAME
from aos_prov.utils.errors import AosProvError
from requests import HTTPError
from tests.fixtures import mock_response



# @mock.patch('pathlib.Path.home')
# @mock.patch('requests.get')
# def test_download_and_save_multinode(mock_get, mock_home, tmp_path):
#     image_test_path = tempfile.NamedTemporaryFile(delete=False)
#     image_test_path.write(b'some_data')
#     image_test_path.close()
#     tar_test_path = tempfile.NamedTemporaryFile(delete=False)
#     # opening the file in write mode
#     tar_test = tarfile.open(tar_test_path.name, 'w')
#     tar_test.add(image_test_path.name)
#     tar_test.close()
#     mock_resp = mock_response(content=tar_test_path.read())
#     tar_test_path.close()
#     mock_get.return_value = mock_resp
#     tmp_directory = tmp_path
#     mock_home.return_value = Path(tmp_directory)
#     download_and_save_multinode('developer.cloud.io', Path(tmp_directory), True)
#     assert 'tmp' in os.listdir(f'{tmp_directory}/')
#     assert os.path.basename(image_test_path.name) in os.listdir(f'{tmp_directory}/tmp/')


@mock.patch('pathlib.Path.home')
@mock.patch('requests.get')
def test_download_and_save_multinode_without_extract(mock_get, mock_home):
    image_test_path = tempfile.NamedTemporaryFile(delete=False)
    image_test_path.write(b'some_data')
    image_test_path.close()
    tar_test_path = tempfile.NamedTemporaryFile(delete=False)
    # opening the file in write mode
    tar_test = tarfile.open(tar_test_path.name, 'w')
    tar_test.add(image_test_path.name)
    tar_test.close()
    mock_resp = mock_response(content=tar_test_path.read(), content_length=False)
    tar_test_path.close()
    mock_get.return_value = mock_resp
    with tempfile.TemporaryDirectory() as tmp_directory:
        mock_home.return_value = Path(tmp_directory)
        download_and_save_multinode('developer.cloud.io', Path(tmp_directory), True)
        assert 'downloaded-multi-node-images.tar.gz' in os.listdir(f'{tmp_directory}/')


@mock.patch('pathlib.Path.home')
@mock.patch('requests.get')
def test_download_and_save_multinode_failed_response(mock_get, mock_home):
    mock_resp = mock_response(status=500, raise_for_status=HTTPError('cloud is down'))
    mock_get.return_value = mock_resp
    with tempfile.TemporaryDirectory() as tmp_directory:
        mock_home.return_value = Path(tmp_directory)
        with raises(HTTPError):
            download_and_save_multinode('developer.cloud.io', Path(tmp_directory), True)


@mock.patch('pathlib.Path.home')
def test_download_and_save_multinode_failed_file_exists(mock_home):
    with tempfile.TemporaryDirectory() as tmp_directory:
        mock_home.return_value = Path(tmp_directory)

        file_node = open(os.path.join(tmp_directory, NODE_MAIN_IMAGE_FILENAME), 'w')
        file_node.write('data')
        file_node.close()
        with raises(AosProvError):
            download_and_save_multinode('developer.cloud.io', Path(tmp_directory), False)
