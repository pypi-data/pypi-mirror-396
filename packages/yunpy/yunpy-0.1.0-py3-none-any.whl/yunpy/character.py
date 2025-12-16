from yunpy.utils import get_readings_from_character, get_fanqie_from_character, get_sixtuples_from_character
from yunpy.utils import db_coverage


class Character:
    """
    Class used to fetch data from the included PHONO-ML database's characters table
    """
    def __init__(self, char):
        """
        Initializes a Character object from any given character

        :param char: The character from which the Character object will be initiated.
        :type char: str
        """
        self.base_character = char
        self.transcriptions = get_readings_from_character(char)
        self.fanqie = get_fanqie_from_character(char)
        self.sixtuple = get_sixtuples_from_character(char)

    def is_in_db(self) -> bool:
        """
        Checks if a character is registered in the database.

        :return: Boolean indicating whether the character is registered or not.
        :rtype: bool
        """
        coverage = db_coverage()
        return self.base_character in coverage

    def set_message(self) -> str:
        """
        Creates a message summarizing known data about a character.

        :return: Short message reviewing available data about a character.
        :rtype: str
        """
        if len(self.fanqie) == 0 and len(self.sixtuple) == 0 and len(self.transcriptions) == 0:
            message = f"The character '{self.base_character}' was not found in the database."
        elif len(self.transcriptions) == 1:
            message = f"Character = {self.base_character}\nFanqie = {self.fanqie}\nSixtuple = {self.sixtuple}\n" \
                      f"Transcription = {self.transcriptions}\n\n"
        else:
            message = f"Character = {self.base_character}\nFanqie = {self.fanqie}\nSixtuples = {self.sixtuple}\n" \
                      f"Transcriptions = {self.transcriptions}\n\n"
        return message

    def set_character_readings_message(self) -> str:
        """
        Creates a message listing known readings for a character.

        :return: Short message listing available phonetic transcriptions for a character.
        :rtype: str
        """
        if len(self.transcriptions) == 0:
            message = f"No reading available for this character: {self.base_character}"
        elif len(self.transcriptions) == 1:
            message = f"Character {self.base_character} has the following reading: {self.transcriptions[0]}"
        else:
            message = f"Character {self.base_character} has the following readings: {', '.join(self.transcriptions)}"
        return message
