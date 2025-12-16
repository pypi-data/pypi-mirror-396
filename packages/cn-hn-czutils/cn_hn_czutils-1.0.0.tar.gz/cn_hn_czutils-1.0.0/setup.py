#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#setup.py 用来描述包的基本信息：用户信息，作者


from setuptools import setup, find_packages


def get_long_description():
    with open('README.rst','r',encoding='UTF8') as readme:
        return readme.read()

setup(
    name="cn_hn_czutils",
    version="1.0.0",
    author="caozz",
    author_email="caozz1119@163.com",
    description="CZ-Utils工具库",
    long_description= get_long_description(),
    #项目主页地址
    url="http://www.sheungee.com.cn/",
    #协议 ,如果新建了LICENSE.txt就不需要使用下面的license
    # 使用LICENSE.txt或者license='MIT'两种方式都可以
    # license='MIT',
    #项目目录下有多个包，packages就是告诉打包工具，把哪些包打包到版本中
    packages=find_packages(),
    #需要导出的当个文件
    py_modules=['Utils'],
    # packages=['stringutil','timeutil'],
    # 安装过程中，需要安装的静态文件，如配置文件、service文件、图片等
    # data_files=[
    #     ('', ['conf/*.conf']),
    #     ('/usr/lib/systemd/system/', ['bin/*.service']),
    #            ],
    # 希望被打包的文件
    # package_data={
    #     '':['*.txt'],
    #     'bandwidth_reporter':['*.txt']
    # },
    # 不打包某些文件
    # exclude_package_data={
    #     'bandwidth_reporter':['*.txt']
    # },
    #install_requires 参数来指定项目的依赖项
    # install_requires=[
    #     'requests>=2.25.1'
    # ]
)