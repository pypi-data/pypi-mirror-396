"""Валидатор для HTTP статус-кода."""

from typing import List, Optional

from ..dto import ValidationError
from .base import BaseValidator


class StatusCodeValidator(BaseValidator):
    """Валидатор для проверки HTTP статус-кода."""
    
    def __init__(self, error_key: str | None = None):
        """
        Инициализация валидатора статус-кода.
        
        Args:
            error_key: Ключ ошибки для идентификации конкретного правила
        """
        super().__init__(error_key=error_key)
        self._rule_name = "StatusCodeValidator"
    
    def blacklist(self, codes: List[int]) -> "StatusCodeValidator":
        """Проверка, что статус-код не в черном списке."""
        return self._add_rule("blacklist", codes=codes)
    
    def whitelist(self, codes: List[int]) -> "StatusCodeValidator":
        """Проверка, что статус-код в белом списке."""
        return self._add_rule("whitelist", codes=codes)
    
    def validate(self, status_code: int) -> tuple[bool, Optional[ValidationError]]:
        """
        Выполняет валидацию статус-кода.
        
        Args:
            status_code: HTTP статус-код для валидации
            
        Returns:
            Tuple[bool, Optional[ValidationError]]: (успешность валидации, ошибка если есть)
        """
        if not self._rules:
            return True, None
        
        for rule in self._rules:
            rule_type = rule["type"]
            codes = rule["codes"]
            
            if rule_type == "blacklist":
                if status_code in codes:
                    return False, self._create_error(
                        rule_type="blacklist",
                        expected_values=[f"not in {codes}"],
                        received_values=[status_code],
                        message=f"Status code {status_code} is in blacklist {codes}",
                    )
            
            elif rule_type == "whitelist":
                if status_code not in codes:
                    return False, self._create_error(
                        rule_type="whitelist",
                        expected_values=codes,
                        received_values=[status_code],
                        message=f"Status code {status_code} is not in whitelist {codes}",
                    )
        
        return True, None

