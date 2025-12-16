import builtins


def import_modules(parent_module):
    """
    把parent_module中定义的所有子模块全部导入到全局变量中。

    :param parent_module:
    :return:
    """
    for name in dir(parent_module):
        if not name.startswith('__'):
            func = getattr(parent_module, name)
            setattr(builtins, name, func)
