from threading import Thread


def async_run(f):
    """
    异步执行修饰器，通过如下方式让函数非阻塞异步执行

    @async_run
    def func():
        print("run async!")

    :param f:
    :return:
    """
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()

    return wrapper
