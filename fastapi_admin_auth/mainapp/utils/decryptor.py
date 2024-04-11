# _*_ coding: utf-8 _*_
__author__ = 'kim dong-hun'
from cryptography.fernet import Fernet


class Decryptor(object):
    def __init__(self, key: str) -> None:
        self.f = Fernet(key)

    def dec(self, enc_data: bytes) -> bytes:
        """
        데이터 복호화
        :param enc_data:
        :return:
        """
        return self.f.decrypt(enc_data)
