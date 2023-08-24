import threading


def threading_wrapper(func):
    def _wrapper(self, *arg, **kwargs):
        threading.Thread(target=func, args=(self, *arg), kwargs=kwargs).start()

    return _wrapper
