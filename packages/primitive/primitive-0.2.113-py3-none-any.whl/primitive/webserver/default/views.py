from django.views import View
from django.http import JsonResponse
from django.http import HttpRequest
from primitive.client import Primitive
from django.http import HttpResponseRedirect

primitive = Primitive(host="api.dev.primitive.tech")

file_server_hostname = "192.168.10.1"


def get_ip_address_from_request(request: HttpRequest):
    ip_address = None
    HTTP_X_FORWARDED_FOR = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if HTTP_X_FORWARDED_FOR:
        ip_address = HTTP_X_FORWARDED_FOR.split(", ")[0]
    else:
        ip_address = request.META.get("REMOTE_ADDR", "")
    return ip_address


class IPtoMacAddressView(View):
    def get(self, request, *args, **kwargs):
        ip_address = get_ip_address_from_request(request)
        dest_to_lladdr = primitive.network.get_ip_address_to_mac_address_dict()
        if ip_address in dest_to_lladdr:
            target_mac_address = dest_to_lladdr[ip_address]
            return HttpResponseRedirect(
                f"http://{file_server_hostname}:9999/pxe/hardware/{target_mac_address}/boot.ipxe"
            )

        return JsonResponse(
            {"ip_address": ip_address, "message": "MAC address not found"}, status=404
        )
