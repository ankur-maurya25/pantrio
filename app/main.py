from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import auth, customer, pantry, shopping, recipes, stores, shopkeeper, admin
from app.core.config import settings
from app.core.exceptions import AppException
from app.db.database import Base, engine

# Create tables if not existing (e.g. for SQLite in-memory tests or initial launch)
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.1.0",
    description="Pantrio / PantryPilot Central Backend REST API for Android App & Web Frontend",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standard Error Envelope Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = "Validation error."
    if errors:
        loc = " -> ".join(str(l) for l in errors[0].get("loc", []))
        msg = f"{loc}: {errors[0].get('msg', 'Invalid field')}"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": msg
            }
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = "HTTP_ERROR"
    if exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        code = "FORBIDDEN"
    elif exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 409:
        code = "CONFLICT"
    elif exc.status_code >= 500:
        code = "INTERNAL_SERVER_ERROR"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail)
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred."
            }
        }
    )


# API Routers under /api/v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(customer.router, prefix="/api/v1")
app.include_router(pantry.router, prefix="/api/v1")
app.include_router(shopping.router, prefix="/api/v1")
app.include_router(recipes.router, prefix="/api/v1")
app.include_router(stores.router, prefix="/api/v1")
app.include_router(shopkeeper.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["Health"])
def api_v1_health():
    return {"status": "ok"}


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Pantrio Central REST API",
        "version": "1.1.0",
        "docs": "/docs"
    }
