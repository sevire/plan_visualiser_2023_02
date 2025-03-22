import json
from plan_visual_django.models import HelpText

import logging
logger = logging.getLogger(__name__)


def add_help_text_service(slug: str, title:str, content: str, overwrite: bool = False):
    """
    Adds or updates a HelpText record in the database.

    Help text can be configured for any page and the name of the slug for each page is defined in the
    appropriate view.

    Adds or updates a HelpText record in the database.

    Help text can be configured for any page. The name of the slug for each page
    is defined in the appropriate view.

    If a record with the given slug already exists, the record will be updated if
    the `overwrite` flag is set to True. Otherwise, a new record is created. If
    the `overwrite` flag is False and the slug already exists, an exception is
    raised.

    :param slug: The unique identifier for the HelpText record.
    :type slug: str

    :param title: The title of the HelpText record.
    :type title: str

    :param content: The content/body of the HelpText record.
    :type content: str

    :param overwrite: A flag to indicate whether to overwrite an existing record.
    Default is False.
    :type overwrite: bool

    :return: None
    """
    # Check if a HelpText record with this slug exists
    help_text = HelpText.objects.filter(slug=slug).first()

    if help_text:
        if overwrite:
            # Overwrite the record
            help_text.title = title
            help_text.content = content
            help_text.save()
            print(f"Successfully overwrote HelpText with slug '{slug}'.")
        else:
            raise ValueError(
                f"A HelpText record with slug '{slug}' already exists. Use '--overwrite' to update it."
            )
    else:
        # Create a new record if the slug does not exist
        HelpText.objects.create(slug=slug, title=title, content=content)
        print(f"Successfully added HelpText '{title}' with slug '{slug}'.")

def populate_help_text_fields(fixture_file: str):
    # Load the JSON data from the fixture file
    with open(fixture_file, "r") as file:
        help_text_data = json.load(file)

    # Iterate through the help text records
    for record in help_text_data:
        fields = record.get("fields")
        # Extract fields from the JSON record
        slug = fields.get("slug")
        title = fields.get("title")
        content = fields.get("content")

        if not slug or not title or not content:
            logger.error("Invalid help text record: Missing required fields")
            continue

        # Call the existing `add_helptext` command
        add_help_text_service(
            slug=slug,
            title=title,
            content=content,
            overwrite=True,  # Always update to latest version from fixture.
        )
        logger.info(f"Successfully added HelpText: {slug}")
