"""
PyX Form Validation System
Comprehensive validation with error states.
"""
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
import re
import uuid


@dataclass
class ValidationRule:
    """Single validation rule"""
    validator: Callable[[Any], bool]
    message: str


class Validators:
    """
    Pre-built validation rules.
    
    Usage:
        v = Validators
        rules = [v.required(), v.email(), v.min_length(8)]
    """
    
    @staticmethod
    def required(message: str = "This field is required") -> ValidationRule:
        return ValidationRule(
            validator=lambda v: v is not None and str(v).strip() != "",
            message=message
        )
    
    @staticmethod
    def email(message: str = "Please enter a valid email") -> ValidationRule:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return ValidationRule(
            validator=lambda v: re.match(pattern, str(v)) is not None,
            message=message
        )
    
    @staticmethod
    def min_length(length: int, message: str = None) -> ValidationRule:
        return ValidationRule(
            validator=lambda v: len(str(v)) >= length,
            message=message or f"Must be at least {length} characters"
        )
    
    @staticmethod
    def max_length(length: int, message: str = None) -> ValidationRule:
        return ValidationRule(
            validator=lambda v: len(str(v)) <= length,
            message=message or f"Must be at most {length} characters"
        )
    
    @staticmethod
    def min_value(value: float, message: str = None) -> ValidationRule:
        return ValidationRule(
            validator=lambda v: float(v) >= value,
            message=message or f"Must be at least {value}"
        )
    
    @staticmethod
    def max_value(value: float, message: str = None) -> ValidationRule:
        return ValidationRule(
            validator=lambda v: float(v) <= value,
            message=message or f"Must be at most {value}"
        )
    
    @staticmethod
    def pattern(regex: str, message: str = "Invalid format") -> ValidationRule:
        return ValidationRule(
            validator=lambda v: re.match(regex, str(v)) is not None,
            message=message
        )
    
    @staticmethod
    def phone(message: str = "Please enter a valid phone number") -> ValidationRule:
        pattern = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
        return ValidationRule(
            validator=lambda v: re.match(pattern, str(v)) is not None,
            message=message
        )
    
    @staticmethod
    def url(message: str = "Please enter a valid URL") -> ValidationRule:
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return ValidationRule(
            validator=lambda v: re.match(pattern, str(v)) is not None,
            message=message
        )
    
    @staticmethod
    def matches(field_name: str, message: str = None) -> ValidationRule:
        """Password confirmation etc."""
        return ValidationRule(
            validator=lambda v, data=None: data and v == data.get(field_name),
            message=message or f"Must match {field_name}"
        )
    
    @staticmethod
    def custom(fn: Callable[[Any], bool], message: str) -> ValidationRule:
        """Custom validation function"""
        return ValidationRule(validator=fn, message=message)


class FormValidator:
    """
    Form-level validation manager.
    
    Usage:
        validator = FormValidator({
            "email": [Validators.required(), Validators.email()],
            "password": [Validators.required(), Validators.min_length(8)],
            "confirm": [Validators.matches("password")]
        })
        
        errors = validator.validate(form_data)
        if errors:
            return errors
    """
    
    def __init__(self, schema: Dict[str, List[ValidationRule]]):
        self.schema = schema
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate data against schema.
        Returns dict of field -> error message (empty if valid)
        """
        errors = {}
        
        for field, rules in self.schema.items():
            value = data.get(field)
            
            for rule in rules:
                # Check if validator takes data for cross-field validation
                try:
                    if hasattr(rule.validator, '__code__') and rule.validator.__code__.co_argcount > 1:
                        valid = rule.validator(value, data)
                    else:
                        valid = rule.validator(value)
                except:
                    valid = False
                
                if not valid:
                    errors[field] = rule.message
                    break  # Stop at first error for this field
        
        return errors
    
    def validate_field(self, field: str, value: Any, data: Dict[str, Any] = None) -> Optional[str]:
        """Validate a single field, returns error message or None"""
        rules = self.schema.get(field, [])
        
        for rule in rules:
            try:
                if hasattr(rule.validator, '__code__') and rule.validator.__code__.co_argcount > 1:
                    valid = rule.validator(value, data or {})
                else:
                    valid = rule.validator(value)
            except:
                valid = False
            
            if not valid:
                return rule.message
        
        return None


class ValidatedInput:
    """
    Input with real-time validation.
    
    Usage:
        ValidatedInput(
            type="email",
            placeholder="Enter email",
            rules=[Validators.required(), Validators.email()],
            name="email"
        )
    """
    
    def __init__(
        self,
        type: str = "text",
        placeholder: str = "",
        rules: List[ValidationRule] = None,
        name: str = None,
        label: str = None,
        helper: str = None,
        validate_on: str = "blur",  # 'blur', 'input', 'submit'
        className: str = "",
    ):
        self.type = type
        self.placeholder = placeholder
        self.rules = rules or []
        self.name = name or f"input-{uuid.uuid4().hex[:8]}"
        self.label = label
        self.helper = helper
        self.validate_on = validate_on
        self.className = className
        self._id = f"validated-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        # Build validation rules for client
        client_rules = []
        for rule in self.rules:
            # Map common validators to client-side
            if "required" in str(rule.message).lower():
                client_rules.append({"type": "required", "message": rule.message})
            elif "email" in str(rule.message).lower():
                client_rules.append({"type": "email", "message": rule.message})
            elif "at least" in str(rule.message).lower():
                # Extract number from message
                import re
                match = re.search(r'\d+', rule.message)
                if match:
                    client_rules.append({"type": "minLength", "value": int(match.group()), "message": rule.message})
        
        import json
        rules_json = json.dumps(client_rules)
        
        label_html = ""
        if self.label:
            required = any("required" in str(r.message).lower() for r in self.rules)
            req_mark = '<span class="text-red-500 ml-1">*</span>' if required else ""
            label_html = f'<label for="{self._id}" class="block text-sm font-medium text-gray-700 mb-1">{self.label}{req_mark}</label>'
        
        helper_html = f'<p class="help-text text-sm text-gray-500 mt-1">{self.helper}</p>' if self.helper else ""
        
        event = f"on{self.validate_on}"
        
        return f'''
        <div id="{self._id}-container" class="validated-input {self.className}">
            {label_html}
            <input 
                type="{self.type}"
                id="{self._id}"
                name="{self.name}"
                placeholder="{self.placeholder}"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                {event}="PyxValidation.validate('{self._id}')"
                data-rules='{rules_json}'
            >
            <p class="error-text text-sm text-red-600 mt-1 hidden"></p>
            {helper_html}
        </div>
        
        <script>
            window.PyxValidation = window.PyxValidation || {{
                validate: function(id) {{
                    const input = document.getElementById(id);
                    const container = document.getElementById(id + '-container');
                    const errorEl = container.querySelector('.error-text');
                    const helpEl = container.querySelector('.help-text');
                    const rules = JSON.parse(input.dataset.rules || '[]');
                    const value = input.value;
                    
                    let error = null;
                    
                    for (const rule of rules) {{
                        if (rule.type === 'required' && !value.trim()) {{
                            error = rule.message;
                            break;
                        }}
                        if (rule.type === 'email' && value) {{
                            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                            if (!emailRegex.test(value)) {{
                                error = rule.message;
                                break;
                            }}
                        }}
                        if (rule.type === 'minLength' && value.length < rule.value) {{
                            error = rule.message;
                            break;
                        }}
                    }}
                    
                    if (error) {{
                        input.classList.add('border-red-500', 'focus:ring-red-500', 'focus:border-red-500');
                        input.classList.remove('border-gray-300', 'focus:ring-blue-500', 'focus:border-blue-500');
                        errorEl.textContent = error;
                        errorEl.classList.remove('hidden');
                        if (helpEl) helpEl.classList.add('hidden');
                    }} else {{
                        input.classList.remove('border-red-500', 'focus:ring-red-500', 'focus:border-red-500');
                        input.classList.add('border-gray-300', 'focus:ring-blue-500', 'focus:border-blue-500');
                        if (value) {{
                            input.classList.add('border-green-500');
                        }}
                        errorEl.classList.add('hidden');
                        if (helpEl) helpEl.classList.remove('hidden');
                    }}
                    
                    return !error;
                }},
                
                validateForm: function(formId) {{
                    const form = document.getElementById(formId);
                    const inputs = form.querySelectorAll('[data-rules]');
                    let valid = true;
                    
                    inputs.forEach(input => {{
                        if (!this.validate(input.id)) {{
                            valid = false;
                        }}
                    }});
                    
                    return valid;
                }}
            }};
        </script>
        '''
    
    def __str__(self):
        return self.render()


class ValidatedForm:
    """
    Form with validation support.
    
    Usage:
        ValidatedForm(
            ui.stack(
                ValidatedInput(label="Email", rules=[v.required(), v.email()]),
                ValidatedInput(label="Password", type="password", rules=[v.min_length(8)]),
                ui.button("Submit")
            ),
            on_submit=handle_submit
        )
    """
    
    def __init__(
        self,
        content,
        on_submit: Callable = None,
        validate_on_submit: bool = True,
        className: str = "",
    ):
        self.content = content
        self.on_submit = on_submit
        self.validate_on_submit = validate_on_submit
        self.className = className
        self._id = f"form-{uuid.uuid4().hex[:8]}"
    
    def render(self) -> str:
        content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content)
        
        submit_handler = ""
        if self.on_submit:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_submit)
            submit_handler = f"""
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                window.ws.send(JSON.stringify({{
                    type: 'event',
                    handler: '{handler_name}',
                    data: data
                }}));
            """
        
        validate_code = ""
        if self.validate_on_submit:
            validate_code = f"""
                if (!PyxValidation.validateForm('{self._id}')) {{
                    return;
                }}
            """
        
        return f'''
        <form id="{self._id}" class="{self.className}" onsubmit="(function(e) {{
            e.preventDefault();
            const form = document.getElementById('{self._id}');
            {validate_code}
            {submit_handler}
        }})(event)">
            {content_html}
        </form>
        '''
    
    def __str__(self):
        return self.render()
