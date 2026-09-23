"""Thin composition root for the local learning application."""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.controllers.api import router as api_router
from app.controllers.static import router as static_router
from app.services.http_security import LocalOnlyMiddleware,value_error,validation_error,internal_error

app=FastAPI(title='AIOps Academy',version='1.2.0-beta.2',docs_url=None,redoc_url=None)
app.add_middleware(LocalOnlyMiddleware)
app.add_exception_handler(ValueError,value_error)
app.add_exception_handler(RequestValidationError,validation_error)
app.add_exception_handler(Exception,internal_error)
app.include_router(api_router)
app.include_router(static_router)
