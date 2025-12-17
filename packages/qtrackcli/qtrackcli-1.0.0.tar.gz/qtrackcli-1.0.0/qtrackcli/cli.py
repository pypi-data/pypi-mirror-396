# qtrackcli/cli.py
import argparse
import requests
import os
import sys
import base64


def upload_junit_report(args):
    """Upload JUnit XML report to the service"""
    # 构造完整的URL路径
    url = f"{args.host.rstrip('/')}/pytest_xml_automation"

    # 准备认证头信息
    api_token= args.api_token
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {api_token}'
    }

    # 准备表单数据
    data = {
        'project_name': args.project_name,
        'run_name': args.run_name,
        'run_description': args.run_description or '',
        'xml_path': args.xml_path,
        'email': args.email
    }

    # 检查文件是否存在
    if not os.path.exists(args.xml_path):
        print(f"Error: File '{args.xml_path}' does not exist")
        sys.exit(1)

    try:
        # 发送POST请求
        print('headers', headers)
        print("data", data)
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("Report uploaded successfully")
        if response.text:
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error uploading report: {e}")
        sys.exit(1)


def main():
    # 创建主解析器
    parser = argparse.ArgumentParser(description='QTrack CLI tool for uploading JUnit XML report to q-track')
    parser.add_argument('-y', '--yes', action='store_true', help='Automatic yes to prompts')
    parser.add_argument('--host', required=True, help='Host URL')
    parser.add_argument('-u', '--email', required=True, help='User email')
    parser.add_argument('-p', '--api_token', required=True, help='API token')
    parser.add_argument('--project_name', required=True, help='Project name')

    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 解析JUnit报告的子命令
    parse_junit_parser = subparsers.add_parser('parse_junit', help='Parse and upload JUnit XML report')
    parse_junit_parser.add_argument('--run_name', required=True, help='Test run name')
    parse_junit_parser.add_argument('--run_description', help='Test run description')
    parse_junit_parser.add_argument('-f', '--xml_path', required=True, help='Path to JUnit XML file')
    parse_junit_parser.set_defaults(func=upload_junit_report)

    # 解析参数
    args = parser.parse_args()

    # 执行对应的功能
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
