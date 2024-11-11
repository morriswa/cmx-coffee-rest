
from app.validation import ValidatedDataModel

class CreateMockPaymentRequest(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.nickname = kwargs.get('nickname')


class MockPaymentResponse(CreateMockPaymentRequest):
    def __init__(self, **kwargs):
        self.payment_id = kwargs.get('payment_id')
        self.payment_method = kwargs.get('payment_method')

        super().__init__(**kwargs)
