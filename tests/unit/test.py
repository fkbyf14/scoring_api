import unittest
from tests import cases
from scoring import api, application_logic


class TestCharField(unittest.TestCase):
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


class TestNameField(unittest.TestCase):
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


class TestArgumentsField(unittest.TestCase):
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


class TestPhoneAndEmailField(unittest.TestCase):
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


class TestBirthdayAndGenderField(unittest.TestCase):
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


class TestDateField(unittest.TestCase):
    @cases([
        {"client_ids": [1], "date": "2017.07.07"},
        {"client_ids": [1], "date": "-07.07.2017"},
        {"client_ids": [1], "date": "08.O8.2018"}
    ])
    def test_bad_date_field(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))


class TestClientsIdsField(unittest.TestCase):
    @cases([
        {"client_ids": 1, "date": "07.07.2017"},
        {"client_ids": ["a", "b"], "date": "07.07.2017"},
        {"client_ids": [], "date": "07.07.2017"},
        {"client_ids": "a", "date": "07.07.2017"}
    ])
    def test_bad_client_ids_field(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))


if __name__ == "__main__":
    unittest.main()
    #suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestNameField)
    #unittest.TextTestRunner().run(suite)
