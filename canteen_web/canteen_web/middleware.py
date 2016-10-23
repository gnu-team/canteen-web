# More or less copy-pasted from:
# http://www.django-rest-framework.org/topics/browser-enhancements/#http-header-based-method-overriding
# To account for Java's inability to send PATCH requests:
# https://bugs.openjdk.java.net/browse/JDK-7016595

METHOD_OVERRIDE_HEADER = 'HTTP_X_HTTP_METHOD_OVERRIDE'

class MethodOverrideMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.method != 'POST':
            return
        if METHOD_OVERRIDE_HEADER not in request.META:
            return
        request.method = request.META[METHOD_OVERRIDE_HEADER]
