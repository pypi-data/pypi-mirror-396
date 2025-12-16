import pytest
from yunpy.core import *
from yunpy import example_input
from pathlib import Path


def test_build_webanno():
    """
    Tests the `build_wabanno()` function for a short span of text.

    :return: None
    """
    sentence = ["關關雎鳩，在河之洲；"]
    lines = build_webanno(sentence)
    assert type(lines) == list
    assert len(lines) == 11
    assert lines[0].strip() == "#Text=關關雎鳩，在河之洲；"
    assert lines[1].strip("\n") == "1-1	0-1	關	kwaen	_	古還	山合二平刪見"
    assert lines[2].strip("\n") == "1-2	1-2	關	kwaen	_	古還	山合二平刪見"
    assert lines[3].strip("\n") == "1-3	2-3	雎	tshjo	_	七余	遇開三平魚清"
    assert lines[4].strip("\n") == "1-4	3-4	鳩	kjuw	_	居求	流開三平尤見"
    assert lines[5].strip("\n") == "1-5	4-5	\，	p	_	_	_"
    assert lines[6].strip("\n") == "1-6	5-6	在	*	dzojX|dzojH	昨宰|昨代	蟹開一上咍從|蟹開一去咍從"
    assert lines[7].strip("\n") == "1-7	6-7	河	ha	_	胡歌	果開一平歌匣"
    assert lines[8].strip("\n") == "1-8	7-8	之	tsyi	_	止而	止開三平之章"
    assert lines[9].strip("\n") == "1-9	8-9	洲	tsyuw	_	職流	流開三平尤章"
    assert lines[10].strip("\n") == "1-10	9-10	\；	p	_	_	_"


def test_build_xml():
    """
    Tests the `build_wabanno()` function for a short span of text.

    :return: None
    """
    sentences = ["關關雎鳩，在河之洲；"]
    root = build_xml(sentences)
    assert root.tag == "ANNOTATED_TEXT"
    assert len(root.findall("line")) == 1
    assert len(root.find("line").findall("token")) == 10


def test_process_dir():
    """
    Tests the `process_dir()` function on an example input directory.

    :return: None
    """
    input_dir = files(example_input).joinpath("Shijing-demo")
    assert input_dir.exists()
    expected_count = len(list(input_dir.rglob("*.txt")))
    expected_output = Path("webanno_output/Shijing-demo_webanno").resolve()
    suffix = "s" if expected_count > 1 else ""
    expected_message = f"{expected_count} file{suffix} successfully saved at {expected_output}"
    message = process_dir(input_dir,mode="webanno")
    assert message == expected_message
