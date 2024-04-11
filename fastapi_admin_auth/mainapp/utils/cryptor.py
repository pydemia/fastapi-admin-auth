# _*_ coding: utf-8 _*_
__author__ = 'kim dong-hun'

from typing import Union, Tuple
import os
import base64
from hashlib import md5

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives import padding


def gen_key():
    """
    암복호 키 생성.
    :return:
    """
    key = Fernet.generate_key()

    try:
        file_out = open("crypto.key", "wb")
        file_out.write(key)
    except ValueError as e:
        raise e
    except OSError as e:
        raise e
    except Exception as e:
        raise e
    return True


class ConnectionCryptor:
    """ConnectionCryptor

    Common에서 기존에 사용 중인 RDB Connection 정보와 동일한 로직의 암/복호화 구현체
    """

    def __init__(self, passphrase: Union[str, bytes]):

        self.salt_len = 8
        self.key_len = 32
        self.block_size = 16
        if isinstance(passphrase, str):
            self.passphrase = passphrase.encode()
        else:
            self.passphrase = passphrase
        self.prefix = b"Salted__"

    def _pad(self, data: Union[str, bytes]) -> bytes:
        if isinstance(data, str):
            data = data.encode()
        length = self.block_size - (len(data) % self.block_size)
        return data + (chr(length)*length).encode()

    def _unpad(self, data: bytes) -> bytes:
        return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

    def _generate_salted_key_with_iv(self,
            passphrase: bytes,
            salt: bytes,
            ) -> Tuple[bytes]:
        """_generate_salted_key_with_iv

        passphrase와 salt로 48개의 bytes를 생성하고
        이 중 첫 32개를 key로, 뒤 16개를 iv로 사용.

        Parameters
        ----------
        passphrase : bytes
            key 생성을 위한 정해진 문자열
        salt : bytes
            암호화된 값에서 추출하거나 또는 임의로 생성한 bytes

        Returns
        -------
        bytes
            48 length bytes, first 32 for 'key' and last 16 for 'iv'.
        """
        _key_len_ = self.key_len + self.block_size

        passphrase += salt
        key = md5(passphrase).digest()
        final_key = key
        while len(final_key) < _key_len_:
            key = md5(key + passphrase).digest()
            final_key += key
        salted_key = final_key[:_key_len_]
        key, iv = self._parse_from_key(salted_key)
        return key, iv

    def _parse_from_key(self, key: bytes) -> Tuple[bytes]:
        key, iv = key[:self.key_len], key[-self.block_size:]
        return key, iv
    
    def _encode_encrypted(self, data: bytes, salt: bytes) -> bytes:
        return base64.urlsafe_b64encode(self.prefix + salt + data)
    
    def _decode_encrypted(self, data:bytes) -> Tuple[bytes]:
        data = base64.urlsafe_b64decode(data).lstrip(self.prefix)
        salt, data = data[:self.salt_len], data[self.salt_len:]
        return data, salt

    def _get_cipher(self, key: bytes, iv: bytes):
        cipher = Cipher(AES(key), CBC(iv))
        return cipher

    def encrypt(
            self,
            data: Union[str, bytes],
            as_str: bool = False,
            ) -> Union[str, bytes]:
        """encrypt

        복호화

        Parameters
        ----------
        data : Union[str, bytes]
            암호화할 값
        as_str : bool, optional. default False
            결과값을 str또는 bytes로 반환

        Returns
        -------
        Union[str, bytes]
            암호화된 값
        """
        if isinstance(data, str):
            data = data.encode()

        salt = os.urandom(self.salt_len)
        key, iv = self._generate_salted_key_with_iv(self.passphrase, salt)

        encryptor = self._get_cipher(key, iv).encryptor()
        encrypted = encryptor.update(self._pad(data)) + encryptor.finalize()
        res = self._encode_encrypted(encrypted, salt)

        if as_str:
            res = res.decode()
        return res
    
    def decrypt(
            self,
            data: Union[str, bytes],
            as_str: bool = False,
            ) -> Union[str, bytes]:
        """decrypt

        복호화

        Parameters
        ----------
        data : Union[str, bytes]
            복호화할 값
        as_str : bool, optional. default False
            결과값을 str또는 bytes로 반환

        Returns
        -------
        Union[str, bytes]
            복호화된 값
        """
        if isinstance(data, str):
            data = data.encode()

        data, salt = self._decode_encrypted(data)
        key, iv = self._generate_salted_key_with_iv(self.passphrase, salt)

        decryptor = self._get_cipher(key, iv).decryptor()
        decrypted = decryptor.update(data) + decryptor.finalize()
        res = self._unpad(decrypted)

        if as_str:
            res = res.decode()
        return res


if __name__ == "__main__":
    gen_key()
