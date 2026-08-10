from fastapi import Request

from fastapi.responses import JSONResponse

from backend.core.exceptions import HireEZException


async def hireez_exception_handler(
    request: Request,
    exc: HireEZException
):

    return JSONResponse(

        status_code=400,

        content={

            "success": False,

            "message": exc.message,

            "data": None,

            "errors": [exc.message]

        }

    )