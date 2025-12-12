# -*- coding: utf-8 -*-
import argparse
import sys

from dding.notify import notify_dding, notify_feishu


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--platform', default='dding', choices=['dding', 'feishu'], 
                      help='选择通知平台: dding(钉钉) 或 feishu(飞书)')
    parser.add_argument('--group', default='default')
    parser.add_argument('--content', default='')
    parser.add_argument('--title', default='')
    parser.add_argument('--msgtype', default='text')
    
    # 支持位置参数作为简化使用方式
    parser.add_argument('positional_args', nargs='*', help='位置参数: content 或 group content')
    
    args = parser.parse_args()

    # 处理位置参数
    if args.positional_args:
        if len(args.positional_args) == 1:
            # dding "hello" 形式
            args.content = args.positional_args[0]
            print(args.content)
        elif len(args.positional_args) == 2:
            # dding group "hello" 形式
            args.group = args.positional_args[0]
            args.content = args.positional_args[1]
    
    params = vars(args)
    # 移除位置参数，不传给通知函数
    params.pop('positional_args', None)
    platform = params.pop('platform')  # 取出platform参数

    # 根据平台选择调用不同的函数
    if platform == 'feishu':
        notify_feishu(**params)
    else:
        notify_dding(**params)


def usage():
    print("usage: dding [options] [content] [group content]")
    print("usage: dding --platform feishu --content hello --title hello --msgtype markdown")
    print("usage: dding --content hello --msgtype text  # 默认使用钉钉")
    print("usage: dding hello  # 简化用法，发送到默认组")
    print("usage: dding mygroup hello  # 简化用法，发送到指定组")
    print("example: dding helloworld")
    print("example: dding --platform feishu 'Hello Feishu!'")
    print("example: dding --platform dding 'Hello DingTalk!')")


def test1():
    content="### 杭州天气 \n> 1111"
    # content="### 杭州天气 \n 1111"

def test_feishu():
    notify_feishu(group='default', title='hello',content=sys.argv[1], msgtype='text')

if __name__ == '__main__':
    main()
    # test1()

