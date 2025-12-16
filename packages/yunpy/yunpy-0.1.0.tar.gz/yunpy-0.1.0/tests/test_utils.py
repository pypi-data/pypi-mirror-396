import pytest
from yunpy.utils import *


def test_about_database():
    """
    Tests the `about_database()` function.

    :return: None
    """
    message = about_database()
    message_lines = message.split("\n")
    assert len(message_lines) == 15
    assert message_lines[1] == "ABOUT PHONO-ML DATABASE:"
    assert message_lines[-2] == "CRLAO - CNRS UMR 8563"


def test_get_readings_from_character():
    """
    Tests the `get_readings_from_character()` function for a character with multiple transcriptions.

    :return: None
    """
    readings = get_readings_from_character("䍶")
    assert type(readings) == list
    assert "tuwng" in readings
    assert "drin" in readings
    assert "tuwngH" in readings
    assert len(readings) == 3


def test_get_fanqie_from_character():
    """
    Tests the `get_fanqie_from_character()` function for a character with one fanqie.

    :return: None
    """
    fanqie = get_fanqie_from_character("範")
    assert type(fanqie) == list
    assert "防錽" in fanqie
    assert len(fanqie) == 1


def test_get_sixtuples_from_character():
    """
    Tests the `get_sixtuples_from_character()` function for a character with multiple sixtuples.

    :return: None
    """
    sixtuples = get_sixtuples_from_character("㺖")
    assert type(sixtuples) == list
    assert "咸開二上銜曉" in sixtuples
    assert "咸開一去談匣" in sixtuples
    assert "咸開二去銜初" in sixtuples
    assert len(sixtuples) == 3


def test_db_coverage():
    """
    Tests the `db_coverage()` function.

    :return: None
    """
    coverage = db_coverage()
    assert type(coverage) == list
    assert len(coverage) == 20276
    assert "東" in coverage
    assert "藃" in coverage
    assert "渜" in coverage
    assert "籑" in coverage
    assert "套" in coverage


def test_get_lines_from_text():
    """
    Tests the `get_lines_from_text()` function on the example.txt file.

    :return: None
    """
    lines = get_lines_from_text()
    assert len(lines) == 10
    assert type(lines) == list
    assert "窈窕淑女，君子好逑。\n" in lines
    assert lines[0].strip() == "關關雎鳩，在河之洲；"
    assert lines[-1].strip() == "窈窕淑女，鍾鼓樂之。"


def test_clean_lines():
    """
    Tests the `clean_lines()` function on a short list of strings.

    :return: None
    """
    readlines = [
        "葛之覃兮，施于中谷；維葉萋萋。\n",
        "黃鳥于飛，集于灌木；其鳴喈喈。\n",
        "葛之覃兮，施于中谷；維葉莫莫。\n",
        "是刈是濩，為絺為綌，服之無斁。\n",
        "言告師氏，言告言歸。\n",
    ]
    contents = clean_lines(readlines)
    assert type(contents) == list
    assert len(contents) == 5
    assert "葛之覃兮，施于中谷；維葉萋萋。" in contents
