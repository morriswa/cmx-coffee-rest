"""
    Admin-related database functions go here
"""

from app import connections

from vendor.models import VendorApplicationResponse

def get_pending_vendor_applications() -> list[VendorApplicationResponse]:
    with connections.cursor() as db:
        db.execute("select * from vendor_applicant")
        results = db.fetchall()
        assert results is not None
        return [VendorApplicationResponse(**result) for result in results]
