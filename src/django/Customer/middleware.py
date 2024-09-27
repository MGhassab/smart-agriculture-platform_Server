import json


class ReadTokenFromBodyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            body = json.loads(request.body)
            token = body.get("Authorization", None)
            if token is not None:
                request.META["HTTP_AUTHORIZATION"] = token
        except ValueError:
            pass
        response = self.get_response(request)
        return response
