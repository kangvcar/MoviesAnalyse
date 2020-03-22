#!/usr/bin/python
# coding=utf-8

import os
if not os.path.exists('comment_data'):
    os.mkdir('comment_data')
    print("成功创建文件夹comment_data")
    target_dir = os.path.join('comment_data', '我不是药神.txt')
    print(target_dir)
else:
    print("comment_data文件已存在")
    target_dir = os.path.join('comment_data', '我不是药神.txt')
    print(target_dir)

with open(target_dir, 'w', encoding='utf-8') as f:
    f.write("测试测试...")