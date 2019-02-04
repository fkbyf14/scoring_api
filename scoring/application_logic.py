# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime

ADMIN_LOGIN = "admin"
ADMIN_SCORE = "42"
ONLINE_SCORE = "online_score"
CLIENTS_INTERESTS = "clients_interests"


class CharField(object):
    def __init__(self, chars):
        self.chars = chars.decode('utf-8')

    def __str__(self):
        return "{}".format(self.chars)


class ArgumentsField(object):
    def __init__(self, args):
        self.args = args
        """for key in args:
            if not (isinstance(key, str) and isinstance(args.get(key), str)
                    or isinstance(args.get(key), int)):
                raise Exception("Oops..!Argument should be in line with json")"""


class PhoneField(object):
    def __init__(self, international_code, phone_num):
        if international_code != "7":
            raise Exception("Oops..! International code in phone number must equal 7")
        if len(phone_num) != 11:
            raise Exception("Oops..! Length of phone number must equal 11")

        self.phone_num = phone_num

    def __repr__(self):
        return "{}".format(self.phone_num)


class EmailField(CharField):
    def __init__(self, email):
        super(EmailField, self).__init__(email)
        if '@' not in email:
            raise Exception("Oops..! Email must contain the @ character")
        self.email = email

    def __repr__(self):
        return "{}".format(self.email)


class BirthDayField(object):
    def __init__(self, birthday):
        self.birthday = datetime.strptime(birthday, "%d.%m.%Y")

        if datetime.now().year - self.birthday.year > 70:
            raise Exception("Oops..! The age should not exceed 70")

    def __str__(self):
        return "{}".format(self.birthday)


class GenderField(object):
    def __init__(self, gender):
        if gender not in (0, 1, 2):
            raise Exception("Oops..! Error in gender")

        self.gender = gender

    def __repr__(self):
        return "{}".format(self.gender)


class Validator(object):
    def __init__(self, arg):
        not_empty_fields = dict()
        if arg.get("phone"):
            self.phone = PhoneField(str(arg.get("phone"))[0], str(arg.get("phone")))
            not_empty_fields["phone"] = 1

        if arg.get("email"):
            self.email = EmailField(arg.get("email"))
            not_empty_fields["email"] = 1

        if arg.get("first_name"):
            self.first_name = CharField(arg.get("first_name"))
            not_empty_fields["first_name"] = 1

        if arg.get("last_name"):
            self.last_name = CharField(arg.get("last_name"))
            not_empty_fields["last_name"] = 1

        if arg.get("birthday"):
            self.birthday = BirthDayField(arg.get("birthday"))#.replace(".", ''))
            not_empty_fields["birthday"] = 1

        if arg.get("gender"):
            self.gender = GenderField(arg.get("gender"))
            not_empty_fields["gender"] = 1

        self.not_empty_fields = not_empty_fields


class MethodRequest(object):
    def __init__(self, request):
        if request.get("account") is not None:
            self.account = CharField(request.get("account"))

        if request.get("login") is None:
            raise ValueError("Please, fill up the login field")

        if request.get("token") is None:
            raise ValueError("Please, fill up the token field")

        if request.get("arguments") is None:
            raise ValueError("Please, fill up the method field")

        if request.get("method") is None:
            raise ValueError("Please, fill up the fields of arguments")

        self.login = CharField(request.get("login"))
        self.token = CharField(request.get("token"))
        self.method = CharField(request.get("method"))
        self.arguments = ArgumentsField(request.get("arguments"))

    @property
    def is_online_score(self):
        return str(self.method) == ONLINE_SCORE   # O_o

    @property
    def is_clients_interests(self):
        return str(self.method) == CLIENTS_INTERESTS

    @property
    def is_admin(self):
        return str(self.login) == ADMIN_LOGIN


class DateField(object):
    def __init__(self, date):
        self.birthday = datetime.strptime(date, "%d.%m.%Y")


class ClientIDsField(object):
    def __init__(self, clients_ids):
        if not isinstance(clients_ids, list):
            raise ValueError("Oops! Clients ids need to be in array")
        for item in clients_ids:
            if not isinstance(item, int):
                raise ValueError("Oops! Clients ids should be integer")
        self.clients_ids = clients_ids
        self.offset = 0

    def next(self):
        if self.offset >= len(self.clients_ids):
            raise StopIteration
        else:
            item = self.clients_ids[self.offset]
            self.offset += 1
            return item

    def __iter__(self):
        return self


class ValidatorInterests(object):
    def __init__(self, arg):
        if not arg.get("client_ids"):
            raise Exception("Please, fill up the clients_ids field")

        self.client_ids = ClientIDsField(arg.get("client_ids"))
        if arg.get("date") is not None:
            self.date = DateField(arg.get("date"))


def get_score(store, arg):#phone, email, first_name=None, last_name=None, birthday=None, gender=None):
    phone = arg.get("phone")
    email = arg.get("email")
    first_name = arg.get("first_name")
    last_name = arg.get("last_name")
    birthday = arg.get("birthday")
    gender = arg.get("gender")

    if arg.get("birthday"):
        birthday = BirthDayField(birthday).birthday

    key_parts = [
        first_name or "",
        last_name or "",
        str(phone) or "",
        birthday.strftime("%Y%m%d") if birthday else "",
    ]

    key = "uid:" + hashlib.md5("".join(key_parts)).hexdigest()
    print key
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
    print score, type(score)
    return score


def get_interests(store, req):
    interests_response = dict()
    for cid in req.get("client_ids"):
        r = store.get(cid)
        interests_response[cid] = r
    return interests_response
