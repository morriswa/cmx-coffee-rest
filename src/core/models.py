

from app.validation import ValidatedDataModel


class Territory(ValidatedDataModel):
    def __init__(self, **kwargs):
        self.territory_id = kwargs.get('territory_id')
        self.state_code = kwargs.get('state_code')
        self.country_code = kwargs.get('country_code')
        self.display_name = kwargs.get('display_name')

        if self.territory_id is None:
            raise ValueError('territory_id may never be none')

        if self.state_code is None:
            raise ValueError('state_code may never be none')

        if self.country_code is None:
            raise ValueError('country_code may never be none')

        if self.display_name is None:
            raise ValueError('display_name may never be none')
