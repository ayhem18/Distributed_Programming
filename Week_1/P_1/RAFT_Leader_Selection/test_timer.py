import random
import threading
import time


class RepeatedTimer(object):
    def __init__(self, interval, function, stop_function=None,  *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.stop_function = stop_function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        return_value = self.function(*self.args, **self.kwargs)
        print("Return values from the self.function")
        print(return_value)
        # checking if the self.stop_function is set and if the return value should stop the object from running
        if self.stop_function and self.stop_function(return_value):
            self.stop()

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            # self._timer.join()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def f():
    num = random.random()
    print(num)
    return num < 0.9


def negate(value):
    if isinstance(value, bool):
        return not value
    return False


if __name__ == "__main__":
    # n = 5
    rep = RepeatedTimer(1, f, negate)
    rep.start()