from starlette.requests import Request
from starlette.responses import JSONResponse
from wasmer_app.services.email_service import EmailService, EventHandlerError


async def webhook_smtp2go_view(request: Request):
    try:
        await EmailService.process_event_smpt2go(request)
    except EventHandlerError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return JSONResponse({"status": "success"}, status_code=200)
