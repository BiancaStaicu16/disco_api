from django.http import HttpResponse
from django.urls import re_path, path, include


def generate_api_urls(name):
    """
    Unlike your usual django app, we are using nested apps here.
    `api` is the main app with app its` sub-apps in `api_namespaces`.
    When creating a new app inside api, make sure you also add it to
    settings in addition to the api_namespaces list.
    """
    regex = r"^{}/".format(name)
    to_include = include("api.{}.urls".format(name))
    namespace = "api.{}".format(name)
    return re_path(regex, to_include, name=namespace)


api_namespaces = [
    "users",
]

urlpatterns = [
    path("", lambda _: HttpResponse("", status=204)),
    re_path(
        r"",
        include(
            [
                re_path(
                    r"", include([generate_api_urls(name) for name in api_namespaces])
                )
            ],
        ),
    ),
]
