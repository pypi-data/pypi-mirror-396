# -*- coding: utf-8 -*-
# author: 王树根
# email: wsg1107556314@163.com
# date: 2025/08/27 23:19
import sys

from .. import deprecated
from ..utility import from_json
from ..utility import is_json_map


def get_or_default(sample, key, default):
  """
  获取数据源中键对应的值
  :param sample: 数据源
  :param key: 键名
  :param default: 默认值
  :return: 获取成功返回对象值, 否则返回默认值
  """
  if '.' not in key:
    return get_with_try_index(sample, key, default)
  pieces = key.split('.')
  for i, piece in enumerate(pieces):
    sample = get_with_try_index(sample, piece, default)
    if i < len(pieces) - 1:
      if isinstance(sample, str) and is_json_map(sample):
        sample = from_json(sample)
  return sample


def get_with_try_index(sample, key, default):
  """
  获取数据源中键对应的值: 支持索引下标数据
  :param sample: 数据源
  :param key: 键名
  :param default: 默认值
  :return: 获取成功返回对象值, 否则返回默认值
  """
  if key in sample:
    return sample[key]
  if '[' in key and ']' in key:
    pos_s, pose_e = key.index('['), key.index(']')
    index = int(key[pos_s + 1:pose_e])
    values = sample[key[:pos_s]]
    if index < len(values):
      return values[index]
  return default


def read_stdin_contents(buffer=None, strip=True, fn=None):
  """
  从标准输入读取: 空行表示数据结束
  :param buffer: 若传入buffer不为空,则填充
  :param strip: 是否对每行进行strip操作
  :param fn: 行处理函数
  :return: 返回行列表或经fn处理后的结果列表
  """
  if buffer is None:
    buffer = []
  for line in sys.stdin:
    if strip:
      line = line.strip()
    if fn is not None:
      line = fn(line)
    if not line:
      break
    buffer.append(line)
  return buffer


@deprecated(new_fn=read_stdin_contents, version='0.8')
def read_from_stdin(*args, **kwargs):
  return read_stdin_contents(*args, **kwargs)
