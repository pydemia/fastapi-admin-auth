from fastapi import APIRouter
from mainapp.core.exception_routers import HandledExceptionLoggingRoute

from .course.view import router as course_router
from .student.view import router as student_router
from .teacher.view import router as teacher_router
from .textbook.view import router as textbook_router

from .course import admin as course_admin
from .student import admin as student_admin

from pathlib import Path

module_path = Path(__file__).parent
list(filter(Path.is_dir, module_path.iterdir()))
import importlib

aa = importlib.import_module(__name__)
def filter_submodules(module):
    module_path = Path(module.__file__).parent
    return [p.parent.name for p in module_path.glob("*/__init__.py")]

import importlib
domain_module = importlib.import_module(__name__)
submodule_names = filter_submodules(domain_module)
submodule_names

importlib.import_module(f"{__name__}.{submodule_names[0]}.view")

importlib.import_module(__name__, f"{submodule_names[0]}.view")


def import_domains(module):
    import importlib
    domain_module = importlib.import_module(__name__)
    submodule_names = filter_submodules(domain_module)

    views = [importlib.import_module(f".{s}.view", __name__) for s in submodule_names]
    sub_routers = [view.router for view in views]

    admins = [importlib.import_module(f".{s}.admin", __name__) for s in submodule_names]
    



inspect.getmembers(module_imported, inspect.ismodule)

def import_domains(name: str):
    """
    Argument
    --------
        name: str
            __name__
    """
    import importlib
    from types import ModuleType
    import inspect
    domain_root_module = importlib.import_module(__name__)
    modules = inspect.getmembers(domain_root_module)

aa = importlib.find_loader(__name__)


aa = importlib.import_module(__name__)

aa = importlib.import_module(__name__, "")
router = APIRouter(
    prefix="/school",
    route_class=HandledExceptionLoggingRoute,
)

router.include_router(course_router)
router.include_router(student_router)
router.include_router(teacher_router)
router.include_router(textbook_router)

from .course import admin as 
from .student import admin import router as student_router
from .teacher import admin import router as teacher_router
from .textbook import admin view import router as textbook_router
