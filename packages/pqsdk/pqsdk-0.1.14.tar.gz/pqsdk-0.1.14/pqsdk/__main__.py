# coding=utf-8
import argparse
import sys
from .main import run_backtest
from pqsdk.utils.value_type_util import convert_to_type
import requests
import getpass
import pqsdk.utils.file_util as fu
import json
from .logger import log
import logging

log.set_level(logging.INFO)


def input_with_default(prompt, default):
    user_input = input(prompt)
    return user_input if user_input else default


def handle_config_command():
    # 提示用户输入用户名
    username = input("请输入用户名: ")
    if not username:
        print("用户名不能为空！")
        return

        # 提示用户输入密码
    password = getpass.getpass("请输入密码: ")
    if not password:
        print("密码不能为空！")
        return

    host = 'api.pinkquant.com'

    # 获取Tenant list
    url = f"http://{host}/api/admin/tenant/login/tenants?username={username}"
    response = requests.get(url)
    tenants = response.json()['data']

    if len(tenants) == 0:
        print(f"用户 {username} 未找到有效的协作空间, 请联系管理员")
        return

    if len(tenants) == 1:
        # 仅归属一个协作空间
        tenant_index = 0
    else:
        print(f"用户 {username} 归属于如下的协作空间: \n")
        for index, tenant in enumerate(tenants):
            print(f"{index}: ", tenant['enterpriseName'])

        tenant_index = input_with_default("\n请输入协作空间的编号(默认值为0): ", "0")

    selectedTenant = tenants[int(tenant_index)]
    tenant_id = selectedTenant['tenantCode']

    # 获取token
    url = f'http://{host}/api/auth/oauth2/token'
    params = {
        'grant_type': 'password',
        'tenantId': tenant_id
    }
    headers = {
        'Authorization': 'Basic YXBpLWNsaWVudDoxMjM0NTY=',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, params=params, headers=headers, data={"username": username, "password": password})
    result = response.json()
    if 'data' not in result:
        log.error(f"用户未分配正确权限，请联系管理员")
        return

    result = result['data']

    config_file = 'config.sdk.json'
    if fu.check_path_exists(config_file):
        # 更新配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            sdk_config = json.loads(f.read())
        sdk_config['token'] = result['access_token']
        sdk_config['audience'] = "api-client"
        sdk_config['host'] = host
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sdk_config, f)
        print("配件文件已经更新")
    else:
        # 创建配置文件
        data = {
            "host": host,
            "audience": "api-client",
            "token": result['access_token']
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        print("新的配置创建完成")

    # 检查响应状态码
    if response.status_code == 200:
        pass
    else:
        print(f"请求失败，状态码：{response.status_code}")


def handle_config_info_command():
    config_file = 'config.sdk.json'
    if fu.check_path_exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            sdk_config = json.loads(f.read())

        print("配置信息:")
        for k, v in sdk_config.items():
            print(f"    {k} = {v}")
    else:
        print("未找到配置文件. 请先运行命令进行配置: pqsdk config")


def main():
    parser = argparse.ArgumentParser(description='PQ SDK Command Line Interface')
    parser.add_argument('command', choices=['backtest', 'config'], help='The command to execute')
    parser.add_argument('subcommand', choices=['info'], nargs='?', help='The subcommand to execute (optional)')
    parser.add_argument('-f', dest='file', metavar='file path', help='回测脚本文件路径')
    parser.add_argument('--plot', action='store_true', help='是否绘图')
    parser.add_argument('--save_metrics', action='store_true', help='是否保存结果到csv文件')
    parser.add_argument('--save_orders', action='store_true', help='是否保存委托到csv文件')
    parser.add_argument('--save_inout_cash', action='store_true', help='是否保存出入金到csv文件')
    parser.add_argument('-p', dest='param', action='append', nargs=1, metavar='key=value',
                        help='自定义的参数, 格式: -p key=value, 等号之间不能有空格')

    args = parser.parse_args()

    # 将 -p 传递的参数转换为字典, args.param的原始格式：[['key1=value1'], ['key2=value2']]
    params = {}
    if args.param is not None:
        for kv in args.param:
            key, value = kv[0].replace(" ", "").split('=')
            params[key] = convert_to_type(value)

    if args.command == 'backtest':
        # 执行回测
        run_backtest(args.file, params, args.plot, args.save_metrics, args.save_orders, args.save_inout_cash)
    elif args.command == 'config':
        if args.subcommand == 'info':
            handle_config_info_command()
        else:
            handle_config_command()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
