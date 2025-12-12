#!/usr/bin/env python
# -*- coding = utf-8 -*-
# filename: async_utils.py

"""
FastDFS客户端异步工具模块

该模块提供了基于asyncio的异步工具函数和类，用于处理文件操作、配置解析等任务。
相比于同步版本，异步版本能够提供更好的并发性能，特别适合高I/O密集型场景。

主要特性：
- 异步文件I/O操作
- 异步配置文件解析
- 异步文件检查和元数据获取
- 完整的错误处理和异常管理
- 支持并发批量操作

使用示例：
```python
import asyncio
from util.async_utils import AsyncFdfsConfigParser, async_fdfs_check_file

async def example():
    # 异步检查文件
    is_valid, error_msg = await async_fdfs_check_file('/path/to/file.txt')

    # 异步读取配置
    parser = AsyncFdfsConfigParser()
    await parser.read('/path/to/config.conf')
    value = parser.get('section', 'key')

    # 批量检查文件
    files = ['file1.txt', 'file2.txt', 'file3.txt']
    results = await async_fdfs_check_files_batch(files)
```
"""

import asyncio
import configparser
import logging
import os
import platform
import re
import stat
from typing import List, Tuple, Optional, Union, Dict, Any

import aiofiles

# 配置日志
logger = logging.getLogger(__name__)

# 常量定义
SUFFIX = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
__os_sep__ = "/" if platform.system() == 'Windows' else os.sep


def appromix(size: int, base: int = 0) -> str:
    """
    将字节流大小转换为人类可读格式

    这是一个纯计算函数，不需要异步处理。保持与原版本相同的实现。

    Args:
        size: 字节流大小，必须为非负整数
        base: 后缀索引，默认为0
    Returns:
        str: 人类可读的大小字符串，如 "1.5MB"
    Raises:
        ValueError: 当size为负数或数值过大时抛出
    """
    multiples = 1024
    if size < 0:
        raise ValueError('[-] Error: number must be non-negative.')
    if size < multiples:
        return '{0:d}{1}'.format(size, SUFFIX[base])
    for suffix in SUFFIX[base:]:
        if size < multiples:
            return '{0:.2f}{1}'.format(size, suffix)
        size = size / float(multiples)
    raise ValueError('[-] Error: number too big.')


def get_file_ext_name(filename: str, double_ext: bool = True) -> str:
    """
    获取文件扩展名

    这是一个纯字符串操作函数，不需要异步处理。保持与原版本相同的实现。

    Args:
        filename: 文件名
        double_ext: 是否支持双扩展名（如.tar.gz），默认为True
    Returns:
        str: 文件扩展名，如果没有扩展名则返回空字符串
    """
    li = filename.split(os.extsep)
    if len(li) <= 1:
        return ''
    else:
        if not _is_ext_name(li[-1]):
            return ''
    if double_ext:
        if len(li) > 2:
            if li[-2].find(__os_sep__) == -1:
                ext_name = '%s.%s' % (li[-2], li[-1])
                if _is_ext_name(ext_name):
                    return ext_name
    return li[-1]

def _is_ext_name(ext_name) -> bool:
    return ext_name and ext_name.isascii() and re.match(r"^[a-z0-9]{1,6}$", ext_name)

def split_remote_fileid(remote_file_id: str) -> Optional[Tuple[str, str]]:
    """
    分割远程文件ID为组名和远程文件名

    这是一个纯字符串操作函数，不需要异步处理。保持与原版本相同的实现。

    Args:
        remote_file_id: 远程文件ID字符串，格式为 "group_name/remote_file_name"
    Returns:
        Optional[Tuple[str, str]]: 如果分割成功返回(组名, 远程文件名)元组，否则返回None
    """
    index = remote_file_id.find('/')
    if -1 == index:
        return None
    return (remote_file_id[0:index], remote_file_id[(index + 1):])


class AsyncFileOperationError(Exception):
    """异步文件操作异常类"""
    pass

async def async_fdfs_check_file(filename: str) -> Tuple[bool, str]:
    """
    异步检查文件的有效性

    使用异步文件系统操作检查指定文件是否存在、是否为常规文件。
    相比于同步版本，该函数不会阻塞事件循环，适合在高并发环境中使用。

    Args:
        filename: 要检查的文件路径
    Returns:
        Tuple[bool, str]: 返回元组 (是否有效, 错误信息)
        - 如果文件有效，返回 (True, '')
        - 如果文件无效，返回 (False, 错误描述)

    Raises:
        AsyncFileOperationError: 当文件系统操作失败时抛出

    Example:
        ```python
        is_valid, error_msg = await async_fdfs_check_file('/path/to/file.txt')
        if is_valid:
            print("文件有效")
        else:
            print(f"文件无效: {error_msg}")
        ```
    """
    try:
        logger.debug(f"开始异步检查文件: {filename}")

        # 使用aiofiles进行异步文件系统操作
        file_exists = await asyncio.to_thread(os.path.isfile, filename)

        if not file_exists:
            error_msg = f'[-] Error: {filename} is not a file.'
            logger.warning(error_msg)
            return (False, error_msg)

        # 异步获取文件状态信息
        file_stat = await asyncio.to_thread(os.stat, filename)

        if not stat.S_ISREG(file_stat.st_mode):
            error_msg = f'[-] Error: {filename} is not a regular file.'
            logger.warning(error_msg)
            return (False, error_msg)

        logger.debug(f"文件检查成功: {filename}")
        return (True, '')

    except (OSError, IOError) as e:
        error_msg = f'[-] Error: Failed to check file {filename}: {e}'
        logger.error(error_msg)
        raise AsyncFileOperationError(error_msg)
    except Exception as e:
        error_msg = f'[-] Error: Unexpected error checking file {filename}: {e}'
        logger.error(error_msg)
        raise AsyncFileOperationError(error_msg)


async def async_fdfs_check_files_batch(filenames: List[str]) -> List[Tuple[str, bool, str]]:
    """
    批量异步检查多个文件的有效性

    并发检查多个文件的有效性，相比逐个检查能够显著提高性能。
    每个文件检查都是独立的，一个文件的失败不会影响其他文件。

    Args:
        filenames: 要检查的文件路径列表
    Returns:
        List[Tuple[str, bool, str]]: 返回结果列表，每个元素为 (文件名, 是否有效, 错误信息)

    Example:
        ```python
        files = ['file1.txt', 'file2.txt', 'file3.txt']
        results = await async_fdfs_check_files_batch(files)
        for filename, is_valid, error_msg in results:
            if is_valid:
                print(f"{filename}: 有效")
            else:
                print(f"{filename}: 无效 - {error_msg}")
        ```
    """
    logger.debug(f"开始批量检查 {len(filenames)} 个文件")

    # 创建并发任务
    tasks = []
    for filename in filenames:
        task = asyncio.create_task(
            async_fdfs_check_file(filename),
            name=f"check_file_{filename}"
        )
        tasks.append((filename, task))

    # 等待所有任务完成
    results = []
    for filename, task in tasks:
        try:
            is_valid, error_msg = await task
            results.append((filename, is_valid, error_msg))
        except AsyncFileOperationError as e:
            logger.error(f"批量检查文件 {filename} 失败: {e}")
            results.append((filename, False, str(e)))
        except Exception as e:
            logger.error(f"批量检查文件 {filename} 发生意外错误: {e}")
            results.append((filename, False, f"Unexpected error: {e}"))

    logger.debug(f"批量文件检查完成，共检查 {len(results)} 个文件")
    return results


async def async_get_file_size(filename: str) -> int:
    """
    异步获取文件大小

    使用异步文件系统操作获取指定文件的大小。

    Args:
        filename: 文件路径
    Returns:
        int: 文件大小（字节数）
    Raises:
        AsyncFileOperationError: 当文件操作失败时抛出

    Example:
        ```python
        size = await async_get_file_size('/path/to/file.txt')
        print(f"文件大小: {appromix(size)}")
        ```
    """
    try:
        logger.debug(f"异步获取文件大小: {filename}")

        # 异步获取文件状态
        file_stat = await asyncio.to_thread(os.stat, filename)
        size = file_stat.st_size

        logger.debug(f"文件 {filename} 大小: {size} 字节")
        return size

    except (OSError, IOError) as e:
        error_msg = f'[-] Error: Failed to get size of {filename}: {e}'
        logger.error(error_msg)
        raise AsyncFileOperationError(error_msg)


async def async_file_exists(filename: str) -> bool:
    """
    异步检查文件是否存在

    Args:
        filename: 文件路径
    Returns:
        bool: 如果文件存在返回True，否则返回False

    Example:
        ```python
        if await async_file_exists('/path/to/file.txt'):
            print("文件存在")
        else:
            print("文件不存在")
        ```
    """
    try:
        logger.debug(f"异步检查文件是否存在: {filename}")
        exists = await asyncio.to_thread(os.path.exists, filename)
        logger.debug(f"文件 {filename} 存在性: {exists}")
        return exists
    except Exception as e:
        logger.error(f"检查文件存在性时发生错误 {filename}: {e}")
        return False


async def async_read_file_content(filename: str, encoding: str = 'utf-8') -> str:
    """
    异步读取文件内容

    使用aiofiles库异步读取文件的全部内容。

    Args:
        filename: 文件路径
        encoding: 文件编码，默认为utf-8
    Returns:
        str: 文件内容
    Raises:
        AsyncFileOperationError: 当文件读取失败时抛出

    Example:
        ```python
        content = await async_read_file_content('/path/to/config.txt')
        print(content)
        ```
    """
    try:
        logger.debug(f"异步读取文件内容: {filename}")

        async with aiofiles.open(filename, 'r', encoding=encoding) as file:
            content = await file.read()

        logger.debug(f"成功读取文件 {filename}，内容长度: {len(content)} 字符")
        return content

    except (OSError, IOError) as e:
        error_msg = f'[-] Error: Failed to read file {filename}: {e}'
        logger.error(error_msg)
        raise AsyncFileOperationError(error_msg)


async def async_write_file_content(filename: str, content: str, encoding: str = 'utf-8') -> None:
    """
    异步写入文件内容

    使用aiofiles库异步写入内容到文件。

    Args:
        filename: 文件路径
        content: 要写入的内容
        encoding: 文件编码，默认为utf-8
    Raises:
        AsyncFileOperationError: 当文件写入失败时抛出

    Example:
        ```python
        await async_write_file_content('/path/to/output.txt', 'Hello, World!')
        ```
    """
    try:
        logger.debug(f"异步写入文件内容: {filename}")

        # 确保目录存在
        directory = os.path.dirname(filename)
        if directory and not await async_file_exists(directory):
            await asyncio.to_thread(os.makedirs, directory, exist_ok=True)

        async with aiofiles.open(filename, 'w', encoding=encoding) as file:
            await file.write(content)

        logger.debug(f"成功写入文件 {filename}，内容长度: {len(content)} 字符")

    except (OSError, IOError) as e:
        error_msg = f'[-] Error: Failed to write file {filename}: {e}'
        logger.error(error_msg)
        raise AsyncFileOperationError(error_msg)
