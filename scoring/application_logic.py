# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime

ADMIN_LOGIN = "admin"
ADMIN_SCORE = "42"
ONLINE_SCORE = "online_score"
CLIENTS_INTERESTS = "clients_interests"


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message


class Field(object):
    def __init__(self, required=True, nullable=True):
        self.required = required
        self.nullable = nullable
        self.label = None

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.label, None)

    def __set__(self, instance, value):

        if value is None and self.required:
            raise ValidationError("\'{}\' is required field".format(self.label))
        if not value and not self.nullable:
            raise ValidationError("\'{}\'-field can't be empty".format(self.label))
        if value is not None and self.validation(value):
            instance.__dict__[self.label] = value

    def __str__(self):
        return "{}".format(self.label)


class CharField(Field):
    def __init__(self, required, nullable):
        super(CharField, self).__init__(required, nullable)

    def validation(self, value):
        if self.label == "first_name" or self.label == "last_name":
            for ch in value:
                if not ch.isalpha():
                    raise ValidationError("Name should consist of letters")
        return True


class ArgumentsField(Field):
    def __init__(self, required, nullable):
        super(ArgumentsField, self).__init__(required, nullable)

    def validation(self, args):
        try:
            for key in args:

                if not isinstance(args.get(key), (str, int, unicode, list)):
                    raise ValidationError
            return True
        except Exception:
            raise ValidationError("Oops..!Argument should be in line with json")


class PhoneField(Field):
    def __init__(self, required, nullable):
        super(PhoneField, self).__init__(required, nullable)

    def validation(self, value):
        value = str(value)
        if value[0] != "7":
            raise ValidationError("Oops..! International code in phone number must equal 7")
        if len(value) != 11:
            raise ValidationError("Oops..! Length of phone number must equal 11")
        return True


class EmailField(CharField):
    def __init__(self, required, nullable):
        super(EmailField, self).__init__(required, nullable)

    def validation(self, value):
        if '@' not in value:
            raise ValidationError("Oops..! Email must contain the @ character")
        return True


class BirthDayField(Field):
    def __init__(self, required, nullable):
        super(BirthDayField, self).__init__(required, nullable)

    def validation(self, value):
        delta = datetime.now() - datetime.strptime(value, "%d.%m.%Y")
        if delta.days > 365 * 70:
            raise ValidationError("Oops..! The age should not exceed 70")
        return True


class GenderField(Field):
    def __init__(self, required, nullable):
        super(GenderField, self).__init__(required, nullable)

    def validation(self, value):
        if value not in (0, 1, 2):
            raise ValidationError("Oops..! Error in gender")
        return True


class DateField(Field):
    def __init__(self, required, nullable):
        super(DateField, self).__init__(required, nullable)

    def validation(self, value):
        datetime.strptime(value, "%d.%m.%Y")
        return True


class ClientIDsField(Field):
    def __init__(self, required, nullable):
        super(ClientIDsField, self).__init__(required, nullable)
        self.offset = 0

    def next(self, value):
        if self.offset >= len(value):
            raise StopIteration
        else:
            item = value[self.offset]
            self.offset += 1
            return item

    def __iter__(self):
        return self

    def validation(self, value):
        if not isinstance(value, list):
            raise ValidationError("Oops! Clients ids need to be in array")
        for item in value:
            if not isinstance(item, int):
                raise ValidationError("Oops! Clients ids should be integer")
        return True


class DeclarativeRequestsMetaclass(type):
    def __new__(mcs, name, bases, attribute_dict):
        declared_fields = []
        # find all requests, auto-set their labels
        for key, value in attribute_dict.items():
            if isinstance(value, Field):
                declared_fields.append((key, value))
                value.label = key
        new_class = super(DeclarativeRequestsMetaclass, mcs).__new__(mcs, name, bases, attribute_dict)
        new_class.declared_fields = declared_fields

        return new_class


class BaseRequest(object):
    __metaclass__ = DeclarativeRequestsMetaclass

    def __init__(self, data=None):
        self.data = data or {}
        self.errors = {}
        for name, _ in self.declared_fields:
            value = self.data.get(name)

            try:
                setattr(self, name, value)
            except ValidationError as e:
                self.errors.update({name: e.message})

    def is_valid(self):
        return not self.errors


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def __init__(self, data):
        super(MethodRequest, self).__init__(data)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    @property
    def is_online_score(self):
        return self.method == ONLINE_SCORE

    @property
    def is_clients_interests(self):
        return self.method == CLIENTS_INTERESTS


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, data):
        super(OnlineScoreRequest, self).__init__(data)

    def is_valid(self):
        pair_1 = self.data.get("first_name") and self.data.get("last_name")
        pair_2 = self.data.get("phone") and self.data.get("email")
        pair_3 = self.data.get("birthday") and self.data.get("gender") is not None
        if not pair_1 and not pair_2 and not pair_3:
            self.errors.update({"ValidationError": "Request to get_score should consist of pair values"})

        return not self.errors


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    def __init__(self, data):
        super(ClientsInterestsRequest, self).__init__(data)


def get_score(store, arg):
    phone = arg.get("phone")
    email = arg.get("email")
    first_name = arg.get("first_name")
    last_name = arg.get("last_name")
    birthday = arg.get("birthday")
    gender = arg.get("gender")

    key_parts = [
        first_name or "",
        last_name or "",
        str(phone) or "",
        birthday or ""
    ]

    key = "uid:" + hashlib.md5("".join(key_parts)).hexdigest()
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    score = store.cache_get(key) or 0
    if score:
        return score
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return score


def get_interests(store, req):
    interests_response = dict()
    for cid in req.get("client_ids"):
        r = store.get(cid)
        if not isinstance(r, list):
            raise Exception(r)
        interests_response[cid] = r
    return interests_response
