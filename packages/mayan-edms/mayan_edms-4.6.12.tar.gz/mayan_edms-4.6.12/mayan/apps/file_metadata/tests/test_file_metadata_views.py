from mayan.apps.testing.tests.base import GenericViewTestCase

from ..permissions import permission_file_metadata_view

from .mixins.file_metadata_mixins import FileMetadataDriverTestMixin


class FileMetadataDriverViewTestCase(
    FileMetadataDriverTestMixin, GenericViewTestCase
):
    def test_file_metadata_driver_list_view_no_permission(self):
        self._clear_events()

        response = self._request_file_metadata_driver_list_view()
        self.assertEqual(response.status_code, 403)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_file_metadata_driver_list_view_with_permission(self):
        self.grant_permission(
            permission=permission_file_metadata_view
        )

        self._clear_events()

        response = self._request_file_metadata_driver_list_view()
        self.assertEqual(response.status_code, 200)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
