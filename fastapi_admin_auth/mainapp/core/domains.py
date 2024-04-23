from pathlib import Path
import importlib
from types import ModuleType
import inspect
from starlette_admin.contrib.sqla.view import BaseModelView
from sqlmodel import SQLModel

from fastapi import APIRouter
from mainapp.core.exception_routers import HandledExceptionLoggingRoute



def filter_submodules(module):
    module_path = Path(module.__file__).parent
    return [p.parent.name for p in module_path.glob("*/__init__.py")]

def import_domain_components(module_or_qualname: ModuleType | str):
    """
    Argument
    --------
        module_or_qualname: str
            module can be a module itself (ex. `import sys; import_domain_components(sys)`)
            qualname can be `__name__` or `__qualname__` (ex. `"a"` or `"a.b"`)

    Return
    ------
        router, admin_views, models

            router: fastapi.routing.APIRouter
            admin_views: List[starlette_admin.contrib.sqla.view.BaseModelView]
            models: List[sqlmodel.main.SQLModel]

    """
    # import domain modules
    if isinstance(module_or_qualname, ModuleType):
        _module_qualname_ = module_or_qualname.__name__
        _domain__name_ = _module_qualname_.split(".")[-1]
        domain_module = module_or_qualname
    elif isinstance(module_or_qualname, str):
        _module_qualname_ = module_or_qualname
        _domain__name_ = _module_qualname_.split(".")[-1]
        domain_module = importlib.import_module(_module_qualname_)
    else:
        raise TypeError(
            f"'module_or_qualname' should be one of ['ModuleType', 'str']. given {type(module_or_qualname)}"
        )
    submodule_names = filter_submodules(domain_module)
    submodules = [importlib.import_module(f".{s}", _module_qualname_) for s in submodule_names]
    
    # import domain routers
    routers = [importlib.import_module(".routes", s.__name__).router for s in submodules]

    def append_domain_tag(router):
        router.tags = [f"{_domain__name_}/{tag}" for tag in router.tags]
        return router
    routers = [append_domain_tag(router) for router in routers]

    # import admin_views
    admin_modules = [importlib.import_module(".admin", s.__name__) for s in submodules]
    def is_modelview(attr):
        return isinstance(attr, BaseModelView)
    admin_views = sum(
        [
            [obj for name, obj in inspect.getmembers(module, is_modelview)]
            for module in admin_modules
        ],
        [],
    )
    domain_router = APIRouter(
        prefix=f"/{_domain__name_}",
        route_class=HandledExceptionLoggingRoute,
    )
    for router in routers:
        domain_router.include_router(router)


    # import domain models
    model_modules = [importlib.import_module(".models", s.__name__) for s in submodules]
    def is_model(attr):
        return isinstance(attr, SQLModel)
    models = sum(
        [
            [obj for name, obj in inspect.getmembers(module, is_model)]
            for module in model_modules
        ],
        [],
    )
    return domain_router, admin_views, models


# def add_admin_views(
#     admin: Admin,
#     admin_views: list[BaseModelView],
# ) -> Admin:
#     for admin_view in admin_views:
#         admin.add_view(admin_view)
#     return admin

