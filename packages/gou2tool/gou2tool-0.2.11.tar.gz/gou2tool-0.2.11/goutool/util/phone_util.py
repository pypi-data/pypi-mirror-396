import re

class PhoneUtil:

    @staticmethod
    def is_phone(value):
        if not value:
            return False
        return PhoneUtil.is_mobile(value) or PhoneUtil.is_tel(value)

    @staticmethod
    def is_mobile(value):
        if not value:
            return False
        return bool(re.match(r'^1[3-9]\d{9}$', value))

    @staticmethod
    def is_tel(value):
        if not value:
            return False
        return bool(re.match(r'^(0\d{2,3}[- ]?)?\d{7,8}(-\d{1,6})?$', value))

    @staticmethod
    def hide_between(phone):
        return phone[0:3] + '****' + phone[-4:]