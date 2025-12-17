from mayan.apps.documents.tests.base import GenericDocumentViewTestCase

from ..events import (
    event_file_metadata_document_file_finished,
    event_file_metadata_document_file_submitted
)
from ..permissions import (
    permission_document_type_file_metadata_setup,
    permission_file_metadata_submit
)

from .mixins.document_type_mixins import DocumentTypeViewTestMixin


class DocumentTypeViewTestCase(
    DocumentTypeViewTestMixin, GenericDocumentViewTestCase
):
    def test_document_type_settings_view_no_permission(self):
        self._clear_events()

        response = self._request_document_type_file_metadata_settings_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_type_settings_view_with_access(self):
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_document_type_file_metadata_setup
        )

        self._clear_events()

        response = self._request_document_type_file_metadata_settings_view()
        self.assertEqual(response.status_code, 200)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_type_submit_view_no_permission(self):
        file_metadata_driver_count = self._test_document.file_latest.file_metadata_drivers.count()

        self._clear_events()

        response = self._request_document_type_file_metadata_submit_view()
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self._test_document.file_latest.file_metadata_drivers.count(),
            file_metadata_driver_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_type_submit_view_with_access(self):
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_file_metadata_submit
        )

        file_metadata_driver_count = self._test_document.file_latest.file_metadata_drivers.count()

        self._clear_events()

        response = self._request_document_type_file_metadata_submit_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self._test_document.file_latest.file_metadata_drivers.count(),
            file_metadata_driver_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 2)

        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].target, self._test_document_file)
        self.assertEqual(
            events[0].verb, event_file_metadata_document_file_submitted.id
        )

        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].action_object, self._test_document)
        self.assertEqual(events[1].target, self._test_document_file)
        self.assertEqual(
            events[1].verb, event_file_metadata_document_file_finished.id
        )

    def test_trashed_document_document_type_submit_view_with_access(self):
        self.grant_access(
            obj=self._test_document_type,
            permission=permission_file_metadata_submit
        )

        self._test_document.delete()

        file_metadata_driver_count = self._test_document.file_latest.file_metadata_drivers.count()

        self._clear_events()

        response = self._request_document_type_file_metadata_submit_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self._test_document.file_latest.file_metadata_drivers.count(),
            file_metadata_driver_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
