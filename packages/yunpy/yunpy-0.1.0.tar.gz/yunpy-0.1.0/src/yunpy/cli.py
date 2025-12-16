import argparse
from tokenize import group

from yunpy.character import Character
from yunpy.utils import about_database, get_example_input_file_path
from yunpy.core import export_webanno_constituents
from yunpy.core import export_xml
from yunpy.core import process_dir


def show_database_stats():
    """
    Displays an informational message about PHONO-ML database.
    """
    db_stats = about_database()
    print(db_stats)


def show_character_readings():
    """
    Displays all known phonetic transcriptions for any given character.
    """
    parser = argparse.ArgumentParser(description="Show all known phonetic transcriptions for a character")
    parser.add_argument(
        "char",
        help="A single character or a string of characters to retrieve phonetic transcriptions for. "
             "For a single character, all transcriptions for that character will be shown. "
             "For a string, transcriptions for each character will be displayed individually."
    )
    args = parser.parse_args()
    if len(args.char) > 1:
        for token in args.char:
            readings = Character(token).set_character_readings_message()
            print(readings)
    else:
        readings = Character(args.char).set_character_readings_message()
        print(readings)


def show_character_info():
    """
    Displays all known data about a character, formatted into a short message.
    """
    parser = argparse.ArgumentParser(description="Show all known data about a character")
    parser.add_argument(
        "char",
        help="A single character or a string of characters to retrieve information about. "
             "For a single character, only that character's data is shown. "
             "For a string, data about each character will be shown individually."
    )
    args = parser.parse_args()
    if len(args.char) > 1:
        for token in args.char:
            info = Character(token).set_message()
            print(info)
    else:
        info = Character(args.char).set_message()
        print(info)


def convert_to_webanno():
    """
    Converts raw text (.txt) file(s) into Webanno TSV 3.3.
    """
    parser = argparse.ArgumentParser(description="Convert plain text files to Webanno TSV 3.3 format.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file", "-f",
        help="Path to the raw text file to be converted into Webanno TSV 3.3. Use 'example' to convert a sample file."
    )
    group.add_argument(
        "--directory", "-d",
        help="Path to the directory containing .txt files to be converted into Webanno TSV 3.3. All .txt files in the "
             "directory will be processed."
    )
    args = parser.parse_args()
    try:
        if args.file:
            if args.file.lower() == "example":
                print("Converting example raw text file into Webanno TSV 3.3 format...")
                file = export_webanno_constituents(str(get_example_input_file_path()))
            else:
                print(f"Converting file ({args.file}) into Webanno TSV 3.3 format...")
                file = export_webanno_constituents(args.file)

        elif args.directory:
            print(f"Converting all text files in directory ({args.directory}) into Webanno TSV 3.3 format...")
            file = process_dir(args.directory, mode="webanno")
        print(file)
    except FileNotFoundError:
        if args.file:
            print(f"File not found at path '{args.file}', please check path again.")
        else:
            print(f"No .txt files found in directory '{args.directory}', please check path again.")


def convert_to_xml():
    """
    Converts raw text (.txt) file(s) into Yunpy XML.
    """
    parser = argparse.ArgumentParser(description="Convert plain text files to XML format.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file", "-f",
        help="Path to the raw text file to be converted into XML. Use 'example' to convert a sample file."
    )
    group.add_argument(
        "--directory", "-d",
        help="Path to the directory containing .txt files to be converted into XML. All .txt files in the directory "
             "will be processed."
    )
    args = parser.parse_args()
    try:
        if args.file:
            if args.file.lower() == "example":
                print("Converting example raw text file into XML format...")
                file = export_xml(str(get_example_input_file_path()))
            else:
                print(f"Converting file ({args.file}) into XML format...")
                file = export_xml(args.file)

        elif args.directory:
            print(f"Converting all text files in directory ({args.directory}) into XML...")
            file = process_dir(args.directory, mode="xml")
        print(file)

    except FileNotFoundError:
        if args.file:
            print(f"File not found at path '{args.file}', please check path again.")
        else:
            print(f"No .txt files found in directory '{args.directory}', please check path again.")
