from __future__ import annotations

import os
from uuid import uuid4

from PIL import Image


def ValidatePhoneNumber(num: str):
    return not num.isalpha()

def ValidatePicture(a):
    trial_image = Image.open(a)
    try:
        trial_image.verify()
        return True
    except Exception as e:
        print(e)
        return False


'''
this format of custom filename generation is found here:
https://stackoverflow.com/questions/2680391/how-to-change-the-file-name-of-an-uploaded-file-in-django
'''


'''
All this currently does is check that all the payment information
is there and then returns True if that is the case.

Simulates a payment system I guess.
'''

def VerifyPayment(paymentData: dict) -> bool:
    PAYMENT_KEYS = (
        "card_type",
        'card_num',
        'card_name',
        'exp_month',
        'exp_year',
        'pin'
    )

    for k in PAYMENT_KEYS:
        if k not in paymentData:
            return False
    return True

class ValidateFloat:
    '''
    error 1 means empty value,
    error 2 means invalid value

    :param value:
    :return:
    '''
    error = 0
    value = None

    def __init__(self, value):
        self.value = value
        d = value
        if isinstance(d, str):
            if not len(d):
                self.error = 1
            else:
                try:
                    self.value = float(d)
                except ValueError:
                    self.error = 2
        elif isinstance(d, float) or isinstance(d, int):
            self.value = float(d)

class ValidateInt:
    '''
    error 1 means empty value,
    error 2 means invalid value

    :param value:
    :return:
    '''
    error = 0
    value = None

    def __init__(self, value):
        self.value = value
        d = value
        if isinstance(d, str):
            if not len(d):
                self.error = 1
            else:
                try:
                    self.value = int(float(d))
                except ValueError:
                    self.error = 2
        elif isinstance(d, float) or isinstance(d, int):
            self.value = int(float(d))

def str2bool(v):
    a = v.lower() in ("yes", "true", "t", "1")
    b = v.lower() in ("no", 'false', 'f', '0')

    if not a and not b:
        raise ValueError("the string is not a boolean")
    return a

class ValidateBool:
    '''
    error 1 means empty value,
    error 2 means invalid value

    :param value:
    :return:
    '''
    error = 0
    value = None

    def __init__(self, value):
        self.value = value
        d = value
        if isinstance(d, str):
            if not len(d):
                self.error = 1
            else:
                try:
                    self.value = str2bool(value)
                except ValueError:
                    self.error = 2
        elif isinstance(d, bool):
            self.value = d
