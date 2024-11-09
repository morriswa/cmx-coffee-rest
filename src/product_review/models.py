"""
    Product Review models go here
"""
from typing import override
from app.validation import ValidatedDataModel,is_blank #Super class for all data models in the app
from app.exceptions import ValidationException #Exception class for validation errors

class CreateProductReview(ValidatedDataModel):
    def __init__(self, **kwargs): #kwargs unordered dictionary keyword arguments
        self.product_id = kwargs.get("product_id")
        self.user_id = kwargs.get("user_id")
        self.review_text = kwargs.get("review_text")
        self.review_score = kwargs.get("review_score")
        self.validate()

    @override
    def validate(self) -> None:
        excs = []
        if self.product_id is None:
            excs.append(('product_id', 'cannot be null'))

        if self.user_id is None:
            excs.append(('user_id', 'cannot be null'))

        if is_blank(self.review_text):
            excs.append(('review_text','cannot be null or empty'))

        if 1 <= self.review_score <= 5: 
            excs.append(('review_score', 'cannot be less than 1 or greater than 5'))

        if len(excs) > 0:
            raise ValidationException(excs)




    