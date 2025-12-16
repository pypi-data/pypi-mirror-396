from typing import List


class FileRequestDto:
    file_name: str
    hash_file: str

    def __init__(self, file_name, hash_file, **data):
        super().__init__(**data)
        self.file_name = file_name
        self.hash_file = hash_file

    def to_dict(self):
        return {
            "nome": self.file_name,
            "bytesBase64": self.hash_file,
        }


class FullSendRequestDto:
    employer_number: str
    process_codes: str
    start_date: str
    end_date: str
    internal_code: str
    files: List[FileRequestDto]

    def __init__(self, employer_number, process_codes, start_date, end_date, internal_code, **data):
        super().__init__(**data)
        self.employer_number = employer_number
        self.process_codes = process_codes
        self.start_date = start_date
        self.end_date = end_date
        self.internal_code = internal_code
        self.files = []

    def to_dict(self):
        return {
            "cnpjEmpresa": self.employer_number,
            "codProcessamentos": self.process_codes,
            "dataIni": self.start_date,
            "dataFim": self.end_date,
            "codInterno": self.internal_code,
            "arquivos": [file.to_dict() for file in self.files],
        }

    def __str__(self):
        return str({
            "cnpjEmpresa": self.employer_number,
            "codProcessamentos": self.process_codes,
            "dataIni": self.start_date,
            "dataFim": self.end_date,
            "codInterno": self.internal_code,
        })


