"""
    Admin-related data models go here
"""

from vendor.models import VendorInformation

class AdminVendorInfo(VendorInformation):
    def __init__(self, **kwargs):
        self.approver_email = kwargs.get('approver_email')

        super().__init__(**kwargs)
