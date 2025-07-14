import unittest
from unittest.mock import patch, MagicMock

# Import the function to test
from db.firebase import load_session_summary

class TestLoadSessionSummary(unittest.TestCase):
    @patch("db.firebase.db")
    def test_load_session_summary_exists(self, mock_db):
        # Setup mock Firestore document with summary
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"summary": "Test summary"}
        mock_session_ref = MagicMock()
        mock_session_ref.get.return_value = mock_doc
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_session_ref

        summary = load_session_summary("user123", "session456")
        self.assertEqual(summary, "Test summary")

    @patch("db.firebase.db")
    def test_load_session_summary_not_exists(self, mock_db):
        # Setup mock Firestore document without summary
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_session_ref = MagicMock()
        mock_session_ref.get.return_value = mock_doc
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_session_ref

        summary = load_session_summary("user123", "session456")
        self.assertEqual(summary, "")

if __name__ == "__main__":
    unittest.main()
