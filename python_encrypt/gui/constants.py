from enum import Enum


class PythonEncryptKeyBinding(Enum):
    PASSWORD = '-Password-'
    REPEAT_PASSWORD = '-Repeat_Password-'
    ENCRYPT = '-ENCRYPT-'
    DECRYPT = '-DECRYPT-'
    FILE_PATH_ENCRYPT = '-FILE_PATH_ENCRYPT-'
    FILE_PATH_DECRYPT = '-FILE_PATH_DECRYPT-'
