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
import core.views as core_views
import customer.views as customer_views
import vendor.views as vendor_views
import admin.views as admin_views
import product.views as product_views




urlpatterns = [
    # core app
    path('health', core_views.health),
    path('permissions', core_views.permissions),
    
    # vendor application
    path('s/forms/vendor-application', vendor_views.apply_for_vendor),
    
    # customer
    path('s/profile', customer_views.get_customer_profile),
    path('s/profile/product-preferences', customer_views.update_customer_product_preferences),
    
    # shopping
    path('s/shop/cart', customer_views.ShoppingCartView.as_view()),
    path('s/shop/products', product_views.get_products_for_sale),
    
    # product
    path('s/product/<int:product_id>', product_views.get_product_details),
    path('s/product/<int:product_id>/image', product_views.get_product_images),
    
    # vendor
    path('s/vendor/products', vendor_views.VendorProductView.as_view()),
    path('s/vendor/product/<int:product_id>', vendor_views.VendorProductDetailsView.as_view()),
    path('s/vendor/product/<int:product_id>/image', vendor_views.upload_product_image),
    path('s/vendor/product/<int:product_id>/image/<str:image_id>', vendor_views.delete_product_image),
    
    # admin
    path('a/vendor-applications', admin_views.get_pending_vendor_applications),
    path('a/vendor-application/<int:application_id>', admin_views.process_pending_vendor_application),
    
]

