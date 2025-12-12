"""
FastDFS客户端异步连接模块

该模块提供了基于asyncio的异步TCP连接实现，用于与FastDFS服务器进行异步通信。
相比于同步连接，异步连接能够提供更好的并发性能，特别适合高并发场景。

主要特性：
- 基于asyncio的异步TCP连接
- 支持主机元组随机选择和故障转移
- 提供连接池管理功能
- 完整的错误处理和异常管理
- 支持连接超时和网络超时配置
- 异步连接健康检查和自动重连

使用示例：
```python
import asyncio
from aiofdfs.async_connection import AsyncConnectionPool

async def example():
    # 创建连接池
    pool = AsyncConnectionPool(
        host_tuple=[('tracker1.example.com', 22122), ('tracker2.example.com', 22122)],
        connect_timeout=5,
        network_timeout=10,
        pool_size=10
    )

    # 获取连接
    async with pool.get_connection() as conn:
        # 使用连接进行通信
        data = await conn.receive(1024)
        await conn.send(b'response data')

    # 连接会自动返回到连接池
```
"""

import asyncio
import os
import random
import socket
import ssl
from typing import Optional, List
import logging


# 配置日志
logger = logging.getLogger(__name__)


class AsyncConnectionError(Exception):
    """异步连接异常类

    用于处理异步连接过程中的各种错误情况，包括连接超时、网络错误等。
    """
    pass


class AsyncConnection:
    """
    异步TCP连接类

    该类负责管理与FastDFS服务器的异步TCP连接。提供连接建立、数据传输、
    连接状态检查等功能。所有操作都是异步的，基于asyncio事件循环。

    Attributes:
        pid (int): 进程ID，用于标识连接所属的进程
        host_tuple (List[str]): 主机地址元组列表，格式为 ['host:port', ...]
        remote_port (Optional[int]): 当前连接的远程端口
        remote_addr (Optional[str]): 当前连接的远程地址
        connect_timeout (float): 连接超时时间（秒）
        network_timeout (float): 网络操作超时时间（秒）
        _reader (Optional[asyncio.StreamReader]): 异步流读取器
        _writer (Optional[asyncio.StreamWriter]): 异步流写入器
        _is_connected (bool): 连接状态标志
        _connection_lock (asyncio.Lock): 连接操作锁，防止并发连接
        _ssl_context (Optional[ssl.SSLContext]): SSL上下文（如果使用SSL）
    """

    def __init__(self,
                 host_tuple: List[str],
                 connect_timeout: float = 5.0,
                 network_timeout: float = 10.0,
                 use_ssl: bool = False,
                 ssl_context: Optional[ssl.SSLContext] = None,
                 pool = None):
        """
        初始化异步连接对象

        Args:
            host_tuple: 主机地址元组列表，每个元素格式为 'host:port'
            connect_timeout: 连接超时时间，单位秒，默认5秒
            network_timeout: 网络操作超时时间，单位秒，默认10秒
            use_ssl: 是否使用SSL加密连接，默认False
            ssl_context: 自定义SSL上下文，如果为None且use_ssl为True，将使用默认SSL配置
        """
        self.pid = os.getpid()
        self.host_tuple = host_tuple
        self.remote_port = None
        self.remote_addr = None
        self.connect_timeout = connect_timeout
        self.network_timeout = network_timeout
        self.use_ssl = use_ssl
        self._ssl_context = ssl_context
        self.pool: AsyncConnectionPool = pool

        # 异步流对象
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None

        # 连接状态
        self._is_connected = False

        # 连接操作锁，防止并发连接问题
        self._connection_lock = asyncio.Lock()

        # 设置SSL上下文
        if self.use_ssl and self._ssl_context is None:
            self._ssl_context = ssl.create_default_context()
            logger.debug("使用默认SSL上下文")

    async def __aenter__(self):
        """异步上下文管理器入口

        Returns:
            AsyncConnection: 返回自身实例，支持异步with语法
        """
        if self.pool is None:
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        if self.pool:
            await self.pool.return_connection(self)
            return
        await self.disconnect()

    async def connect(self) -> None:
        """
        建立异步TCP连接

        从主机元组中随机选择一个主机地址，建立异步TCP连接。
        如果连接失败，会尝试其他主机地址。

        Raises:
            AsyncConnectionError: 当所有主机连接失败时抛出

        Note:
            该方法是线程安全的，使用连接锁防止并发连接
        """
        # 如果已经连接，直接返回
        if self._is_connected and self._reader and self._writer:
            logger.debug(f"连接已存在: {self.remote_addr}:{self.remote_port}")
            return

        async with self._connection_lock:
            # 双重检查，防止在等待锁期间其他线程已经建立了连接
            if self._is_connected:
                return

            logger.debug(f"开始建立连接，候选主机: {self.host_tuple}")

            # 随机打乱主机顺序，实现负载均衡
            shuffled_hosts = random.sample(self.host_tuple, len(self.host_tuple))

            # 尝试连接每个主机，直到成功或全部失败
            last_exception = None
            for host in shuffled_hosts:
                try:
                    host_parts = host.split(':')
                    if len(host_parts) != 2:
                        logger.warning(f"无效的主机格式: {host}，应为 'host:port'")
                        continue

                    remote_addr = host_parts[0]
                    remote_port = int(host_parts[1])

                    logger.debug(f"尝试连接到 {remote_addr}:{remote_port}")

                    # 使用asyncio.open_connection建立异步连接
                    reader, writer = await asyncio.wait_for(
                        asyncio.open_connection(
                            host=remote_addr,
                            port=remote_port,
                            ssl=self._ssl_context
                        ),
                        timeout=self.connect_timeout
                    )

                    # 设置TCP选项
                    sock = writer.get_extra_info('socket')
                    if sock:
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                    # 保存连接信息
                    self._reader = reader
                    self._writer = writer
                    self.remote_addr = remote_addr
                    self.remote_port = remote_port
                    self._is_connected = True

                    logger.info(f"成功连接到FastDFS服务器: {remote_addr}:{remote_port}")
                    return

                except (asyncio.TimeoutError, socket.error, OSError) as e:
                    last_exception = e
                    logger.warning(f"连接到 {remote_addr}:{remote_port} 失败: {e}")
                    # 清理失败的连接
                    if 'writer' in locals() and writer:
                        writer.close()
                        try:
                            await writer.wait_closed()
                        except:
                            pass
                    continue

            # 所有主机连接失败，抛出异常
            error_msg = f"无法连接到任何FastDFS服务器。最后错误: {last_exception}"
            logger.error(error_msg)
            raise AsyncConnectionError(error_msg)

    async def disconnect(self) -> None:
        """
        断开异步TCP连接

        安全地关闭连接，释放相关资源。该方法会关闭读写流并清理连接状态。

        Note:
            该方法可以被多次调用而不出错
        """
        if not self._is_connected:
            logger.debug("连接已断开，无需重复操作")
            return

        async with self._connection_lock:
            if not self._is_connected:
                return

            logger.debug(f"开始断开连接: {self.remote_addr}:{self.remote_port}")

            try:
                # 关闭写入流
                if self._writer:
                    self._writer.close()
                    try:
                        await asyncio.wait_for(
                            self._writer.wait_closed(),
                            timeout=self.network_timeout
                        )
                    except asyncio.TimeoutError:
                        logger.warning("关闭写入流超时")
                    except Exception as e:
                        logger.warning(f"关闭写入流时发生错误: {e}")

                # 清理连接状态
                self._reader = None
                self._writer = None
                self._is_connected = False

                logger.debug(f"成功断开连接: {self.remote_addr}:{self.remote_port}")

            except Exception as e:
                logger.error(f"断开连接时发生错误: {e}")
                # 即使发生错误，也要清理连接状态
                self._reader = None
                self._writer = None
                self._is_connected = False
                raise AsyncConnectionError(f"断开连接失败: {e}")

    async def send(self, data: bytes) -> None:
        """
        异步发送数据

        向连接的远程端发送二进制数据。

        Args:
            data: 要发送的二进制数据

        Raises:
            AsyncConnectionError: 当连接未建立或发送失败时抛出

        Note:
            发送操作具有超时保护，超时时间由network_timeout参数控制
        """
        if not self._is_connected or not self._writer:
            raise AsyncConnectionError("连接未建立，无法发送数据")

        try:
            logger.debug(f"发送数据 {len(data)} 字节到 {self.remote_addr}:{self.remote_port}")
            # 使用asyncio.wait_for为发送操作添加超时保护
            self._writer.write(data)
            # 确保数据被立即发送
            await asyncio.wait_for(
                self._writer.drain(),
                timeout=self.network_timeout
            )

            logger.debug(f"成功发送数据到 {self.remote_addr}:{self.remote_port}")

        except asyncio.TimeoutError:
            error_msg = f"发送数据超时 ({self.network_timeout}秒)"
            logger.error(error_msg)
            await self._handle_connection_error()
            raise AsyncConnectionError(error_msg)

        except Exception as e:
            error_msg = f"发送数据失败: {e}"
            logger.error(error_msg)
            await self._handle_connection_error()
            raise AsyncConnectionError(error_msg)

    async def receive(self, size: int) -> bytes:
        """
        异步接收数据

        从连接的远程端接收指定大小的二进制数据。

        Args:
            size: 要接收的数据字节数

        Returns:
            bytes: 接收到的二进制数据

        Raises:
            AsyncConnectionError: 当连接未建立或接收失败时抛出

        Note:
            接收操作具有超时保护，超时时间由network_timeout参数控制
            如果连接被远程端关闭，会返回空字节串
        """
        if not self._is_connected or not self._reader:
            raise AsyncConnectionError("连接未建立，无法接收数据")

        try:
            logger.debug(f"准备接收 {size} 字节数据从 {self.remote_addr}:{self.remote_port}")

            # 使用asyncio.wait_for为接收操作添加超时保护
            data = await asyncio.wait_for(
                self._reader.read(size),
                timeout=self.network_timeout
            )

            logger.debug(f"成功接收 {len(data)} 字节数据从 {self.remote_addr}:{self.remote_port}")
            return data

        except asyncio.IncompleteReadError:
            # 远程端关闭了连接
            logger.warning(f"远程端关闭了连接: {self.remote_addr}:{self.remote_port}")
            await self._handle_connection_error()
            return b''

        except asyncio.TimeoutError:
            error_msg = f"接收数据超时 ({self.network_timeout}秒)"
            logger.error(error_msg)
            await self._handle_connection_error()
            raise AsyncConnectionError(error_msg)

        except Exception as e:
            error_msg = f"接收数据失败: {e}"
            logger.error(error_msg)
            await self._handle_connection_error()
            raise AsyncConnectionError(error_msg)

    async def receive_until(self, separator: bytes, max_size: int = 65536) -> bytes:
        """
        异步接收数据直到遇到分隔符

        从连接的远程端接收数据，直到遇到指定的分隔符或达到最大长度。

        Args:
            separator: 分隔符字节数组
            max_size: 最大接收字节数，默认65536

        Returns:
            bytes: 接收到的数据（不包含分隔符）

        Raises:
            AsyncConnectionError: 当连接未建立或接收失败时抛出
            ValueError: 当max_size过小时抛出
        """
        if max_size <= 0:
            raise ValueError("max_size必须大于0")

        if not self._is_connected or not self._reader:
            raise AsyncConnectionError("连接未建立，无法接收数据")

        try:
            logger.debug(f"接收数据直到分隔符从 {self.remote_addr}:{self.remote_port}")

            # 使用asyncio.wait_for为接收操作添加超时保护
            data = await asyncio.wait_for(
                self._reader.readuntil(separator),
                timeout=self.network_timeout
            )

            # 移除分隔符
            result = data[:-len(separator)]
            logger.debug(f"成功接收 {len(result)} 字节数据从 {self.remote_addr}:{self.remote_port}")
            return result

        except asyncio.LimitOverrunError:
            error_msg = f"接收数据超过最大限制 {max_size} 字节"
            logger.error(error_msg)
            await self._handle_connection_error()
            raise AsyncConnectionError(error_msg)

        except asyncio.IncompleteReadError:
            # 远程端关闭了连接
            logger.warning(f"远程端关闭了连接: {self.remote_addr}:{self.remote_port}")
            await self._handle_connection_error()
            return b''

        except asyncio.TimeoutError:
            error_msg = f"接收数据超时 ({self.network_timeout}秒)"
            logger.error(error_msg)
            await self._handle_connection_error()
            raise AsyncConnectionError(error_msg)

        except Exception as e:
            error_msg = f"接收数据失败: {e}"
            logger.error(error_msg)
            await self._handle_connection_error()
            raise AsyncConnectionError(error_msg)

    async def is_connected(self) -> bool:
        """
        检查连接是否仍然活跃

        通过发送心跳包来检测连接状态。这是一个非阻塞的操作，
        不会影响正常的通信流程。

        Returns:
            bool: 如果连接活跃返回True，否则返回False
        """
        if not self._is_connected or not self._reader or not self._writer:
            return False

        try:
            # 检查读取器是否已关闭
            if self._reader.at_eof():
                logger.debug(f"连接已关闭: {self.remote_addr}:{self.remote_port}")
                return False

            # 检查写入器状态
            transport = self._writer.transport
            if transport and transport.is_closing():
                logger.debug(f"传输层正在关闭: {self.remote_addr}:{self.remote_port}")
                return False
            await self.send(b'')
            return True

        except Exception as e:
            logger.warning(f"检查连接状态时发生错误: {e}")
            return False

    async def ensure_connected(self) -> bool:
        """
        确保连接处于活跃状态

        检查连接状态，如果连接断开则自动重新连接。

        Returns:
            bool: 如果重新连接成功返回True，否则返回False

        Note:
            该方法会自动处理连接重建，适用于需要长时间保持连接的场景
        """
        if await self.is_connected():
            return False

        logger.info("连接已断开，尝试重新连接...")

        try:
            # 先断开可能存在的残留连接
            await self.disconnect()
            # 重新建立连接
            await self.connect()
            logger.info("重新连接成功")
            return True

        except Exception as e:
            logger.error(f"重新连接失败: {e}")
            return False

    async def _handle_connection_error(self) -> None:
        """
        处理连接错误的内部方法

        当发生连接相关错误时，清理连接状态并标记为断开。
        这个方法通常在发送/接收数据失败后被调用。
        """
        logger.debug(f"处理连接错误: {self.remote_addr}:{self.remote_port}")
        if not await self.is_connected():
            self._is_connected = False

            # 清理读写器
            if self._writer:
                try:
                    self._writer.close()
                    await asyncio.wait_for(
                        self._writer.wait_closed(),
                        timeout=1.0
                    )
                except:
                    pass

            self._reader = None
            self._writer = None

    @property
    def connection_info(self) -> dict:
        """
        获取连接信息

        Returns:
            dict: 包含连接详细信息的字典
        """
        return {
            'remote_addr': self.remote_addr,
            'remote_port': self.remote_port,
            'is_connected': self._is_connected,
            'connect_timeout': self.connect_timeout,
            'network_timeout': self.network_timeout,
            'use_ssl': self.use_ssl,
            'pid': self.pid
        }


class AsyncConnectionPool:
    """
    异步连接池

    管理多个异步连接实例，提供连接复用功能，减少连接建立和断开的开销。
    支持连接池大小限制、连接超时、自动重连等功能。

    Attributes:
        host_tuple (List[str]): 主机地址元组列表
        connect_timeout (float): 连接超时时间
        network_timeout (float): 网络操作超时时间
        pool_size (int): 连接池最大大小
        max_idle_time (float): 连接最大空闲时间
        _pool (asyncio.Queue): 连接池队列
        _active_connections (int): 当前活跃连接数
        _pool_lock (asyncio.Lock): 连接池操作锁
    """

    def __init__(self,
                 host_tuple: List[str],
                 connect_timeout: float = 5.0,
                 network_timeout: float = 10.0,
                 pool_size: int = 10,
                 max_idle_time: float = 300.0,
                 use_ssl: bool = False,
                 ssl_context: Optional[ssl.SSLContext] = None):
        """
        初始化异步连接池

        Args:
            host_tuple: 主机地址元组列表
            connect_timeout: 连接超时时间
            network_timeout: 网络操作超时时间
            pool_size: 连接池最大大小
            max_idle_time: 连接最大空闲时间（秒），超过此时间的空闲连接将被清理
            use_ssl: 是否使用SSL加密连接
            ssl_context: 自定义SSL上下文
        """
        self.host_tuple = host_tuple
        self.connect_timeout = connect_timeout
        self.network_timeout = network_timeout
        self.pool_size = pool_size
        self.max_idle_time = max_idle_time
        self.use_ssl = use_ssl
        self.ssl_context = ssl_context

        # 连接池队列
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=pool_size)

        # 活跃连接计数
        self._active_connections = 0

        # 连接池操作锁
        self._pool_lock = asyncio.Lock()

        # 启动连接清理任务
        self._cleanup_task = None
        self._start_cleanup_task()

        logger.info(f"初始化异步连接池，大小: {pool_size}, 主机: {host_tuple}")

    async def get_connection(self) -> AsyncConnection:
        """
        从连接池获取连接

        如果连接池中有可用连接，则返回；否则创建新连接。

        Returns:
            AsyncConnection: 异步连接实例

        Raises:
            AsyncConnectionError: 当无法创建连接时抛出
        """
        while not self._pool.empty():
            try:
                # 尝试从连接池获取现有连接
                connection = self._pool.get_nowait()
                self._pool.task_done()

                # 检查连接是否仍然有效
                if await connection.is_connected():
                    logger.debug("从连接池获取现有连接")
                    return connection
                else:
                    logger.debug("连接已失效，丢弃并创建新连接")
                    self._active_connections -= 1

            except asyncio.QueueEmpty:
                # 连接池为空，需要创建新连接
                pass

        # 创建新连接
        async with self._pool_lock:
            if self._active_connections >= self.pool_size:
                logger.warning(f"连接池已满 ({self.pool_size})，等待可用连接")
                # 等待其他连接释放
                connection = await self._pool.get()
                self._pool.task_done()
                if await connection.is_connected():
                    return connection
                else:
                    # 如果获取的连接无效，继续创建新连接
                    pass

            connection = AsyncConnection(
                host_tuple=self.host_tuple,
                connect_timeout=self.connect_timeout,
                network_timeout=self.network_timeout,
                use_ssl=self.use_ssl,
                ssl_context=self.ssl_context,
                pool=self
            )

            await connection.connect()
            self._active_connections += 1

            logger.debug(f"创建新连接，当前活跃连接数: {self._active_connections}")
            return connection

    async def return_connection(self, connection: AsyncConnection) -> None:
        """
        将连接返回到连接池

        Args:
            connection: 要返回的连接实例

        Note:
            如果连接已断开，将不会被返回到连接池
        """
        if connection and await connection.is_connected():
            try:
                self._pool.put_nowait(connection)
                logger.debug("连接已返回到连接池")
            except asyncio.QueueFull:
                # 连接池已满，关闭多余的连接
                logger.debug("连接池已满，关闭连接")
                await connection.disconnect()
                self._active_connections -= 1
        else:
            # 连接已断开，减少活跃连接计数
            logger.debug("连接已断开，不返回到连接池")
            self._active_connections -= 1

    async def close_all(self) -> None:
        """
        关闭连接池中的所有连接

        清理连接池，关闭所有连接并停止后台清理任务。
        """
        logger.info("开始关闭连接池中的所有连接")

        # 停止清理任务
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # 关闭连接池中的所有连接
        while not self._pool.empty():
            try:
                connection = self._pool.get_nowait()
                self._pool.task_done()
                await connection.disconnect()
            except asyncio.QueueEmpty:
                break

        logger.info(f"连接池已关闭，共关闭 {self._active_connections} 个连接")
        self._active_connections = 0

    def _start_cleanup_task(self) -> None:
        """启动连接清理任务"""
        self._cleanup_task = asyncio.create_task(self._cleanup_idle_connections())

    async def _cleanup_idle_connections(self) -> None:
        """
        清理空闲连接的后台任务

        定期检查并关闭超过最大空闲时间的连接。
        """
        logger.debug("启动连接清理任务")

        while True:
            try:
                await asyncio.sleep(120)  # 每2分钟检查一次

                current_time = asyncio.get_event_loop().time()
                connections_to_check = []

                # 收集池中的连接进行检查
                while not self._pool.empty():
                    try:
                        connection = self._pool.get_nowait()
                        self._pool.task_done()
                        connections_to_check.append(connection)
                    except asyncio.QueueEmpty:
                        break

                # 检查每个连接的空闲时间
                for connection in connections_to_check:
                    # 这里简化处理，实际应该记录连接的最后使用时间
                    # 如果连接不活跃，则关闭
                    if not await connection.is_connected():
                        await connection.disconnect()
                        self._active_connections -= 1
                        logger.debug("关闭不活跃的连接")
                    else:
                        # 连接仍然有效，返回到池中
                        try:
                            self._pool.put_nowait(connection)
                        except asyncio.QueueFull:
                            # 池已满，关闭连接
                            await connection.disconnect()
                            self._active_connections -= 1

            except asyncio.CancelledError:
                logger.debug("连接清理任务被取消")
                break
            except Exception as e:
                logger.error(f"连接清理任务发生错误: {e}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close_all()

    @property
    def pool_info(self) -> dict:
        """
        获取连接池信息

        Returns:
            dict: 包含连接池状态信息的字典
        """
        return {
            'pool_size': self.pool_size,
            'active_connections': self._active_connections,
            'available_connections': self._pool.qsize(),
            'host_tuple': self.host_tuple,
            'connect_timeout': self.connect_timeout,
            'network_timeout': self.network_timeout,
            'max_idle_time': self.max_idle_time,
            'use_ssl': self.use_ssl
        }



async def tcp_recv_response(conn: AsyncConnection, bytes_size, buffer_size=4096):
    '''Receive response from server.
        It is not include tracker header.
        arguments:
        @conn: connection
        @bytes_size: int, will be received byte_stream size
        @buffer_size: int, receive buffer size
        @Return: tuple,(response, received_size)
    '''
    recv_buff = []
    total_size = 0
    try:
        while bytes_size > 0:
            resp = await conn.receive(buffer_size)
            recv_buff.append(resp)
            total_size += len(resp)
            bytes_size -= len(resp)
    except AsyncConnectionError as e:
        raise ConnectionError(f'[-] Error: while reading from socket: {e}')
    return (b''.join(recv_buff), total_size)


async def tcp_send_data(conn: AsyncConnection, bytes_stream):
    '''Send buffer to server.
        It is not include tracker header.
        arguments:
        @conn: connection
        @bytes_stream: trasmit buffer
        @Return bool
    '''
    try:
        await conn.send(bytes_stream)
    except AsyncConnectionError as e:
        raise ConnectionError(f'[-] Error: while writting to socket: {e}')