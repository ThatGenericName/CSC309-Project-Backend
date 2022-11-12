from __future__ import annotations

import os
from uuid import uuid4
import re

from PIL import Image

from studios.models import StudioSearchHash, StudioSearchTemp


def ValidatePhoneNumber(num: str):
    return not num.isalpha()

def ValidatePostalCode(postal_code: str):
    regex = '^(?!.*[DFIOQU])[A-VXY][0-9][A-Z] ?[0-9][A-Z][0-9]$'
    if re.match(regex, postal_code) is None:
        return False
    return True

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


'''
Some Search Utilities

'''
from functools import reduce
import operator
from django.db import models
from django.db.models import Q
def GenerateFilter(**kwargs):

    pass

def GenerateQObjectsContainsAnd(paramName:str, *args):
    qList = []
    q = f"{paramName}__contains"
    for q in args:
        if len(q) and isinstance(q, str):
            temp = {paramName: q}
            qobj = Q(**temp)
            qList.append(qobj)

    collapsed = reduce(operator.and_, qList)
    return collapsed

def ClearOldDateCalculations(searchHash: StudioSearchHash):
    StudioSearchTemp.objects.filter(searchkey=searchHash).delete()
    searchHash.delete()

def ClearAllDistCalculations():
    StudioSearchHash.objects.all().delete()
