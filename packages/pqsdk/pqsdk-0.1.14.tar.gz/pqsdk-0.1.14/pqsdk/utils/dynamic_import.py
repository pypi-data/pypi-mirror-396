import importlib
import importlib.util
import six


def check_module(module_name: str):
    """
    Checks if module can be imported without actually
    importing it
    """

    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        print("Module: {} not found".format(module_name))
        return None
    else:
        return module_spec


def import_module(module_name: str):
    """
    动态导入模块

    :param file_path: 模块文件路径，i.e. strats/strat_demo.py 或者 strats\\strat_demo.py
    :return:
    """
    return importlib.import_module(module_name)


def import_module_from_file(file_path: str):
    """
    动态导入模块

    :param file_path: 模块文件路径，i.e. strats/strat_demo.py 或者 strats\\strat_demo.py
    :return:
    """
    module_name = file_path[:-3]
    module_name = module_name.replace('/', '.').replace('\\', '.')
    return importlib.import_module(module_name)


def check_module_from_file(file_path: str):
    """
    Checks if module can be imported without actually
    importing it
    """
    module_name = file_path[:-3]
    module_name = module_name.replace('/', '.').replace('\\', '.')

    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        print("Module: {} not found".format(module_name))
        return None
    else:
        return module_spec


def import_module_from_spec(module_spec):
    """
    Import the module via the passed in module specification
    Returns the newly imported module
    """
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def import_module_from_code(code: str, kwargs: dict = None):
    """
    从字符串的代码中导入模块
    :param kwargs: 传入策略代码的相关信息
    :param code: 字符串代码
    :return: 代码模块
    """
    if kwargs is not None and 'origin' in kwargs:
        origin = kwargs['origin']
    else:
        origin = 'strategy.py'

    # 从字符串中创建一个ModuleSpec对象
    obj_spec = importlib.util.spec_from_loader('obj_spec',
                                               loader=None,
                                               origin=origin,
                                               is_package=False)
    # 创建一个新模块对象
    obj = importlib.util.module_from_spec(obj_spec)
    # 将Python代码作为字符串传递给exec()函数来执行它
    six.exec_(code, obj.__dict__)
    # 执行新模块中的函数或变量
    return obj


if __name__ == '__main__':
    # case 1: fake module
    file_path = 'strats/hello_world.py'
    module_spec = check_module_from_file(file_path)
    if not module_spec:
        print("fake module: {}".format(file_path))

    # case 2: true module, check before imported
    file_path = 'strats/new_strat_demo.py'
    module_spec = check_module_from_file(file_path=file_path)
    if module_spec:
        strategy = import_module_from_spec(module_spec=module_spec)
        strategy.handle_bar(None)

    # case 3: import module directly
    file_path = 'strats/new_strat_demo.py'
    strategy = import_module_from_file(file_path)
    if hasattr(strategy, 'before_trading_start'):
        print("has before_trading_start")
    strategy.handle_bar(None)

    code = """
import pandas as pd
def initialize():
    print("I'm in Init! imported from code")
"""
    strat = import_module_from_code(code=code)
    strat.initialize()
