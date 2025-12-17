"""
Contains constant values.
"""

EXTENSIONS_APP_NAME = "uni_bot"
CONTAINER_BLOCK_TYPES = {
    "course",
    "chapter",
    "sequential",
    "vertical",
    "library_content",
}
PUBLISHABLE_COURSE_STRUCTURE_BLOCK_TYPES = {"chapter", "sequential", "vertical"}
UUID_PATTERN = (
    r"(?P<uuid>({hex}{{8}}-{hex}{{4}}-{hex}{{4}}-{hex}{{4}}-{hex}{{12}}))".format(
        hex="[0-9a-f]"
    )
)
REQUEST_METHOD_CHOICES = [
    ("GET", "GET"),
    ("POST", "POST"),
]
