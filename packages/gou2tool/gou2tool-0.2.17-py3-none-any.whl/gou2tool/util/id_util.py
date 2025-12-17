import uuid

class IdUtil:

    @staticmethod
    def random_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def simple_uuid():
        return str(uuid.uuid4()).replace('-', '')