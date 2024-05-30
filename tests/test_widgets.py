import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.forms import Form
from django.forms.fields import FileField
from django.test import TestCase, override_settings
from playwright.sync_api import sync_playwright

from droppablefileinput.widgets import DroppableFileInput


def assert_and_accept_dialog(dialog, expected_message):
    assert dialog.message == expected_message
    dialog.accept()


class TestDroppableFileInput(TestCase):
    def setUp(self):
        class TestForm(Form):
            file = FileField(
                widget=DroppableFileInput(
                    label="Test label",
                    auto_submit=True,
                    max_file_size="10M",
                    allowed_types="image/png,image/jpeg",
                    icon_url="/static/droppablefileinput/images/test_icon.svg",
                    icon_width=48,
                    icon_height=48,
                )
            )

        self.form = TestForm()

    def test_widget_rendering(self):
        rendered = self.form.as_p()
        self.assertIn("Test label", rendered)
        self.assertIn('data-auto-submit="True"', rendered)
        self.assertIn('data-max-file-size="10M"', rendered)
        self.assertIn('data-allowed-types="image/png,image/jpeg"', rendered)
        self.assertIn('src="/static/droppablefileinput/images/test_icon.svg"', rendered)
        self.assertIn('width="48"', rendered)
        self.assertIn('height="48"', rendered)

    def test_default_icon(self):
        class DefaultIconForm(Form):
            file = FileField(widget=DroppableFileInput())

        form = DefaultIconForm()
        rendered = form.as_p()
        self.assertIn('src="/static/droppablefileinput/images/icon.svg"', rendered)
        self.assertIn('width="32"', rendered)
        self.assertIn('height="32"', rendered)

    def test_js_css_inclusion(self):
        widget = DroppableFileInput()
        media = str(widget.media)
        self.assertIn("droppablefileinput/css/droppable_file_input.css", media)
        self.assertIn("droppablefileinput/js/droppable_file_input.js", media)

    def test_template_context(self):
        widget = DroppableFileInput(
            label="Context label", auto_submit=True, max_file_size="20M", allowed_types="application/pdf"
        )
        context = widget.get_context("file", None, {"id": "file_id"})
        self.assertEqual(context["widget"]["label"], "Context label")
        self.assertEqual(context["widget"]["auto_submit"], True)
        self.assertEqual(context["widget"]["max_file_size"], "20M")
        self.assertEqual(context["widget"]["allowed_types"], "application/pdf")

    def test_widget_attrs(self):
        widget = DroppableFileInput(attrs={"class": "custom-class", "accept": ".pdf"})
        context = widget.get_context("file", None, {"id": "file_id"})
        self.assertIn("custom-class", context["widget"]["attrs"]["class"])
        self.assertEqual(context["widget"]["attrs"]["accept"], ".pdf")


@override_settings(LANGUAGE_CODE="en")
class TestDroppableFileInputStatic(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.page.goto(self.live_server_url)

    def tearDown(self):
        self.page.close()

    def test_invalid_file_type(self):
        self.page.goto(f"{self.live_server_url}/")
        input_selector = 'input[type="file"]'
        self.page.set_input_files(input_selector, {"name": "file.txt", "mimeType": "text/plain", "buffer": b"content"})

        # Handle the alert dialog
        self.page.on(
            "dialog",
            lambda dialog: assert_and_accept_dialog(
                dialog, "The file type is not allowed. Please select a file of type: image/png."
            ),
        )

        # Trigger the change event to simulate file upload
        self.page.evaluate("document.querySelector('input[type=\"file\"]').dispatchEvent(new Event('change'))")

    def test_file_size_limit(self):
        self.page.goto(f"{self.live_server_url}/")
        input_selector = 'input[type="file"]'
        self.page.set_input_files(input_selector, {"name": "file.png", "mimeType": "image/png", "buffer": b"a" * 1025})

        # Handle the alert dialog
        self.page.on(
            "dialog",
            lambda dialog: assert_and_accept_dialog(
                dialog, "The file is too large. Please select a file that is 1K or smaller."
            ),
        )

        # Trigger the change event to simulate file upload
        self.page.evaluate("document.querySelector('input[type=\"file\"]').dispatchEvent(new Event('change'))")
