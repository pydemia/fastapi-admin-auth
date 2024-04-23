from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col, and_
from mainapp.core.database import db, Session

from .models import Certificate


class CertificateCRUD:
    def __init__(self):
        pass

    def __call__(
        self,
        session: Session = Depends(db.get_session),
    ):
        self.session = session
        return self

    def get_certificates_all(
        self,
    ) -> list[Certificate | None]:    

        session = self.session
        stmt = select(Certificate)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_certificates_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Certificate | None]:

        session = self.session
        stmt = select(Certificate)
        if order_by_asc:
            stmt.order_by(col(Certificate.id).asc())
        else:
            stmt.order_by(col(Certificate.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_certificates_by_ids(
        self,
        ids: Iterable,
    ) -> list[Certificate | None]:

        session = self.session
        stmt = select(Certificate).where(Certificate.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_certificate_by_id(
        self,
        id,
    ) -> Certificate | None:

        session = self.session
        stmt = select(Certificate).where(Certificate.id == id)
        stmt = session.exec(stmt)
        return stmt.first()

    def get_certificate_by_name(
        self,
        firstname: str,
        lastname: str,
    ) -> Certificate | None:

        session = self.session
        stmt = select(Certificate).where(
            and_(Certificate.firstname == firstname, Certificate.lastname == lastname)
        )
        stmt = session.exec(stmt)
        return stmt.first()

    def create_certificate(
        self,
        certificate: Certificate,
    ) -> Certificate:

        session = self.session
        session.add(certificate)
        session.commit()
        session.refresh(certificate)
        return certificate


    def get_or_create_certificate(
        self,
        firstname: str,
        lastname: str,
    ) -> Certificate:
        certificate: Certificate | None = self.get_certificate_by_name(
            firstname=firstname,
            lastname=lastname,
        )
        if certificate:
            return certificate
        else:
            certificate = Certificate(firstname=firstname, lastname=lastname)
            certificate = self.create_certificate(certificate)
            return certificate


    def update_certificate(
        self,
        certificate: Certificate,
    ) -> Certificate:

        session = self.session
        session.add(certificate)
        session.commit()
        session.refresh(certificate)
        return certificate

    def delete_certificate(
        self,
        certificate: Certificate,
    ) -> None:
        session = self.session
        session.delete(certificate)
        session.commit()
