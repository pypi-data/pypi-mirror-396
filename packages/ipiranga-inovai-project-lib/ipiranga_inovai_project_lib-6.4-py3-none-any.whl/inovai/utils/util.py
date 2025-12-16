import logging
from datetime import datetime


def format_date(date_str, date_str_format: str = '%d/%m/%Y', new_format: str = None) -> str:

    try:
        if "T" in date_str and "Z" in date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        elif " " in date_str and ":" in date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        else:
            date_obj = datetime.strptime(date_str, date_str_format)

        if new_format:
            return date_obj.strftime(new_format)

        return date_obj.strftime(date_str_format)
    except ValueError as ve:
        logging.error(f"Formato de data inválido. Data '{date_str}', formato esperado: '{date_str_format}'. Erro: {ve}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado ao formatar a data '{date_str}': {e}")
        raise