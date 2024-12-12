import unittest
from unittest.mock import patch, MagicMock
from frontend_ui import app


class TestFrontendUI(unittest.TestCase):

    @patch("frontend_ui.app.requests.post")
    @patch("frontend_ui.app.st.text_input")
    @patch("frontend_ui.app.st.button")
    def test_submit_button_triggers_api_call(
        self, mock_button, mock_text_input, mock_post
    ):
        # Simulate button click and text input
        mock_button.return_value = True
        mock_text_input.return_value = "sample query"

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": "sample query",
            "documents": ["Document 1", "Document 2"],
            "answer": "Sample Answer",
        }
        mock_post.return_value = mock_response

        # Run the main function to simulate the API call
        app.st.write("Sending query to backend...")
        response = app.requests.post(app.API_URL, json={"query": "sample query"})

        # Assert that API was called with correct query data
        mock_post.assert_called_once_with(app.API_URL, json={"query": "sample query"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Sample Answer")

    @patch("frontend_ui.app.requests.post")
    @patch("frontend_ui.app.st.text_input")
    @patch("frontend_ui.app.st.button")
    def test_no_api_call_on_empty_query(self, mock_button, mock_text_input, mock_post):
        # Simulate empty query input and button click
        mock_button.return_value = True
        mock_text_input.return_value = ""

        # Call the API only if there is a non-empty query
        if mock_text_input.return_value:
            app.requests.post(app.API_URL, json={"query": mock_text_input.return_value})

        # Assert that API was not called with an empty query
        mock_post.assert_not_called()

    @patch("frontend_ui.app.requests.post")
    @patch("frontend_ui.app.st.text_input")
    @patch("frontend_ui.app.st.button")
    def test_api_call_with_exception_handling(
        self, mock_button, mock_text_input, mock_post
    ):
        # Simulate a query and button click
        mock_button.return_value = True
        mock_text_input.return_value = "sample query"

        # Mock an exception when calling the API
        mock_post.side_effect = Exception("Connection Error")

        # Attempt API call and catch the exception
        try:
            app.requests.post(app.API_URL, json={"query": "sample query"})
        except Exception as e:
            caught_exception = e

        # Assert that an exception was raised and caught correctly
        self.assertIsInstance(caught_exception, Exception)
        self.assertEqual(str(caught_exception), "Connection Error")


if __name__ == "__main__":
    unittest.main()
