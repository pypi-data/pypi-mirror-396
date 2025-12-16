import re

class EmailUtil:

    @staticmethod
    def is_email(value):
        if not value:
            return False
        return bool(re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$', value))