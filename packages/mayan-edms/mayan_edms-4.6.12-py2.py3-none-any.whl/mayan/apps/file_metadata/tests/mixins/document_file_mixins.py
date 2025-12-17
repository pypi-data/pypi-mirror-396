from mayan.apps.documents.tests.mixins.document_mixins import (
    DocumentTestMixin
)

from ..literals import TEST_FILE_METADATA_KEY, TEST_FILE_METADATA_VALUE

from .file_metadata_mixins import FileMetadataTestMixin


class DocumentFileMetadataTestMixin(
    DocumentTestMixin, FileMetadataTestMixin
):
    _test_document_file_metadata_create_auto = False

    def setUp(self):
        super().setUp()

        if self._test_document_file_metadata_create_auto:
            self._test_document_file_metadata_create()

    def _test_document_file_metadata_create(self):
        self._test_document_file_driver_entry, created = self._test_document_file.file_metadata_drivers.get_or_create(
            driver=self._test_document_file_metadata_driver.model_instance
        )

        self._test_document_file_metadata = self._test_document_file_driver_entry.entries.create(
            key=TEST_FILE_METADATA_KEY,
            value=TEST_FILE_METADATA_VALUE
        )

        self._test_document_file_metadata_path = '{}__{}'.format(
            self._test_document_file_driver_entry.driver.internal_name,
            self._test_document_file_metadata.key
        )


class DocumentFileMetadataViewTestMixin(DocumentFileMetadataTestMixin):
    def _request_document_file_metadata_driver_list_view(self):
        return self.get(
            viewname='file_metadata:document_file_metadata_driver_list',
            kwargs={'document_file_id': self._test_document_file.pk}
        )

    def _request_document_file_metadata_list_view(self):
        return self.get(
            viewname='file_metadata:document_file_metadata_driver_attribute_list',
            kwargs={
                'document_file_driver_id': self._test_document_file_driver_entry.pk
            }
        )

    def _request_document_file_metadata_single_submit_view(self):
        return self.post(
            viewname='file_metadata:document_file_metadata_single_submit',
            kwargs={'document_file_id': self._test_document_file.pk}
        )

    def _request_document_file_multiple_submit_view(self):
        return self.post(
            viewname='file_metadata:document_file_metadata_multiple_submit',
            data={
                'id_list': self._test_document_file.pk
            }
        )
