import os
import shutil


def check_path_exists(path):
    """
    检查文件或者路径是否存在
    :param path:
    :return:
    """
    if os.path.exists(path):
        return True
    else:
        return False


def delete_path(path):
    """
    删除文件或者文件夹(文件夹中的内容也会被清除)
    :param path:
    :return:
    """
    if os.path.isfile(path):
        os.remove(path)  # 删除文件
    elif os.path.isdir(path):
        shutil.rmtree(path)  # 递归删除非空文件夹


def create_dir(path):
    """
    如果指定的路径不存在，则创建路径
    :param path:
    :return:
    """
    os.makedirs(path, exist_ok=True)


def clear_dir(path):
    """
    删除指定目录的所有内容但保留该目录
    :param path: 
    :return: 
    """
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            clear_dir(file_path)  # 递归删除子目录中的内容
            os.rmdir(file_path)


if __name__ == '__main__':
    directory_path = "data/synthesize/dag_temp_data"

    # 调用函数清空指定目录的内容
    if check_path_exists(directory_path):
        clear_dir(directory_path)
    else:
        print("指定的路径不存在")
