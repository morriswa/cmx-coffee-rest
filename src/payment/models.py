
from app.validation import ValidatedDataModel


class CreateMockPaymentRequest(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.nickname = kwargs.get('nickname')
        self.territory = kwargs.get('territory')


class MockPaymentResponse(CreateMockPaymentRequest):
    def __init__(self, **kwargs):
        self.payment_id = kwargs.get('payment_id')
        self.payment_method = kwargs.get('payment_method')
        self.territory_name  = kwargs.get('territory_name')

        super().__init__(**kwargs)
