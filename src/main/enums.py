from enum import Enum

class Language(Enum):
    ENGLISH = "en", "English"
    RUSSIAN = "ru", "Russian"
    UZBEK = "uz", "Uzbek"

    @classmethod
    def choices(cls):
        return [item.value for item in cls]

    @classmethod
    def labels(cls):
        return [item.label for item in cls]