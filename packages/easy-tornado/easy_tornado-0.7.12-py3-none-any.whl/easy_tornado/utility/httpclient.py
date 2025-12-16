# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:25
from __future__ import print_function

from .datetime import Timer
from .printext import it_print
from .printext import json_print
from .printext import print_json
from .printext import print_prefix
from .webext import request


class HttpTest(object):
  """
  Http API测试工具
  """
  debug = True

  def __init__(self, url=None):
    self.url = url
    self.timer = None

  def set_url(self, host, context, port=80, https=False):
    schema = 'https' if https else 'http'
    self.url = '{}://{}:{}{}'.format(schema, host, port, context)

  def request_url(self, url, data=None, as_json=True, timeout=None):
    # 请求地址
    request_url = url
    if self.debug:
      print_prefix(request_url, "url:")

    # 请求数据
    if data is None:
      data = {}

    if self.debug:
      # 起始时间
      self.timer = Timer()
      self.timer.display_start("request at: ")

      # 打印请求数据
      it_print("request:")
      if len(data) != 0:
        json_print(data)

    # 发起请求
    res = request(request_url, data, as_json, timeout)

    if self.debug:
      self.timer.finish()
      # 打印结果
      it_print("response:")
      if res is not None:
        print_json(res)
      else:
        it_print()

      # 结束时间
      self.timer.display_finish("finished at: ")
      it_print("time cost: {} s".format(self.timer.cost()))

      it_print()
    return res

  def request(self, uri, data=None, as_json=True, timeout=None):
    return self.request_url('{}{}'.format(self.url, uri), data, as_json, timeout)
