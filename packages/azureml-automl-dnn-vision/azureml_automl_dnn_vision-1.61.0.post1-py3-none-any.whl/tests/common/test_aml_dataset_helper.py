import os
import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import azureml.dataprep as dprep
import pandas as pd
import pytest
from _pytest.monkeypatch import MonkeyPatch
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from azureml.data.dataset_factory import FileDatasetFactory
from azureml.exceptions import UserErrorException

from .aml_dataset_mock import AmlDatasetMock
from .run_mock import DatastoreMock, ExperimentMock, RunMock, WorkspaceMock


class TestAmlDatasetHelper:
    def setup(self):
        self.monkey_patch = MonkeyPatch()

    def setup_class(cls):
        cls.temp_folder = tempfile.mkdtemp()

    def teardown_class(cls):
        shutil.rmtree(cls.temp_folder)

    def test_labeled_dataset_create_file_upload_path(self):
        datastore_name = "TestDatastoreName"
        datastore_mock = DatastoreMock(datastore_name)
        workspace_mock = WorkspaceMock(datastore_mock)
        experiment_mock = ExperimentMock(workspace_mock)
        run_mock = RunMock(experiment_mock)

        test_target_path = "TestTargetPath"
        labeled_dataset_file_name = "labeled_dataset.json"

        def _test_file_upload_path(monkey_patch, labeled_dataset_file):
            Path(labeled_dataset_file).touch()

            def _upload_directory_mock(directory, data_path, overwrite):
                assert len(data_path) == 2
                assert data_path[0] == datastore_mock
                assert data_path[1] == test_target_path
                assert overwrite

                # Check that labeled_dataset_file is copied at root of directory
                dir_files = os.listdir(directory)
                assert len(dir_files) == 1
                file_0_path = os.path.join(directory, dir_files[0])
                assert os.path.isfile(file_0_path)
                assert dir_files[0] == os.path.basename(labeled_dataset_file)

            with monkey_patch.context() as m:
                m.setattr(FileDatasetFactory, "upload_directory", _upload_directory_mock)
                with patch("azureml.core.Dataset.Tabular.from_json_lines_files"):
                    AmlDatasetHelper.create(run_mock, datastore_mock, labeled_dataset_file,
                                            test_target_path, "TestTask")

        with tempfile.TemporaryDirectory() as tmp_output_dir:
            labeled_dataset_file = os.path.join(tmp_output_dir, labeled_dataset_file_name)
            _test_file_upload_path(self.monkey_patch, labeled_dataset_file)

            dir_path = os.path.join(tmp_output_dir, "dir1", "dir2")
            labeled_dataset_file = os.path.join(dir_path, labeled_dataset_file_name)
            os.makedirs(dir_path, exist_ok=True)
            _test_file_upload_path(self.monkey_patch, labeled_dataset_file)

            try:
                _test_file_upload_path(self.monkey_patch, labeled_dataset_file_name)
            finally:
                os.remove(labeled_dataset_file_name)

    def test_init_non_existent_image_when_downloading_files(self):
        with patch('azureml.automl.dnn.vision.common.dataset_helper.AmlDatasetHelper.download_image_files') \
                as mock_download:
            dataset = self._build_mock_dataset(["AmlDatastore://non_existent_file.jpg"])
            helper = AmlDatasetHelper(dataset, ignore_data_errors=True, download_files=True)
            assert helper.images_df.empty
            mock_download.assert_called_once()

    def test_init_non_existent_image_when_not_downloading_files(self):
        dataset = self._build_mock_dataset(["AmlDatastore://non_existent_file.jpg"])
        helper = AmlDatasetHelper(dataset, ignore_data_errors=True, download_files=False)
        # Existence checks are too slow when mounted. Validate that existence check isn't performed
        assert len(helper.images_df) == 1

    @patch("azureml.automl.dnn.vision.common.dataset_helper.AmlDatasetHelper.mount_datastore")
    def test_mount_image_file_datastores(self, mock_mount_datastore):
        mounted_datastores = set()

        def mock_mount_datastore_side_effect(datastore_name, workspace):
            mounted_datastores.add(datastore_name)
        mock_mount_datastore.side_effect = mock_mount_datastore_side_effect

        dataset = self._build_mock_dataset([
            "AmlDatastore://datastore1/file1.jpg",
            "AmlDatastore://datastore2/file2.jpg",
            "AmlDatastore://datastore1/file3.jpg"
        ])
        AmlDatasetHelper.mount_image_file_datastores(
            ds=dataset,
            image_column_name=AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME,
            workspace=None)

        assert len(mounted_datastores) == 2
        assert "datastore1" in mounted_datastores
        assert "datastore2" in mounted_datastores

    def test_mount_image_file_datastores_errors_on_non_datastore_path(self):
        dataset = self._build_mock_dataset([
            "AmlDatastore://datastore1/file1.jpg",
            "http://www.microsoft.com/logo.jpg"
        ])
        with pytest.raises(AutoMLVisionDataException) as e:
            AmlDatasetHelper.mount_image_file_datastores(
                ds=dataset,
                image_column_name=AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME,
                workspace=None)
        assert "Reading directly from the Http protocol" in e.value.message

    def test_mount_image_file_datastores_errors_on_invalid_path(self):
        dataset = self._build_mock_dataset([
            "AmlDatastore1111://datastore1/file1.jpg"
        ])
        with pytest.raises(AutoMLVisionDataException) as e:
            AmlDatasetHelper.mount_image_file_datastores(
                ds=dataset,
                image_column_name=AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME,
                workspace=None)
        assert "Could not convert the dataset to a pandas data frame" in e.value.message

    def test_mount_image_file_datastores_errors_if_image_column_absent(self):
        dataset = self._build_mock_dataset([
            "AmlDatastore://datastore1/file1.jpg",
        ])
        with pytest.raises(AutoMLVisionDataException) as e:
            AmlDatasetHelper.mount_image_file_datastores(
                ds=dataset,
                image_column_name="invalid_column",
                workspace=None)
        assert "Image URL column 'invalid_column'" in e.value.message

    def test_mount_image_file_datastores_errors_if_image_column_data_type_isnt_stream(self):
        dflow = _get_dataflow_from_pandas(
            pd.DataFrame({AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME: ["AmlDatastore://datastore1/file1.jpg"]})
        ).set_column_types({"invalid_column": dprep.StreamInfoConverter(WorkspaceMock())})
        dataset = self._build_mock_dataset_from_dataflow(dflow)
        with pytest.raises(AutoMLVisionDataException) as e:
            AmlDatasetHelper.mount_image_file_datastores(
                ds=dataset,
                image_column_name=AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME,
                workspace=None)
        assert e.value.message == "The data type of image URL column 'image_url' is STRING, but it should be STREAM."

    @patch("azureml.core.Dataset.File", return_value=MagicMock())
    @patch("azureml.core.Datastore.get", return_value=MagicMock())
    def test_mount_datastore_each_datastore_only_mounted_once(self, mock_datastore_get, _):
        """Test that each datastore is only mounted once. If a datastore is mounted twice,
        an exception will be thrown.
        """
        AmlDatasetHelper.mount_datastore("datastore1", None)
        assert mock_datastore_get.call_count == 1
        AmlDatasetHelper.mount_datastore("datastore1", None)
        assert mock_datastore_get.call_count == 1
        AmlDatasetHelper.mount_datastore("datastore2", None)
        assert mock_datastore_get.call_count == 2

    @patch("azureml.core.Datastore.get", side_effect=UserErrorException("message"))
    def test_mount_datastore_user_error(self, _):
        with pytest.raises(AutoMLVisionDataException):
            AmlDatasetHelper.mount_datastore("datastore_exception", None)

    def test_download_image_files_errors_if_image_column_data_type_isnt_stream(self):
        dflow = _get_dataflow_from_pandas(
            pd.DataFrame({AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME: ["AmlDatastore://datastore1/file1.jpg"]})
        ).set_column_types({AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME: dprep.FieldType.STRING})
        dataset = self._build_mock_dataset_from_dataflow(dflow)

        with pytest.raises(AutoMLVisionDataException) as e:
            AmlDatasetHelper.download_image_files(
                ds=dataset,
                image_column_name=AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME)
        assert e.value.message == f"The data type of image URL column " \
                                  f"'{AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME}' is STRING, but it should be " \
                                  f"STREAM."

    def test_download_image_files_datastores_errors_if_image_column_absent(self):
        dataset = self._build_mock_dataset([
            "AmlDatastore://datastore1/file1.jpg",
        ])
        with pytest.raises(AutoMLVisionDataException) as e:
            AmlDatasetHelper.download_image_files(
                ds=dataset,
                image_column_name="invalid_column")
        assert "Image URL column 'invalid_column'" in e.value.message

    @pytest.mark.parametrize("filename", [
        "https%3A/%2Ftest%3Asemicolon/000000000.png",
        "https://test:semicolon/000000000.png"
    ])
    def test_write_dataset_file_line(self, filename):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            labeled_dataset_file = os.path.join(tmp_output_dir, "labeled_dataset_file_name.json")
            with open(labeled_dataset_file, "w") as ldsf:
                AmlDatasetHelper.write_dataset_file_line(ldsf, filename, confidence=[0.1], label=['a'])

            with open(labeled_dataset_file, "r") as rptr:
                lines = rptr.readlines()
                op_filename = json.loads(lines[0])["image_url"]
                assert op_filename == AmlDatasetHelper.DATASTORE_PREFIX + "https://test:semicolon/000000000.png"

    @classmethod
    def _build_mock_dataset(cls, image_urls):
        dflow = _get_dataflow_from_pandas(
            pd.DataFrame({AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME: image_urls})
        ).set_column_types(
            {AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME: dprep.StreamInfoConverter(WorkspaceMock())})
        return cls._build_mock_dataset_from_dataflow(dflow)

    @classmethod
    def _build_mock_dataset_from_dataflow(cls, dflow):
        return AmlDatasetMock(
            properties={
                AmlDatasetHelper.IMAGE_COLUMN_PROPERTY: {
                    AmlDatasetHelper.COLUMN_PROPERTY: AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME
                }},
            dataflow=dflow)


def _get_dataflow_from_pandas(df: pd.DataFrame) -> dprep.Dataflow:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    f = tmp.name
    tmp.close()
    df.to_csv(f)
    return dprep.read_csv(f)


if __name__ == "__main__":
    pytest.main([__file__])
