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


class DocumentType(Enum):
    PDF = "pdf", "PDF fayl"
    TXT = "txt", "TXT fayl"

    @classmethod
    def choices(cls):
        return [item.value for item in cls]

    @classmethod
    def labels(cls):
        return [item.label for item in cls]


class DocumentStatus(Enum):
    PENDING = "pending", "Kutilmoqda"
    PROCESSING = "processing", "Qayta ishlanmoqda"
    PROCESSED = "processed", "Qayta ishlangan"
    ERROR = "error", "Xatolik"

    @classmethod
    def choices(cls):
        return [item.value for item in cls]

    @classmethod
    def labels(cls):
        return [item.label for item in cls]