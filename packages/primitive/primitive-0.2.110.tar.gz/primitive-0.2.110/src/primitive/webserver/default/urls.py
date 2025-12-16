from django.urls import path
from .views import IPtoMacAddressView

urlpatterns = [
    path(
        "pxe/ip-address-to-mac-address/",
        IPtoMacAddressView.as_view(),
        name="ip_to_mac",
    ),
]
