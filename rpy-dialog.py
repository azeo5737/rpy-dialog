from argparse import ArgumentParser
from glob import glob
import json
import re

# Labels and control flow commands are intentionally left intact
COMMANDS_TO_REMOVE = (
    "$", "centered", "xalign", "yalign", "xoffset", "yoffset",
    "scene", "with", "play", "pause", "stop", "queue", "show", "hide",
    "transform", "linear", "on", "easein", "easeout", "image", "window",
    "init", "screen", "python"
)

parser = ArgumentParser(prog='rpy-dialog.py',
                        description='Extract dialog from RPY scripts.')
parser.add_argument('directory', type=str, help='Root directory of extracted RPA.')
parser.add_argument('--narrator', type=str, default="NARRATOR", help='Name of the narrating character, used for dialog without a specified speaker. (Defaults to NARRATOR)')
parser.add_argument('--output', type=str, default='dialog.json', help='Output filename. (Defaults to dialog.json)')
args = parser.parse_args()


def read_rpy_lines(directory: str) -> list:
    """Read every RPY file in a directory line-by-line,
    removing unnecessary commands while doing so.

    Args:
        directory (str): Directory of rpy files to read.

    Returns:
        list: Combined list of all rpy script lines.
    """

    files = glob(f'{directory}/*.rpy')
    filter_lambda = lambda x: not x.isspace() and not x.strip().startswith(COMMANDS_TO_REMOVE)
    processed_lines = []
    for path in files:
        with open(path, 'r') as f:
            lines = f.readlines()
            processed_lines += filter(filter_lambda, lines) # Remove irrelevant lines
    return processed_lines


def parse_characters(lines: list) -> dict:
    """Parse character definitions into a dictionary to convert ids to names.

    Args:
        lines (list): Lines of rpy script

    Returns:
        dict: Dictionary that maps character ids to names.
    """

    definitions = filter(lambda x: x.startswith('define'), lines)
    parsed_definitions = {}
    for d in definitions:
        # Group 1 is the character key, group 2 is their actual name
        result = re.search(r"define\s*(\w+)\s*\=\s*Character\s*\(\s*'([^']+)", d)
        if not result:
            continue
        parsed_definitions[result.group(1)] = result.group(2)
    return parsed_definitions


def extract_labels(lines: list) -> dict:
    """Store labels and lines under them in a dictionary.

    Args:
        lines (list): Lines of rpy script

    Returns:
        dict: Dictionary that maps label names to lists of corresponding lines
    """

    in_label = None
    label_dict = {}
    for line in lines:
        # Check if this line is the start of a block
        # Group 1 is the type of block, group 2 is the name
        block_match = re.match(r"(\w+)[\ \t]*([^:\n\r]+)?:", line)

        if block_match:
            block_type = block_match.group(1)
            if block_type == 'label':
                in_label = block_match.group(2)
            continue

        if in_label:
            if not label_dict.get(in_label):
                label_dict[in_label] = [line]
            else:
                label_dict[in_label].append(line)

    return label_dict


def parse_dialog(labels: dict, characters: dict) -> list:
    """Parse dialog from the given labels with the specified set of characters

    Args:
        labels (dict): Dictionary of label names to line lists
        characters (dict): Dictionary of character ids to names

    Returns:
        list: List of messages.
    """

    messages = []
    for (label, lines) in labels.items():
        for line in lines:
            # TODO: Try to parse dialog inside of blocks
            if line.startswith(('\t', '    ')):
                continue

            line = line.strip()
            result = re.match(r"(?:(\w+)\s+)?\"([^\"]*)\"", line)
            if not result:
                continue
            
            # Format the dialog into a message object
            if not result.group(1):
                # No speaker specified, use narrator character and put message in asterisks
                character = args.narrator
                utterance = f'*{result.group(2)}*'
            else:
                character = characters[result.group(1)]
                utterance = result.group(2)
            messages.append({'speaker': character, 'utterance': utterance})
    
    return messages


rpy_lines = read_rpy_lines(args.directory)
rpy_characters = parse_characters(rpy_lines)
rpy_labels = extract_labels(rpy_lines)
rpy_messages = parse_dialog(rpy_labels, rpy_characters)

print(f"Parsing finished:")
print(f"    {len(rpy_characters)} characters.")
print(f"    {len(rpy_labels)} labels.")
print(f"    {len(rpy_messages)} messages.")

dialog_characters = {}
for name in rpy_characters.values():
    dialog_characters[name] = ''

with open(args.output, 'w') as f:
    json.dump({
        "characters": dialog_characters,
        "messages": rpy_messages
        }, f, sort_keys=True)
print(f'Successfully wrote to {args.output}.')