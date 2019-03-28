import datetime
import hashlib
import unittest


from tests import cases
from scoring import api, application_logic


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.settings = {}

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.settings)

    @staticmethod
    def set_valid_auth(request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest()
        else:
            msg = request.get("account", "") + request.get("login", "") + api.SALT
            request["token"] = hashlib.sha512(msg).hexdigest()

    @cases([
        -1, 0, b'', [], {}
    ])
    def test_invalid_char_field(self, value):
        char_field = application_logic.CharField(required=False, nullable=True)
        with self.assertRaises(application_logic.ValidationError):
            char_field.validation(value)

    @cases([
        '', 'None', 'null', '0', '{}', '[]'
    ])
    def test_valid_char_field(self, value):
        char_field = application_logic.CharField(required=False, nullable=True)
        try:
            char_field.validation(value)
        except application_logic.ValidationError:
            pass

    @cases([
        {"first_name": "a1", "last_name": "b2"},
        {"first_name": "a&", "last_name": "b?"},
    ])
    def test_invalid_name(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases([
        {"phone": [79584545712], "email": ("python@", "@")},
        {"first_name": {"otus","o"}, "last_name": "b"},
    ])
    def test_invalid_arguments_field(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases([
        {'x': 'z'}, {0: None}, {}
    ])
    def test_valid_arguments_field(self, value):
        arguments_field = application_logic.ArgumentsField(nullable=True)
        try:
            arguments_field.validatation(value)
        except application_logic.ValidationError:
            pass

    @cases([
        -1, 0, b'', [], {},
        -79638527411, 796385274111, 79638527411, 49523965411, '-79638527411',
        '+79638527411', '7(963)8527411', '796385274111', '7963852741', '7 963 852-74-11'
    ])
    def test_invalid_phone_field(self, value):
        phone_field = application_logic.PhoneField(nullable=True)
        with self.assertRaises(api.ValidationError):
            phone_field.validation(value)

    @cases([
        '', '79638527411', 79638527411, 70000000000, 79999999999
    ])
    def test_valid_phone_field(self, value):
        phone_field = application_logic.PhoneField(nullable=True)
        try:
            phone_field.validation(value)
        except application_logic.ValidationError:
            self.fail()

    @cases([
        'user', 'user@', '@domain.tld', 'user@domain', 'first last@domain.tld', '<user@domain.tld>'
    ])
    def test_invalid_email_field(self, value):
        email_field = application_logic.EmailField(nullable=True)
        with self.assertRaises(application_logic.ValidationError):
            email_field.validation(value)

    @cases([
        'user@domain.tld', 'first.last@domain.sub.tld'
    ])
    def test_valid_email_field(self, value):
        email_field = application_logic.EmailField(nullable=True)
        try:
            email_field.validation(value)
        except application_logic.ValidationError:
            self.fail()

    @cases([
        {"phone": 89584545712, "email": "python@g"},
        {"phone": 895845457123, "email": "python@g"},
        {"phone": 89584545712, "email": "python"}
    ])
    def test_bad_phone_and_email_field(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases([
        {"birthday": '11.12.1999', "gender": 3},
        {"birthday": '11.12.1999', "gender": -1},
        {"birthday": '11.12.1909', "gender": 0}
    ])
    def test_bad_birthday_and_gender(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases([
        -1, 0, b'', [], {},
        '2001-01-01', '01-01-01', '01.01.0000'
        '01/01/2001', '01/01/01', '01.01.01',
        '32.01.2001', '01.13.2001', '1.1.1',

    ])
    def test_invalid_date_field(self, value):
        date_field = application_logic.DateField(nullable=True)
        with self.assertRaises(application_logic.ValidationError):
            date_field.validation(value)

    @cases([
        '01.01.2001', '31.12.9999', '01.01.0001', '07.07.2017'
    ])
    def test_valid_date_field(self, value):
        date_field = application_logic.DateField(nullable=True)
        try:
            date_field.validation(value)
        except application_logic.ValidationError:
            self.fail()

    @cases([
        '01.01.1905', '01.01.2105',
        datetime.datetime.today().replace(year=datetime.datetime.today().year - 71).strftime('%d.%m.%Y'),
        (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%d.%m.%Y'),
    ])
    def test_invalid_birthday_field(self, value):
        birthday_field = application_logic.BirthDayField(nullable=True)
        with self.assertRaises(application_logic.ValidationError):
            birthday_field.validation(value)

    @cases([
        '01.01.2018',
        datetime.datetime.today().replace(year=datetime.datetime.today().year - 69).strftime('%d.%m.%Y'),
        (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%d.%m.%Y'),
    ])
    def test_valid_birthday_field(self, value):
        birthday_field = application_logic.BirthDayField(nullable=True)
        try:
            birthday_field.validation(value)
        except application_logic.ValidationError:
            self.fail()

    @cases([
        -1, b'', [], {}, 3, '0', '1', '2'
    ])
    def test_invalid_gender_field(self, value):
        gender_field = application_logic.GenderField(nullable=True)
        with self.assertRaises(application_logic.ValidationError):
            gender_field.validation(value)

    @cases([
        0, 1, 2
    ])
    def test_valid_gender_field(self, value):
        gender_field = application_logic.GenderField(nullable=True)
        try:
            gender_field.validation(value)
        except application_logic.ValidationError:
            self.fail()

    @cases([
        -1, 0, b'', {}, '', '[]',
        [1, 2, '3'], [1, 2, 3.5], [1, 2, []]
    ])
    def test_invalid_client_ids_field(self, value):
        client_ids_field = application_logic.ClientIDsField(nullable=True)
        with self.assertRaises(application_logic.ValidationError):
            client_ids_field.validation(value)

    @cases([
        [], [0], [1, 2, 3], [-1, -2, -3]
    ])
    def test_valid_client_ids_field(self, value):
        client_ids_field = application_logic.ClientIDsField(nullable=True)
        try:
            client_ids_field.validation(value)
        except application_logic.ValidationError:
            self.fail()


if __name__ == "__main__":
    unittest.main()

