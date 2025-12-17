from django.utils.module_loading import import_string

from ...classes import FileMetadataDriver

from ..literals import TEST_DRIVER_CLASS_PATH


class FileMetadataTestMixin:
    _test_document_file_metadata_driver_path = TEST_DRIVER_CLASS_PATH

    def setUp(self):
        super().setUp()
        FileMetadataDriver.load_modules()

        FileMetadataDriver.collection.do_driver_disable_all()

        if self._test_document_file_metadata_driver_path:
            self._test_document_file_metadata_driver = import_string(
                dotted_path=self._test_document_file_metadata_driver_path
            )
            self._test_document_file_metadata_driver.do_model_instance_populate()
            FileMetadataDriver.collection.do_driver_enable(
                driver=self._test_document_file_metadata_driver
            )


class FileMetadataDriverTestMixin(FileMetadataTestMixin):
    def _request_file_metadata_driver_list_view(self):
        return self.get(viewname='file_metadata:file_metadata_driver_list')
