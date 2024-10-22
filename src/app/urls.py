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
import vendor.views as vendor_views
import admin.views as admin_views


urlpatterns = [
    # core app
    path('health', core_views.health),
    path('permissions', core_views.permissions),
    # vendor application
    path('s/forms/vendor-application', vendor_views.apply_for_vendor),
    # admin
    path('a/vendor-applications', admin_views.get_pending_vendor_applications),
]
