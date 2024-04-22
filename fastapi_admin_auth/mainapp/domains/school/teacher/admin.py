# from starlette_admin.contrib.sqla import Admin, ModelView

# # Create admin
# admin = Admin(engine, title="Example: SQLAlchemy")
# admin.add_view(ModelView(Post))

# admin.mount_to(app)

from typing import Any
from starlette_admin.contrib.sqla import ModelView
from starlette.requests import Request
from starlette_admin import action, row_action

# from mainapp.core.admin import AuthorizedModelView


from .models import Teacher


TeacherView = ModelView(
    Teacher,
    icon=None,
    # name="Teacher",
    label="Teacher",
)


# AuthorizedTeacherView = AuthorizedModelView(
#     Teacher,
#     # name="Authorized Teacher",
#     icon=None,
#     name="Teacher: Authorized",
# )
# class AuthorizedTeacherView(AuthorizedModelView):

#     def is_accessible(
#         self, request: Request,
#     ) -> bool:
#         roles = request.state.user.get("roles")
#         if roles is None:
#             return False
#         if "default-roles-fastapi-admin-auth" not in roles:
#             return False
#         # key = request.state.user
#         return True

# TeacherView = AuthorizedTeacherView(
#     Teacher,
#     # name="Authorized Teacher",
#     icon=None,
#     label="AuthorizedTeacher",
# )



class CustomActionedTeacherView(ModelView):
    exclude_fields_from_list = [Teacher.description]
    def is_accessible(
        self, request: Request,
        # user: OIDCUser = Depends(idp.get_current_user()),
    ) -> bool:
        return True

    def can_view_details(self, request: Request) -> bool:
        return "read" in request.state.user["roles"]

    def can_create(self, request: Request) -> bool:
        return "create" in request.state.user["roles"]

    def can_edit(self, request: Request) -> bool:
        return "edit" in request.state.user["roles"]

    def can_delete(self, request: Request) -> bool:
        # from mainapp.core.iam.idp import idp, get_user_id
        # uu = request.state.user
        # roles = idp.get_user_roles(get_user_id(request))
        # idp.get_user_roles(request.state.user.get("sub"))
        return "delete" in request.state.user["roles"]

    async def is_action_allowed(self, request: Request, name: str) -> bool:
        if name == "make_published":
            return "action_make_published" in request.state.user["roles"]
        return await super().is_action_allowed(request, name)

    async def is_row_action_allowed(self, request: Request, name: str) -> bool:
        if name == "make_published":
            return "row_action_make_published" in request.state.user["roles"]
        return await super().is_row_action_allowed(request, name)

    @action(
        name="make_published",
        text="Mark selected articles as published",
        confirmation="Are you sure you want to mark selected articles as published ?",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
    )
    async def make_published_action(self, request: Request, pks: list[Any]) -> str:
        ...
        return "{} articles were successfully marked as published".format(len(pks))


    @row_action(
        name="make_published",
        text="Mark as published",
        confirmation="Are you sure you want to mark this article as published ?",
        icon_class="fas fa-check-circle",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
        action_btn_class="btn-info",
    )
    async def make_published_row_action(self, request: Request, pk: Any) -> str:
        ...
        return "The article was successfully marked as published"


ActionedTeacherView = CustomActionedTeacherView(
    Teacher,
    label="Teacher: CustomActioned",
)