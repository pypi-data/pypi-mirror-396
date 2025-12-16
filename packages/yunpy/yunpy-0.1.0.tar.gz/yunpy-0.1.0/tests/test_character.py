import pytest
from yunpy.character import Character


@pytest.mark.parametrize("base_character, in_db", [
    ("a", False),
    ("囝", True),
    ("偭", True),
])
def test_is_in_db_all_cases(base_character, in_db):
    """
    Tests the `is_in_db()` method for different characters.

    :param base_character: Character that is put to test
    :type base_character: str
    :param in_db: Expected result
    :type in_db: bool

    :return: None
    """
    current_character = Character(base_character)
    assert current_character.is_in_db() == in_db


@pytest.mark.parametrize("base_character, howtoread_message", [
    ("a", "No reading available for this character."),
    ("囝", "Character 囝 has the following reading: kjenX"),
    ("偭", "Character 偭 has the following readings: mjienX, mjienH"),
])
def test_set_character_readings_message_all_cases(base_character, howtoread_message):
    """
    Tests the `set_character_readings_message()` method for different characters.

    :param base_character: Character that is put to test
    :type base_character: str
    :param howtoread_message: Expected result
    :type howtoread_message: str

    :return: None
    """
    current_character = Character(base_character)
    assert current_character.set_character_readings_message() == howtoread_message


@pytest.mark.parametrize("base_character, charinfo_message", [
    ("a", "The character 'a' was not found in the database."),
    ("囝", "Character = 囝\nFanqie = ['九輦']\nSixtuple = ['山開三上仙見']\nTranscription = ['kjenX']\n\n"),
    ("偭", "Character = 偭\nFanqie = ['彌兖', '彌箭']\nSixtuples = ['山開三上仙明', '山開三去仙明']\n"
        "Transcriptions = ['mjienX', 'mjienH']\n\n"),
])
def test_set_character_readings_message_all_cases(base_character, charinfo_message):
    """
    Tests the `set_message()` method for different characters.

    :param base_character: Character that is put to test
    :type base_character: str
    :param charinfo_message: Expected result
    :type charinfo_message: str

    :return: None
    """
    current_character = Character(base_character)
    assert current_character.set_message() == charinfo_message
