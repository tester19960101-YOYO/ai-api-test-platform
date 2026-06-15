from fastapi import APIRouter

from app.api.v1.ai_generation_api import router as ai_generation_router
from app.api.v1.assertion_api import router as assertion_router
from app.api.v1.api_document_api import router as api_document_router
from app.api.v1.api_endpoint_api import router as api_endpoint_router
from app.api.v1.environment_api import router as environment_router
from app.api.v1.execution_api import router as execution_router
from app.api.v1.health_api import router as health_router
from app.api.v1.project_api import router as project_router
from app.api.v1.test_case_api import router as test_case_router
from app.core.config import settings

api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(project_router, tags=["projects"])
api_router.include_router(environment_router, tags=["environments"])
api_router.include_router(api_document_router, tags=["api-documents"])
api_router.include_router(api_endpoint_router, tags=["api-endpoints"])
api_router.include_router(test_case_router, tags=["test-cases"])
api_router.include_router(ai_generation_router, tags=["ai-generation"])
api_router.include_router(execution_router, tags=["executions"])
api_router.include_router(assertion_router, tags=["assertion"])
api_router.include_router(health_router, tags=["health"])
