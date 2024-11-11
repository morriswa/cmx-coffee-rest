"""
    Product Review models go here
"""
from typing import override
from app.validation import ValidatedDataModel,is_blank #Super class for all data models in the app
from app.exceptions import ValidationException #Exception class for validation errors
from product.models import BaseProduct

class CreateProductReview(ValidatedDataModel):
    def __init__(self, **kwargs): #kwargs unordered dictionary keyword arguments
        self.review_text = kwargs.get("review_text")
        self.review_score = kwargs.get("review_score")
        self.validate()

    @override
    def validate(self) -> None:
        excs = []

        if is_blank(self.review_text):
            excs.append(('review_text','cannot be null or empty'))

        if self.review_score < 1 or 5 < self.review_score:
            excs.append(('review_score', 'cannot be less than 1 or greater than 5'))

        if len(excs) > 0:
            raise ValidationException(excs)

class ProductStats(ValidatedDataModel):
    def __init__(self, **kwargs):#unordered dictionary key word arguements
        self.average_review_score = kwargs.get("average_review_score")
        self.review_count = kwargs.get("review_count")
        self.validate()

    @override
    def validate(self) -> None:
        if self.review_count is None:
             raise ValueError("Review Count should never be none")

class ProductReview(CreateProductReview):
    def __init__(self, **kwargs):
        self.review_id = kwargs.get("review_id")
        self.validate()

        super().__init__(**kwargs)
        super().validate()

    @override
    def validate(self) -> None:
        excs = []
        if self.review_id is None:
            excs.append(('review_id', 'cannot be null'))

        if len(excs) > 0:
            raise ValidationException(excs)
