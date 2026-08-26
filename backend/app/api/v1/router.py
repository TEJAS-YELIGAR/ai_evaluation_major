from fastapi import APIRouter
from app.api.v1.endpoints import auth, subjects, soe, booklets, results

router = APIRouter()

router.include_router(auth.router,     prefix="/auth",     tags=["Authentication"])
router.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
router.include_router(soe.router,      prefix="/soe",      tags=["Scheme of Evaluation"])
router.include_router(booklets.router, prefix="/booklets", tags=["Booklets"])
router.include_router(results.router,  prefix="/results",  tags=["Results"])