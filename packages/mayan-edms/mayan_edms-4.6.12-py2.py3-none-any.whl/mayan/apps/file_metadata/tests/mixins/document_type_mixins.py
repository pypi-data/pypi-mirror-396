from .file_metadata_mixins import FileMetadataTestMixin


class DocumentTypeViewTestMixin(FileMetadataTestMixin):
    def _request_document_type_file_metadata_settings_view(self):
        return self.get(
            viewname='file_metadata:document_type_file_metadata_settings',
            kwargs={'document_type_id': self._test_document.document_type.pk}
        )

    def _request_document_type_file_metadata_submit_view(self):
        return self.post(
            viewname='file_metadata:document_type_file_metadata_submit', data={
                'document_type': self._test_document_type.pk,
            }
        )
