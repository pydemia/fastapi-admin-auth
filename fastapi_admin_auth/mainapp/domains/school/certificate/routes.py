from fastapi import APIRouter, Depends
# from mainapp.core.database import Session
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse
from .models import Certificate
from .service import CertificateService
from .schema import CertificateRequest


router = APIRouter(
    prefix="/certificates",
    tags=["certificates"],
    route_class=HandledExceptionLoggingRoute,
)


@router.get("")
async def get_certificates(
    firstname: str | None = None,
    lastname: str | None = None,
    service: CertificateService = Depends(CertificateService()),
):
    if firstname and lastname:
        certificate_or_certificates = service.get_certificate_by_name(firstname, lastname)
    else:
        certificate_or_certificates = service.get_certificates_all()
    return CommonResponse(data=certificate_or_certificates)


@router.post("")
async def add_certificate(
    body: CertificateRequest,
    service: CertificateService = Depends(CertificateService()),
    ):
    certificate: Certificate = service.add_new_certificate(
        certificate={
            "firstname": body.firstname,
            "lastname": body.lastname,
            "description": body.description,
        },
    )
    return CommonResponse(data=certificate)


@router.get("/{certificate_id}")
async def get_certificate_by_id(
    certificate_id: int,
    service: CertificateService = Depends(CertificateService()),
):
    certificate = service.get_certificate_by_id_or_entity(certificate_id)
    return CommonResponse(data=certificate)


@router.put("/{certificate_id}")
async def update_certificate(
    certificate_id: int,
    body: CertificateRequest,
    service: CertificateService = Depends(CertificateService()),
):
    
    certificate = service.update_certificate(certificate_id, body)
    return CommonResponse(data=certificate)


@router.delete("/{certificate_id}")
async def delete_certificate(
    certificate_id: int,
    service: CertificateService = Depends(CertificateService()),
):
    is_deleted = service.delete_certificate(certificate_id)
    return CommonResponse(
        data={
            "id": certificate_id,
            "is_deleted": is_deleted,
        }
    )
