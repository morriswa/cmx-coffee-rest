"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.http import HttpResponse

import admin.views as admin_views
import core.views as core_views
import customer.views as customer_views
import payment.views as payment_views
import product.views as product_views
import product_review.views as review_views  # Import the views for product_reviews app
import vendor.views as vendor_views


# required to override django default 404
handler404 = lambda *args, **kwargs: HttpResponse(status=404)

# rest api paths
urlpatterns = [
    # core app
    path('health', core_views.health),
    path('s/permissions', core_views.permissions),

    # public product endpoints
    path('product/<int:product_id>', product_views.get_product_details),
    path('product/<int:product_id>/image', product_views.get_product_images),
    path('product/<int:product_id>/reviews', review_views.get_product_reviews),
    path('shop/products', product_views.get_products_for_sale),

    # vendor application
    path('s/forms/vendor-application', vendor_views.apply_for_vendor),

    # product review
    path('s/product/<int:product_id>/reviews', review_views.add_product_review),
    path('s/product/<int:product_id>/review/<int:review_id>', review_views.delete_product_reviews),
    path('product/<int:product_id>/reviews-stats',review_views.get_product_reviews_stats),

    # customer
    path('s/profile/product-preferences', customer_views.CustomerPreferencesView.as_view()),
    path('s/payment', payment_views.PaymentView.as_view()),

    # shopping
    path('s/shop/cart', customer_views.ShoppingCartView.as_view()),

    # vendor
    path('s/vendor/products', vendor_views.VendorProductView.as_view()),
    path('s/vendor/product/<int:product_id>', vendor_views.VendorProductDetailsView.as_view()),
    path('s/vendor/product/<int:product_id>/image', vendor_views.upload_product_image),
    path('s/vendor/product/<int:product_id>/image/<str:image_id>', vendor_views.delete_product_image),

    # admin
    path('s/admin/vendor-applications', admin_views.get_pending_vendor_applications),
    path('s/admin/vendor-application/<int:application_id>', admin_views.process_pending_vendor_application),
    path('s/admin/vendors', admin_views.get_all_vendors),
]
