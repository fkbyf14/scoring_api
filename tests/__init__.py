import functools
import unittest


def cases(case_vectors):
    def decorator(test_func):
        @functools.wraps(test_func)
        def wrapper(*args):
            test_case = args[0]  # self
            print "hello from wrapper:", args
            assert isinstance(test_case, unittest.TestCase)
            for case in case_vectors:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                with test_case.subTest(msg=repr(case)):
                    test_func(*new_args)
        return wrapper
    return decorator
