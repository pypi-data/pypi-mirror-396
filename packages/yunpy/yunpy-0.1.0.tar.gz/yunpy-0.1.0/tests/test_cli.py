import pytest
import subprocess
from importlib.resources import files
from yunpy import example_input
from pathlib import Path


def test_show_database_stats():
    """
    Tests function `show_database_stats()`.

    :return: None
    """
    result = subprocess.run(
        ["database"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    assert result.returncode == 0
    message_snippets = [
        "ABOUT PHONO-ML",
        "one known transcription",
        "multiple transcriptions",
        "Creative Commons Attribution 4.0 International License",
        "CRLAO - CNRS UMR 8563"]
    for snippet in message_snippets:
        assert snippet in result.stdout


def test_show_character_readings():
    """
    Tests function `show_character_readings()`.

    For various reasons this test is currently run only on an ASCII character which is not registered in the databse.

    :return: None
    """
    result = subprocess.run(
        ["howtoread", "a"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    assert result.returncode == 0
    assert result.stdout == "No reading available for this character: a\n"


def test_show_character_info():
    """
    Tests function `show_character_info()`.

    For various reasons this test is currently run only on an ASCII character which is not registered in the database.

    :return: None
    """
    result = subprocess.run(
        ["charinfo", "a"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    assert result.returncode == 0
    assert result.stdout == "The character 'a' was not found in the database.\n"


def test_export_webanno_file():
    """
    Tests function `convert_to_webanno()` on the example file.

    This function only tests the CLI response, as the actual data/file processing is tested in test_core.py.

    :return: None
    """
    result = subprocess.run(
        args=["webanno", "--file", "example"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    assert result.returncode == 0
    message_snippets = [
        "Converting example raw text file into Webanno TSV 3.3 format",
        "Webanno file successfully saved at ",
        ".tsv"]
    for snippet in message_snippets:
        assert snippet in result.stdout


def test_export_webanno_file_not_found():
    """
    Tests function `convert_to_webanno()` on an incorrect path (file mode).

    This function only tests the CLI response, as the actual data/file processing is tested in test_core.py.

    :return: None
    """
    result = subprocess.run(
        args=["webanno", "--file", "path_that_does_not_exist_to/file_that_does_not_exist.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    assert result.returncode == 0
    assert result.stdout == "Converting file (path_that_does_not_exist_to/file_that_does_not_exist.txt) into Webanno " \
                            "TSV 3.3 format...\nFile not found at path " \
                            "'path_that_does_not_exist_to/file_that_does_not_exist.txt', please check path again.\n"


def test_export_xml_file():
    """
    Tests function `convert_to_xml() on the example file.

    This function only tests the CLI response, as the actual data/file processing is tested in test_core.py.

    :return: None
    """
    result = subprocess.run(
        args=["yunpyxml", "--file", "example"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    assert result.returncode == 0
    message_snippets = [
        "Converting example raw text file into XML format",
        "XML file successfully saved at ",
        ".xml"]
    for snippet in message_snippets:
        assert snippet in result.stdout


def test_export_xml_file_not_found():
    """
    Tests function `convert_to_xml()` on an incorrect path (file mode).

    This function only tests the CLI response, as the actual data/file processing is tested in test_core.py

    :return: None
    """
    result = subprocess.run(
        args=["yunpyxml", "--file", "path_that_does_not_exist_to/file_that_does_not_exist.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    assert result.returncode == 0
    assert result.stdout == "Converting file (path_that_does_not_exist_to/file_that_does_not_exist.txt) into XML " \
                            "format...\nFile not found at path " \
                            "'path_that_does_not_exist_to/file_that_does_not_exist.txt', please check path again.\n"


def test_export_webanno_directory():
    """
    Tests function `convert_to_webanno()` on the example input directory.

    This function only tests the CLI response, as the actual data/file processing is tested in test_core.py

    :return: None
    """
    input_dir = files(example_input).joinpath("Shijing-demo")
    expected_outdir = (Path("webanno_output") / f"{input_dir.name}_webanno").resolve()
    result = subprocess.run(
        args=["webanno", "-d", input_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    assert result.returncode == 0
    assert f"Converting all text files in directory ({input_dir}) into Webanno TSV 3.3 format..." in result.stdout
    assert "successfully saved at " in result.stdout
    assert f"{expected_outdir}" in result.stdout


def test_export_webanno_directory_not_found():
    """
    Tests function `convert_to_webanno()` on an incorrect path (directory mode).

    This function only tests the CLI response, as the actual data/file processing is tested in test_core.py.

    :return: None
    """
    result = subprocess.run(
        args=["webanno", "-d", "path_that_does_not_exist_dir"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    assert result.returncode == 0
    assert (result.stdout == "Converting all text files in directory (path_that_does_not_exist_dir) into Webanno TSV 3.3 format...\n"
                             "No .txt files found in directory 'path_that_does_not_exist_dir', please check path again.\n")


def test_export_xml_directory():
    """
    Tests function `convert_to_xml()` on the example input directory.

    This function only tests the CLI response, as the actual data/file processing is tested in test_core.py

    :return: None
    """
    input_dir = files(example_input).joinpath("Shijing-demo")
    expected_outdir = (Path("xml_output") / f"{input_dir.name}_xml").resolve()
    result = subprocess.run(
        args=["yunpyxml", "-d", input_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    assert result.returncode == 0
    assert f"Converting all text files in directory ({input_dir}) into XML..." in result.stdout
    assert "successfully saved at " in result.stdout
    assert f"{expected_outdir}" in result.stdout


def test_export_xml_directory_not_found():
    """
    Tests function `convert_to_xml()` on an incorrect path.

    This function only tests the CLI response, as the actual data/file processing is tested in test_core.py.

    :return: None
    """
    result = subprocess.run(
        args=["yunpyxml", "-d", "path_that_does_not_exist_dir"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    assert result.returncode == 0
    assert result.stdout == ("Converting all text files in directory (path_that_does_not_exist_dir) into XML...\n"
                             "No .txt files found in directory 'path_that_does_not_exist_dir', please check path again.\n")
