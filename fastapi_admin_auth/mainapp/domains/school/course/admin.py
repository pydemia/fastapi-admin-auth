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
#     # TagsField,
#     # StringField,
# #     DateField,
# #     TimeField,
# #     DateTimeField,
# #     TimeZoneField,
#     # ListField,
# #     ImageField,
#     # CollectionField,
# #     PasswordField,
# #     RelationField,
    # ArrowField,
# #     ColorField,
    HasOne,
    HasMany,
)

# from mainapp.core.admin import AuthorizedModelView


from .models import Course, Certificate


class CertificateModelView(ModelView):
    page_size = 10
    page_size_options = [10, 20, 50, 100, -1]
    fields = [
        "id",
        "name",
        Certificate.description,
        # HasOne("course", identity="course_id"),
        # TagsField("tags", label="Tags"),
    ]


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
        Course.description,
        HasOne("book", identity="textbook"),
        HasOne("certificate", identity="certificate", required=True),
        HasOne("teacher", identity="teacher", required=True),
        HasMany("students", identity="student", required=False)
        # HasOne(Course.book.key, identity="textbook"),
        # HasOne(Course.certificate.key, identity="certificate", required=True),
        # HasOne(Course.teacher.key, identity="teacher", required=True),
        # HasMany(Course.students.key, identity="Student[multiple, optional]", required=False)
        # TagsField("tags", label="Tags"),
        # CollectionField(
        #     "certificate",
        #     fields=CertificateView.fields,
        #     # fields=[
        #     #     StringField
        #     # ]
        # )
        # ListField(
        #     field=CollectionField
        # )
    ]
    # exclude_fields_from_list = ["certificate"]
    # exclude_fields_from_detail = ["certificate"]
    # exclude_fields_from_edit = ["certificate"]

    # async def create(
    #         self,
    #         request: Request,
    #         data: dict[str, Any],
    #     ) -> Any:
    #     certificate = data.pop("certificate")
    #     certificate = Certificate.model_validate(certificate)
    #     data["certificate"] = certificate

    #     course = await super().create(request, data)
    #     return course

    # async def edit(
    #         self,
    #         request: Request,
    #         pk: Any,
    #         data: dict[str, Any],
    #     ) -> Any:
    #     certificate = data.pop("certificate")
    #     # Update the existing certifiate, delete the ones that are no longer there and add the new ones.
    #     certificate = Certificate.model_validate(certificate)
    #     data["certificate"] = certificate
    #     course = await super().edit(request, pk, data)
    #     return course


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
        from mainapp.core.iam.oauth import idp, get_user_id
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