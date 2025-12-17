"""
PyX Validation System
Declarative input validation like Laravel.
"""
import re
from typing import Dict, List, Any, Optional, Union


class ValidationError(Exception):
    """Validation error with field-specific messages"""
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__(str(errors))


class Validator:
    """
    PyX Input Validator.
    
    Usage:
        from pyx import validate
        
        # Simple validation
        errors = validate(data, {
            "email": ["required", "email"],
            "password": ["required", "min:8"],
            "age": ["required", "number", "min:18", "max:100"]
        })
        
        if errors:
            return {"errors": errors}
        
        # With custom messages
        errors = validate(data, rules, messages={
            "email.required": "Email wajib diisi",
            "password.min": "Password minimal {min} karakter"
        })
    
    Available Rules:
        - required          : Field must exist and not be empty
        - email             : Must be valid email format
        - url               : Must be valid URL format
        - number            : Must be numeric
        - integer           : Must be integer
        - string            : Must be string
        - boolean           : Must be boolean
        - min:X             : Minimum length (string) or value (number)
        - max:X             : Maximum length (string) or value (number)
        - between:X,Y       : Value/length between X and Y
        - in:a,b,c          : Value must be in list
        - not_in:a,b,c      : Value must not be in list
        - regex:pattern     : Must match regex pattern
        - alpha             : Only letters
        - alpha_num         : Letters and numbers
        - alpha_dash        : Letters, numbers, dash, underscore
        - confirmed         : Must match {field}_confirmation
        - same:field        : Must match another field
        - different:field   : Must be different from another field
        - date              : Must be valid date format
        - before:date       : Must be date before given date
        - after:date        : Must be date after given date
    """
    
    # Default error messages
    DEFAULT_MESSAGES = {
        "required": "{field} is required",
        "email": "{field} must be a valid email",
        "url": "{field} must be a valid URL",
        "number": "{field} must be a number",
        "integer": "{field} must be an integer",
        "string": "{field} must be a string",
        "boolean": "{field} must be true or false",
        "min": "{field} must be at least {min}",
        "max": "{field} must not exceed {max}",
        "between": "{field} must be between {min} and {max}",
        "in": "{field} must be one of: {values}",
        "not_in": "{field} must not be one of: {values}",
        "regex": "{field} format is invalid",
        "alpha": "{field} must only contain letters",
        "alpha_num": "{field} must only contain letters and numbers",
        "alpha_dash": "{field} must only contain letters, numbers, dashes, and underscores",
        "confirmed": "{field} confirmation does not match",
        "same": "{field} must match {other}",
        "different": "{field} must be different from {other}",
        "date": "{field} must be a valid date",
        "before": "{field} must be a date before {date}",
        "after": "{field} must be a date after {date}",
    }
    
    def __init__(self, data: Dict[str, Any], rules: Dict[str, List[str]], messages: Dict[str, str] = None):
        self.data = data
        self.rules = rules
        self.custom_messages = messages or {}
        self.errors: Dict[str, List[str]] = {}
    
    def validate(self) -> Dict[str, List[str]]:
        """Run validation and return errors dict"""
        for field, rules in self.rules.items():
            # Normalize rules to list
            if isinstance(rules, str):
                rules = [rules]
            
            for rule in rules:
                self._validate_rule(field, rule)
        
        return self.errors
    
    def fails(self) -> bool:
        """Check if validation failed"""
        return len(self.errors) > 0
    
    def passes(self) -> bool:
        """Check if validation passed"""
        return len(self.errors) == 0
    
    def _add_error(self, field: str, rule: str, **params):
        """Add error message for field"""
        # Check custom message first
        custom_key = f"{field}.{rule}"
        if custom_key in self.custom_messages:
            message = self.custom_messages[custom_key]
        elif rule in self.custom_messages:
            message = self.custom_messages[rule]
        else:
            message = self.DEFAULT_MESSAGES.get(rule, f"{field} is invalid")
        
        # Format message with params
        message = message.format(field=field.replace("_", " ").title(), **params)
        
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
    
    def _get_value(self, field: str) -> Any:
        """Get field value from data"""
        return self.data.get(field)
    
    def _validate_rule(self, field: str, rule: str):
        """Validate a single rule"""
        value = self._get_value(field)
        
        # Parse rule and parameters
        if ":" in rule:
            rule_name, params = rule.split(":", 1)
        else:
            rule_name = rule
            params = None
        
        # Skip non-required empty values
        if rule_name != "required" and (value is None or value == ""):
            return
        
        # Call validation method
        method = getattr(self, f"_rule_{rule_name}", None)
        if method:
            method(field, value, params)
    
    # ==========================================
    # VALIDATION RULES
    # ==========================================
    
    def _rule_required(self, field: str, value: Any, params: str = None):
        """Value must exist and not be empty"""
        if value is None or value == "" or value == []:
            self._add_error(field, "required")
    
    def _rule_email(self, field: str, value: Any, params: str = None):
        """Must be valid email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, str(value)):
            self._add_error(field, "email")
    
    def _rule_url(self, field: str, value: Any, params: str = None):
        """Must be valid URL format"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(pattern, str(value)):
            self._add_error(field, "url")
    
    def _rule_number(self, field: str, value: Any, params: str = None):
        """Must be numeric"""
        try:
            float(value)
        except (ValueError, TypeError):
            self._add_error(field, "number")
    
    def _rule_integer(self, field: str, value: Any, params: str = None):
        """Must be integer"""
        try:
            int(value)
            if isinstance(value, float) and value != int(value):
                raise ValueError
        except (ValueError, TypeError):
            self._add_error(field, "integer")
    
    def _rule_string(self, field: str, value: Any, params: str = None):
        """Must be string"""
        if not isinstance(value, str):
            self._add_error(field, "string")
    
    def _rule_boolean(self, field: str, value: Any, params: str = None):
        """Must be boolean"""
        if not isinstance(value, bool) and value not in [0, 1, "0", "1", "true", "false"]:
            self._add_error(field, "boolean")
    
    def _rule_min(self, field: str, value: Any, params: str = None):
        """Minimum length/value"""
        min_val = float(params)
        
        # For numbers, check value
        try:
            num_val = float(value)
            if num_val < min_val:
                self._add_error(field, "min", min=int(min_val))
            return
        except (ValueError, TypeError):
            pass
        
        # For strings, check length
        if len(str(value)) < min_val:
            self._add_error(field, "min", min=int(min_val))
    
    def _rule_max(self, field: str, value: Any, params: str = None):
        """Maximum length/value"""
        max_val = float(params)
        
        # For numbers, check value
        try:
            num_val = float(value)
            if num_val > max_val:
                self._add_error(field, "max", max=int(max_val))
            return
        except (ValueError, TypeError):
            pass
        
        # For strings, check length
        if len(str(value)) > max_val:
            self._add_error(field, "max", max=int(max_val))
    
    def _rule_between(self, field: str, value: Any, params: str = None):
        """Value/length between X and Y"""
        min_val, max_val = params.split(",")
        min_val, max_val = float(min_val), float(max_val)
        
        try:
            num_val = float(value)
            if num_val < min_val or num_val > max_val:
                self._add_error(field, "between", min=int(min_val), max=int(max_val))
        except (ValueError, TypeError):
            length = len(str(value))
            if length < min_val or length > max_val:
                self._add_error(field, "between", min=int(min_val), max=int(max_val))
    
    def _rule_in(self, field: str, value: Any, params: str = None):
        """Value must be in list"""
        allowed = [v.strip() for v in params.split(",")]
        if str(value) not in allowed:
            self._add_error(field, "in", values=", ".join(allowed))
    
    def _rule_not_in(self, field: str, value: Any, params: str = None):
        """Value must not be in list"""
        forbidden = [v.strip() for v in params.split(",")]
        if str(value) in forbidden:
            self._add_error(field, "not_in", values=", ".join(forbidden))
    
    def _rule_regex(self, field: str, value: Any, params: str = None):
        """Must match regex pattern"""
        if not re.match(params, str(value)):
            self._add_error(field, "regex")
    
    def _rule_alpha(self, field: str, value: Any, params: str = None):
        """Only letters"""
        if not str(value).isalpha():
            self._add_error(field, "alpha")
    
    def _rule_alpha_num(self, field: str, value: Any, params: str = None):
        """Letters and numbers"""
        if not str(value).isalnum():
            self._add_error(field, "alpha_num")
    
    def _rule_alpha_dash(self, field: str, value: Any, params: str = None):
        """Letters, numbers, dash, underscore"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', str(value)):
            self._add_error(field, "alpha_dash")
    
    def _rule_confirmed(self, field: str, value: Any, params: str = None):
        """Must match {field}_confirmation"""
        confirmation = self._get_value(f"{field}_confirmation")
        if value != confirmation:
            self._add_error(field, "confirmed")
    
    def _rule_same(self, field: str, value: Any, params: str = None):
        """Must match another field"""
        other_value = self._get_value(params)
        if value != other_value:
            self._add_error(field, "same", other=params)
    
    def _rule_different(self, field: str, value: Any, params: str = None):
        """Must be different from another field"""
        other_value = self._get_value(params)
        if value == other_value:
            self._add_error(field, "different", other=params)
    
    def _rule_date(self, field: str, value: Any, params: str = None):
        """Must be valid date format"""
        from datetime import datetime
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"]
        
        valid = False
        for fmt in formats:
            try:
                datetime.strptime(str(value), fmt)
                valid = True
                break
            except ValueError:
                continue
        
        if not valid:
            self._add_error(field, "date")


def validate(
    data: Dict[str, Any],
    rules: Dict[str, Union[str, List[str]]],
    messages: Dict[str, str] = None
) -> Dict[str, List[str]]:
    """
    Validate data against rules.
    
    Args:
        data: Dictionary of data to validate
        rules: Dictionary of field -> rules
        messages: Custom error messages
        
    Returns:
        Dictionary of field -> error messages (empty if valid)
        
    Usage:
        errors = validate(
            {"email": "test", "password": "123"},
            {
                "email": ["required", "email"],
                "password": ["required", "min:8"]
            }
        )
        
        if errors:
            # {"email": ["Email must be a valid email"], "password": ["Password must be at least 8"]}
            return {"errors": errors}
    """
    validator = Validator(data, rules, messages)
    return validator.validate()


def validate_or_fail(
    data: Dict[str, Any],
    rules: Dict[str, Union[str, List[str]]],
    messages: Dict[str, str] = None
):
    """
    Validate data and raise ValidationError if fails.
    
    Usage:
        try:
            validate_or_fail(data, rules)
            # Data is valid, continue...
        except ValidationError as e:
            return {"errors": e.errors}
    """
    errors = validate(data, rules, messages)
    if errors:
        raise ValidationError(errors)
