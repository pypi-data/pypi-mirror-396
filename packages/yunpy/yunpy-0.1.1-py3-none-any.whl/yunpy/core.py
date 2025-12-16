from yunpy.character import Character
from yunpy.utils import *
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import indent
import string

WEBANNO_PREFIX = (
"#FORMAT=WebAnno TSV 3.3\n"
"#T_SP=webanno.custom.Transcription|value\n"
"#T_SP=webanno.custom.Transcriptions|values\n"
"#T_SP=webanno.custom.Fanqie|value\n"
"#T_SP=webanno.custom.Sixtuples|value\n"
"\n\n"
)


def build_webanno(sentences) -> list[str]:
    """
    Builds Webanno TSV 3.3 formated data from a list of strings.

    :param sentences: List of strings returned from utils function get_sentences_from_text().
    :type sentences: list

    :return: List of Webanno TSV 3.3 data lines.
    :rtype: list
    """
    punctuation_list = ["；", "。", "，", ";", ".", ","]
    lines = []
    offset = 0

    for sentence in sentences:
        lines.append(f"#Text={sentence}")

    for sentence_id, sentence in enumerate(sentences, start=1):
        for token_id, token in enumerate(sentence, start=1):
            begin = offset
            offset += 1
            end = offset
            char = Character(token)

            if char.base_character in punctuation_list or char.base_character in string.punctuation:
                escaped_char = "\\" + char.base_character
                reading = "p"
                multiple_readings = "_"
            else:
                escaped_char = char.base_character

                if not char.transcriptions:
                    reading = "_"
                    multiple_readings = "_"
                elif len(char.transcriptions) == 1:
                    reading = char.transcriptions[0]
                    multiple_readings = "_"
                else:
                    reading = "*"
                    multiple_readings = "|".join(char.transcriptions)

            fanqie = "|".join(char.fanqie) if char.fanqie else "_"
            sixtuples = "|".join(char.sixtuple) if char.sixtuple else "_"

            line = (
                f"{sentence_id}-{token_id}\t{begin}-{end}\t{escaped_char}\t{reading}\t{multiple_readings}\t{fanqie}\t{sixtuples}"
            )
            lines.append(line)

        offset += 1
    return lines


def export_webanno_constituents(input_file: str, output_path="webanno_output") -> str:
    """
    Creates an annotated Webanno TSV 3.3 file from a raw text file.

    :param input_file: Path of the raw text input file.
    :type input_file: str

    :param output_path: Path of the output directory.
    :type output_path: str

    :return: Short message indicating the path of the output file.
    :rtype: str
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / (Path(input_file).stem + ".tsv")

    contents = get_sentences_from_text(input_file)
    tsv_body = "\n".join(build_webanno(contents))

    with open(output_file, mode="w", encoding="utf-8", newline="") as f:
        f.write(WEBANNO_PREFIX)
        f.writelines(tsv_body)

    return f"Webanno file successfully saved at {output_file.resolve()}"


def build_xml(sentences):
    """
    Builds XML formated data from a list of strings.

    :param sentences: List of strings returned from utils function get_sentences_from_text().
    :type sentences: list

    :return: ElementTree object (root element of the XML structure).
    :rtype: ET.Element
    """
    root = ET.Element("ANNOTATED_TEXT")

    for sentence in sentences:
        line = ET.SubElement(root, "line")

        for ch in sentence:
            token_el = ET.SubElement(line, "token")
            character_el = ET.SubElement(token_el, "character")
            character_el.text = ch

            char_object = Character(ch)

            if not char_object.transcriptions:
                continue
            elif len(char_object.transcriptions) == 1:
                transcription_el = ET.SubElement(token_el, "transcription")
                transcription_el.text = char_object.transcriptions[0]
            else:
                transcriptions_el = ET.SubElement(token_el, "transcriptions")
                for tran in char_object.transcriptions:
                    tran_el = ET.SubElement(transcriptions_el, "transcription")
                    tran_el.text = tran

    return root


def export_xml(input_file: str, output_path="xml_output") -> str:
    """
    Creates an annotated XML file from a raw text file.

    :param input_file: Path of the raw text input file.
    :type input_file: str

    :param output_path: Path of the output directory.
    :type output_path: str

    :return: Short message indicating the path of the output file.
    :rtype: str
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / (Path(input_file).stem + ".xml")

    sentences = get_sentences_from_text(input_file)
    root = build_xml(sentences)
    indent(root, space=' ', level=0)

    xml_output = ET.tostring(root, encoding="utf-8", method="xml", xml_declaration=True).decode("utf-8")
    with open(output_file, mode="w", encoding="utf-8") as f:
        f.write(xml_output)

    return f"XML file successfully saved at {output_file.resolve()}"


def process_dir(input_dir, mode):
    """
    Processes all raw text (.txt) files from a directory into Webanno TSV 3.3 or XML annotated files.

    :param input_dir: Path of the input directory.
    :type input_dir: Path

    :param mode: Annotation mode, "webanno" for Webanno TSV 3.3 or "XML" for Yunpy XML.
    :type mode: str

    :return: Short message indicating how many files have been processed and their output directory's path.
    """
    input_path = Path(input_dir)
    dir_name = input_path.name
    count = 0

    input_txt = list(input_path.rglob("*.txt"))
    if len(input_txt) == 0:
        raise FileNotFoundError

    if mode == "xml":
        output_path = Path("xml_output")/f"{dir_name}_xml"
    elif mode == "webanno":
        output_path = Path("webanno_output")/f"{dir_name}_webanno"
    else:
        print(f"Mode missing : {mode}")
        return
    output_path.mkdir(parents=True, exist_ok=True)

    for p in input_txt:
        file_stem = p.stem
        suffix = ".xml" if mode == "xml" else ".tsv"
        if mode == "xml":
            export_xml(str(p), output_path=str(output_path))
        else:
            export_webanno_constituents(str(p), output_path=str(output_path))
        count += 1
        print(f"{file_stem}{suffix} in {output_path}")

    return f"{count} file{'s' if count > 1 else ''} successfully saved at {output_path.resolve()}"
