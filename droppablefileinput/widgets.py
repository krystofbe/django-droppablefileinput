from django.forms.widgets import ClearableFileInput
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class DroppableFileInput(ClearableFileInput):
    template_name = "widgets/droppable_file_input.html"

    def __init__(
        self,
        attrs=None,
        label="Click here or drag and drop a file",
        instructions="",
        auto_submit=False,
        max_file_size=None,
        allowed_types=None,
        icon_url=None,
        icon_width=None,
        icon_height=None,
        max_size_error_message=None,
        invalid_file_type_error_message=None,
    ):
        super().__init__(attrs)
        self.label = label
        self.auto_submit = auto_submit
        self.max_file_size = max_file_size
        self.allowed_types = allowed_types
        self.instructions = instructions
        if max_size_error_message is None:
            max_size_error_message = _("The file is too large. The maximum file size is %(max_file_size)s.") % {
                "max_file_size": max_file_size
            }
        self.max_size_error_message = max_size_error_message

        if invalid_file_type_error_message is None:
            invalid_file_type_error_message = _("Invalid file type. Only %(allowed_types)s files are allowed.") % {
                "allowed_types": allowed_types
            }
        self.invalid_file_type_error_message = invalid_file_type_error_message

        # defaults for the icon
        if icon_url is None:
            icon_url = static("droppablefileinput/images/icon.svg")
        self.icon_url = icon_url
        if icon_width is None:
            icon_width = 32
        self.icon_width = icon_width
        if icon_height is None:
            icon_height = 32
        self.icon_height = icon_height

    class Media:
        css = {
            "all": [
                "droppablefileinput/css/droppable_file_input.css",
            ]
        }
        js = ("droppablefileinput/js/droppable_file_input.js",)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"].update({
            "label": self.label,
            "auto_submit": self.auto_submit,
            "max_file_size": self.max_file_size,
            "allowed_types": self.allowed_types,
            "icon_url": self.icon_url,
            "icon_width": self.icon_width,
            "icon_height": self.icon_height,
            "instructions": self.instructions,
            "max_size_error_message": self.max_size_error_message,
            "invalid_file_type_error_message": self.invalid_file_type_error_message,
        })
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return mark_safe(renderer.render(self.template_name, context))
