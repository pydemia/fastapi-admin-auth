# _*_ coding: utf-8 _*_
__author__ = 'kim dong-hun'
from cryptography.fernet import Fernet


class Encryptor(object):
    def __init__(self, key: str) -> None:
        self.f = Fernet(key)

    def enc(self, plain_data: str) -> bytes:
        """
        데이터 암호화
        :param plain_data:
        :return:
        """
        enc_block = plain_data.encode('utf-8')

        return self.f.encrypt(enc_block)
