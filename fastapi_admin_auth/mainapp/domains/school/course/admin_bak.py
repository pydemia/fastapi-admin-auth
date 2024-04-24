# from starlette_admin.contrib.sqla import Admin, ModelView

# # Create admin
# admin = Admin(engine, title="Example: SQLAlchemy")
# admin.add_view(ModelView(Post))

# admin.mount_to(app)

from typing import Any
from starlette_admin.contrib.sqla import ModelView
from starlette.requests import Request
from starlette_admin import action, row_action
from starlette_admin import (
    # TagsField,
    # StringField,
#     DateField,
#     TimeField,
#     DateTimeField,
#     TimeZoneField,
    # ListField,
#     ImageField,
    CollectionField,
#     PasswordField,
#     RelationField,
#     ArrowField,
#     ColorField,
    HasOne,
#     HasMany,
)

# from mainapp.core.admin import AuthorizedModelView


from .models import Course, Certificate


class CertificateModelView(ModelView):
    page_size = 10
    page_size_options = [10, 20, 50, 100, -1]
    fields = [
        "id",
        "name",
        # Certificate.description,
        "description",
        HasOne("course", identity="course_id"),
        # TagsField("tags", label="Tags"),
    ]

    def can_delete(self, request: Request) -> bool:
        return False

CertificateView = ModelView(
    Certificate,
    icon=None,
    # name="Course",
    label="Course Certificate",
)


class CourseModelView(ModelView):
    page_size = 10
    page_size_options = [10, 20, 50, 100, -1]
    fields = [
        "id",
        "name",
        # Course.description,
        "description",
        HasOne("book", identity="textbook"),
        # HasOne("certificate_id", identity="certificate_id"),
        # TagsField("tags", label="Tags"),
        HasOne("certificate", identity="certificate_id"),
        CollectionField(
            "certificate_info",
            # "certificate",
            fields=CertificateView.fields,
        )
    ]
    # exclude_fields_from_list = ["certificate_id"]
    # exclude_fields_from_detail = ["certificate_id"]
    # exclude_fields_from_edit = ["certificate_id"]
    # exclude_fields_from_list = ["cetrificate"]
    # exclude_fields_from_detail = ["cetrificate"]
    # exclude_fields_from_edit = ["cetrificate"]
    exclude_fields_from_list = ["certificate_info"]
    exclude_fields_from_detail = ["certificate_info"]
    exclude_fields_from_edit = ["certificate_info"]
    exclude_fields_from_create = ["certificate"]

    async def create(
            self,
            request: Request,
            data: dict[str, Any],
        ) -> Any:
        # certificate = data.pop("certificate_info")
        certificate = data.pop("certificate_info")
        certificate = Certificate(**certificate)
        # data["certificate_info"] = certificate.model_dump()
        # data["certificate"] = certificate.model_dump()
        data["certificate_info"] = certificate
        # data["certificate"] = certificate

        # data = Course.model_validate(data).model_dump()
        # return await super().create(request, data)
        course = await super().create(request, data)
        return course
        # return Course.model_validate(course.model_dump())

    async def edit(
            self,
            request: Request,
            pk: Any,
            data: dict[str, Any],
        ) -> Any:
        certificate = data.pop("certificate_info")
        certificate = Certificate.model_validate(certificate)
        data["certificate_info"] = certificate
        return await super().edit(request, pk, data)
        # course = await super().edit(request, pk, data)
        # return Course.model_validate(course.model_dump())


CourseView = CourseModelView(
    Course,
    label="Course",
)
# CourseView = ModelView(
#     Course,
#     label="Course",
# )


# CourseView = ModelView(
#     Course,
# )

# class CourseView(ModelView):
#     fields = ["id", "rel"]


# AuthorizedCourseView = AuthorizedModelView(
#     Course,
#     # name="Authorized Course",
#     icon=None,
#     name="Course: Authorized",
# )
# class AuthorizedCourseView(AuthorizedModelView):

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

# CourseView = AuthorizedCourseView(
#     Course,
#     # name="Authorized Course",
#     icon=None,
#     label="AuthorizedCourse",
# )



class CustomActionedCourseView(ModelView):
    exclude_fields_from_list = [Course.description]
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
        from mainapp.core.iam.idp import idp, get_user_id
        uu = request.state.user
        roles = idp.get_user_roles(get_user_id(request))
        idp.get_user_roles(request.state.user.get("sub"))
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


# ActionedCourseView = CustomActionedCourseView(
#     Course,
#     label="Course: CustomActioned",
# )