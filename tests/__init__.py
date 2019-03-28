import functools


def cases(case_vectors):
    def decorator(test_func):
        @functools.wraps(test_func)
        def inner(self, *args):
            for case in case_vectors:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                try:
                    test_func(self, *new_args)
                except Exception as e:
                    msg = "TEST args: %s" % (new_args,)
                    e.args += (msg,)
                    pass
        return inner
    return decorator
