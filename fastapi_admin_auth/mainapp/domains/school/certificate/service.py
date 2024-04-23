from typing import Any
from .models import Certificate
from fastapi import Depends
# from .crud import (
#     get_certificates_all,
#     get_certificates_by_ids,
#     get_certificates_by_range,
#     get_certificate_by_id,
#     create_certificate,
#     update_certificate,
#     delete_certificate,
# )

# get_certificates_all
# get_certificates_by_ids
# get_certificates_by_range
# get_certificate_by_id
# create_certificate
# update_certificate
# delete_certificate
from mainapp.core.types.exceptions import HandledException, ResponseCode
from .crud import CertificateCRUD


class CertificateService:
    def __init__(self):
        pass

    def __call__(
        self,
        crud: CertificateCRUD = Depends(CertificateCRUD()),
    ):
        self.crud = crud
        return self


    def add_new_certificate(
        self,
        certificate: dict[str, Any] | Certificate,
    ) -> Certificate:
        if isinstance(certificate, dict):
            certificate = Certificate(
                firstname=certificate["firstname"],
                lastname=certificate["lastname"],
                description=certificate.get("description"),
            )
        certificate = self.crud.create_certificate(certificate)
        return certificate


    def add_new_certificates(
        self,
        certificate_list: list[dict[str, Any] | Certificate],
    ) -> list[Certificate]:
        certificates = [self.add_new_certificate(certificate) for certificate in certificate_list]
        return certificates


    def get_certificate_by_name(
        self,
        firstname: str,
        lastname: str,
    ) -> Certificate | None:
        certificate = self.crud.get_certificate_by_name(firstname, lastname)
        return certificate


    def get_certificate_by_id_or_entity(
        self,
        id_or_entity: int | Certificate,
    ) -> Certificate | None:
        if isinstance(id_or_entity, int):
            certificate = self.crud.get_certificate_by_id(id_or_entity)
        elif isinstance(id_or_entity, Certificate):
            certificate = self.crud.get_certificate_by_id(id_or_entity.id)
        else:
            raise HandledException(ResponseCode.ENTITY_ID_INVALID)

        return certificate


    def get_certificates_all(
        self,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Certificate | None]:
        if page:
            certificates = self.crud.get_certificates_by_range(page=1)
        else:
            certificates = self.crud.get_certificates_all()
        return certificates
    
    def update_certificate_description(
        self,
        name: str,
        description: str,
    ) -> Certificate:
        certificate = self.get_certificate(name)
        if not certificate:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        
        certificate.description = description
        certificate = self.crud.update_certificate(certificate)
        return certificate


    def update_certificate(
        self,
        certificate_id: int,
        new_certificate: Certificate,
    ) -> Certificate:
        old_certificate: Certificate | None = self.crud.get_certificate_by_id(certificate_id)
        if not old_certificate:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        old_certificate.firstname = new_certificate.firstname
        old_certificate.lastname = new_certificate.lastname
        old_certificate.description = new_certificate.description
        certificate = self.crud.update_certificate(old_certificate)

        return certificate


    def delete_certificate(
        self,
        certificate_id: str,
    ) -> bool:
        certificate = self.get_certificate_by_id_or_entity(certificate_id)
        if not certificate:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        self.crud.delete_certificate(certificate)
        return
