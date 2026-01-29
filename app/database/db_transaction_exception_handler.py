from app.models.class_return_model.services_class_response_models import RepositoryClassResponse

class TransactionAbort(Exception):
    def __init__(self, response: RepositoryClassResponse):
        self.response = response