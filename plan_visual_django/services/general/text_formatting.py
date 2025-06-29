import textwrap


def prettify_key(key: str) -> str:
    """Convert underscore-separated key to space-separated capitalized form."""
    return ' '.join(word.capitalize() for word in key.split('_'))


def print_formatted_dict_list(dict_list: list[dict]) -> None:
    """Print a list of dictionaries in a formatted column layout with prettified headers."""
    if not dict_list:
        return

    # Use first dictionary to establish field order
    first_dict = dict_list[0]
    field_order = list(first_dict.keys())

    # Calculate maximum lengths for values in each field
    max_lengths = {}
    for field in field_order:
        max_lengths[field] = max(len(str(d[field])) for d in dict_list) + 2  # Add space for comma and space

    # Print each dictionary's data
    for dictionary in dict_list:
        line_parts = []
        for i, field in enumerate(field_order):
            pretty_key = prettify_key(field)
            value = str(dictionary[field])
            comma = ", " if i < len(field_order) - 1 else ""
            padded_value = (value + comma).ljust(max_lengths[field])
            line_parts.append(f"{pretty_key}: {padded_value}")

        # Join all parts without additional separators
        print("".join(line_parts))


def print_banner(text: str, width: int = 80, border_char: str = "=") -> None:
    """Print text in a banner with specified width and border character.

    Args:
        text: The text to display in the banner
        width: The total width of the banner (default: 80)
        border_char: The character to use for the banner border (default: '=')
    """
    # Calculate the content width (total width minus borders and padding)
    content_width = width - 8  # 3 chars on each side plus two spaces

    # Wrap the text to fit within the content width
    wrapped_lines = textwrap.wrap(text, width=content_width)

    # Create the banner
    print(border_char * width)
    print(border_char * width)
    print(f"{border_char * 3}{' ' * (width - 6)}{border_char * 3}")

    for line in wrapped_lines:
        padding = content_width - len(line)
        print(f"{border_char * 3} {line}{' ' * padding} {border_char * 3}")

    print(f"{border_char * 3}{' ' * (width - 6)}{border_char * 3}")
    print(border_char * width)
    print(border_char * width)
