import inspect

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from starlette.requests import Request

from db.class_to_dict import serialize


# Custom router that runs simpler serialization logic to avoid certain
# pitfalls of FastAPIs standard serialization scheme. The specific use
# case for us is that FastAPI doesn't support the case where a dataclass
# extends a non dataclass, so it misses serializing those fields
class Router(APIRouter):
    def post(self, endpoint: str):
        def post_decorator(func):
            return super(Router, self).post(endpoint)(Router.get_serialize_wrapper(func))

        return post_decorator

    def get(self, endpoint: str):
        def get_decorator(func):
            return super(Router, self).get(endpoint)(Router.get_serialize_wrapper(func))
        
        return get_decorator

    @staticmethod
    def fix_signature(wrapper, func):
        params = [
            # Skip *args and **kwargs from wrapper parameters:
            *filter(
                lambda p: p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD),
                inspect.signature(wrapper).parameters.values()
            ),
            # Use all parameters from handler
            *inspect.signature(func).parameters.values()
        ]

        wrapper.__signature__ = inspect.Signature(
            parameters = params,
            return_annotation = inspect.signature(func).return_annotation,
        )

    @staticmethod
    def get_serialize_wrapper(func):
        def json_serialize(request: Request, *positional, **named):
            result = func(*positional, **named)
            return JSONResponse(content=serialize(result))

        Router.fix_signature(json_serialize, func)

        return json_serialize