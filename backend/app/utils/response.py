# app/utils/response.py
from fastapi.responses import JSONResponse

def success_response(data, message="Success"):
    return JSONResponse({"success": True, "message": message, "data": data})

def error_response(message, status_code=400):
    return JSONResponse({"success": False, "error": message}, status_code=status_code)