import csv
from importlib.resources import files
from yunpy import sources, example_input


def get_database_path():
    """
    Gets the path to the included PHONO-ML database's characters table.

    :return: Path to phonoML_characters.csv file
    :rtype: str
    """
    return files(sources).joinpath("phonoML_characters.csv")


def get_example_input_file_path():
    """
    Gets the path to the included example file.

    :return: Path to example.txt file
    :rtype: str
    """
    return files(example_input).joinpath("example.txt")


def about_database():
    """
    Builds an informational message about PHONO-ML database.

    :return: Informational message about PHONO-ML database with download links
    :rtype: str
    """
    database_path = get_database_path()
    with open(database_path, "r", encoding="utf-8") as db:
        reader = csv.DictReader(db)
        single_reading = len([line["Character"] for line in reader if ";" not in line["Transcriptions"]])
        db.seek(0)
        multiple_readings = len([line["Character"] for line in reader if ";" in line["Transcriptions"]])
        message = f"\nABOUT PHONO-ML DATABASE:\n{'-'*20}\n" \
                  f"PHONO-ML database covers {single_reading + multiple_readings} characters " \
                  f"and their Middle Chinese transcription(s).\n" \
                  f"{single_reading} characters have only one known transcription.\n" \
                  f"{multiple_readings} characters have multiple transcriptions.\n" \
                  f"{'-'*20}\nPHONO-ML database is available on:\n" \
                  f"* Zenodo = (URL)\n" \
                  f"* Gitlab = https://gitlab.huma-num.fr/phono-ml/database\n{'-'*20}\n" \
                  f"Licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).\n" \
                  f"Created by Guillaume JACQUES and Alexander DELAPORTE\n" \
                  f"CRLAO - CNRS UMR 8563\n"
    return message


def get_readings_from_character(char: str) -> list[str]:
    """
    Gets all known phonetic transcriptions for a character.

    :param char: Character which transcriptions will be fetched from the database
    :type char: str

    :return: List of all its known phonetic transcriptions
    :rtype: list
    """
    database_path = get_database_path()
    with database_path.open("r", encoding="utf-8") as db:
        reader = csv.DictReader(db)
        try:
            readings = [line["Transcriptions"].split(";") for line in reader if line["Character"] == char][0]
        except IndexError:
            readings = []
    return readings


def get_fanqie_from_character(char: str) -> list[str]:
    """
    Gets all known fanqie for a character.

    :param char: Character which fanqie will be fetched from the database
    :type char: str

    :return: List of all its known fanqie
    :rtype: list
    """
    database_path = get_database_path()
    with database_path.open("r", encoding="utf-8") as db:
        reader = csv.DictReader(db)
        try:
            fanqie = [line["Fanqie"].split(";") for line in reader if line["Character"] == char][0]
        except IndexError:
            fanqie = []
    return fanqie


def get_sixtuples_from_character(char: str) -> list[str]:
    """
    Gets all known sixtuples for a character.

    :param char: Character which sixtuples will be fetched from the database
    :type char: str

    :return: List of all its known sixtuples
    :rtype: list
    """
    database_path = get_database_path()
    with database_path.open("r", encoding="utf-8") as db:
        reader = csv.DictReader(db)
        try:
            sixtuples = [line["Sixtuples"].split(";") for line in reader if line["Character"] == char][0]
        except IndexError:
            sixtuples = []
    return sixtuples


def db_coverage() -> list[str]:
    """
    Builds a list of all characters currently registered in the database.

    :return: Full list of registered characters
    :rtype: list
    """
    database_path = get_database_path()
    with database_path.open("r", encoding="utf-8") as db:
        reader = csv.DictReader(db)
        characters = [line["Character"] for line in reader]
        return characters


def get_lines_from_text(path_to_text=str(get_example_input_file_path())) -> list[str]:
    """
    Segments plain text from a file into a list of lines.

    :param path_to_text: Path to a raw text file (default = path to example.txt file)
    :type path_to_text: str

    :return: List of text lines
    :rtype: list
    """
    with open(path_to_text, "r", encoding="utf-8") as f:
        return f.readlines()


def clean_lines(lines: list) -> list[str]:
    """
    Removes leading and trailing whitespaces for each item of a list of text strings.

    :param lines: List of text lines (result of get_lines_from_text() function)
    :type lines: list

    :return: List of stripped lines of text
    :rtype: list
    """
    cleans = [line.strip() for line in lines]
    return cleans


def get_sentences_from_text(txt_path: str) -> list[str]:
    """
    Segments plain text from a file into a list of stripped lines.

    :param txt_path: Path to a raw text file
    :type txt_path: str

    :return: List of text lines
    :rtype: list
    """
    lines = get_lines_from_text(txt_path)
    return clean_lines(lines)
