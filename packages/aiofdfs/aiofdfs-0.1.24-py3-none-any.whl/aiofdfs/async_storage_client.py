#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: storage_client.py
import platform

import aiofiles

from .async_connection import *
from .async_fdfs_protol import *
# from test_fdfs.sendfile import *
from .exceptions import (
    ConnectionError,
    ResponseError,
    DataError
)

__os_sep__ = "/" if platform.system() == 'Windows' else os.sep

from .util import appromix, get_file_ext_name


async def tcp_send_file(conn: AsyncConnection, filename, buffer_size=512 * 1024):
    '''
    Send file to server, and split into multiple pkgs while sending.
    arguments:
    @conn: connection
    @filename: string
    @buffer_size: int ,send buffer size
    @Return int: file size if success else raise ConnectionError.
    '''
    file_size = 0
    async with aiofiles.open(filename, 'rb') as f:
        while True:
            try:
                send_buffer = await f.read(buffer_size)
                send_size = len(send_buffer)
                if send_size == 0:
                    break
                await tcp_send_data(conn, send_buffer)
                file_size += send_size
            except ConnectionError as e:
                raise ConnectionError('[-] Error while uploading file(%s).' % e.args)
            except IOError as e:
                raise DataError('[-] Error while reading local file(%s).' % e.args)
    return file_size

async def tcp_recv_file(conn: AsyncConnection, local_filename, file_size, buffer_size=512 * 1024):
    '''
    Receive file from server, fragmented it while receiving and write to disk.
    arguments:
    @conn: connection
    @local_filename: string
    @file_size: int, remote file size
    @buffer_size: int, receive buffer size
    @Return int: file size if success else raise ConnectionError.
    '''
    total_file_size = 0
    flush_size = 0
    remain_bytes = file_size
    async with aiofiles.open(local_filename, 'wb+') as f:
        while remain_bytes > 0:
            try:
                if remain_bytes >= buffer_size:
                    file_buffer, recv_size = await tcp_recv_response(conn, buffer_size, buffer_size)
                else:
                    file_buffer, recv_size = await tcp_recv_response(conn, remain_bytes, buffer_size)
                await f.write(file_buffer)
                remain_bytes -= recv_size
                total_file_size += recv_size
                flush_size += recv_size
                if flush_size >= 4096:
                    await f.flush()
                    flush_size = 0
            except ConnectionError as e:
                raise ConnectionError('[-] Error: while downloading file(%s).' % e.args)
            except IOError as e:
                raise DataError('[-] Error: while writting local file(%s).' % e.args)
    return total_file_size

async def tcp_upload_from_upload_file(conn: AsyncConnection, upload_file, buffer_size=512 * 1024):
    '''
    Send file to server, and split into multiple pkgs while sending.
    arguments:
    @conn: connection
    @buffer_size: int ,send buffer size
    @Return int: file size if success else raise ConnectionError.
    '''
    file_size = 0
    while True:
        try:
            send_buffer = await upload_file.read(buffer_size)
            send_size = len(send_buffer)
            if send_size == 0:
                break
            await tcp_send_data(conn, send_buffer)
            file_size += send_size
        except ConnectionError as e:
            raise ConnectionError('[-] Error while uploading file(%s).' % e.args)
        except IOError as e:
            raise DataError('[-] Error while reading local file(%s).' % e.args)
    return file_size


async def tcp_recv_generator(conn: AsyncConnection, file_size, buffer_size=512 * 1024):
    '''
    Receive file from server, fragmented it while receiving and write to bytes.
    arguments:
    @conn: connection
    @file_size: int, remote file size
    @buffer_size: int, receive buffer size
    @Return int: file size if success else raise ConnectionError.
    '''
    total_file_size = 0
    remain_bytes = file_size
    while remain_bytes > 0:
        try:
            if remain_bytes >= buffer_size:
                file_buffer, recv_size = await tcp_recv_response(conn, buffer_size, buffer_size)
            else:
                file_buffer, recv_size = await tcp_recv_response(conn, remain_bytes, buffer_size)
            yield file_buffer
            remain_bytes -= recv_size
            total_file_size += recv_size
        except ConnectionError as e:
            raise ConnectionError('[-] Error: while downloading file(%s).' % e.args)
        except IOError as e:
            raise DataError('[-] Error: while writting local file(%s).' % e.args)

class Async_Storage_Client(object):
    '''
    The Class Storage_client for storage server.
    Note: argument host_tuple of storage server ip address, that should be a single element.
    '''

    def __init__(self, *kwargs):
        conn_kwargs = {
            # 'name': 'Storage Pool',
            'host_tuple': (f'{kwargs[0].decode("utf-8")}:{kwargs[1]}',),
            'connect_timeout': kwargs[2],
            'network_timeout': kwargs[3]
        }
        self.pool: AsyncConnectionPool = AsyncConnectionPool(**conn_kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pool.close_all()
        self.pool = None

    async def update_pool(self, old_store_serv, new_store_serv, connect_timeout=30, network_timeout=30):
        '''
        Update connection pool of storage client.
        We need update connection pool of storage client, while storage server is changed.
        but if server not changed, we do nothing.
        '''
        if old_store_serv.ip_addr == new_store_serv.ip_addr:
            return None
        await self.pool.close_all()
        if isinstance(new_store_serv.ip_addr, str):
            ip_addr = new_store_serv.ip_addr
        else:
            ip_addr = new_store_serv.ip_addr.decode("utf-8")
        conn_kwargs = {
            'name': 'Storage_pool',
            'host_tuple': (f'{ip_addr}:{new_store_serv.port}',),
            'connect_timeout': connect_timeout,
            'network_timeout': network_timeout
        }
        self.pool: AsyncConnectionPool = AsyncConnectionPool(**conn_kwargs)
        return True


    async def storage_upload_from_upload_file(self, store_serv, upload_file, file_size=None, meta_dict=None,
                                              master_filename=None, prefix_name=None,
                                              file_ext_name=None):
        '''
        core of upload file.
        arguments:
        @tracker_client: Tracker_client, it is useful connect to tracker server
        @store_serv: Storage_server, it is return from query tracker server
        @file_size: int
        @upload_type: int, optional: FDFS_UPLOAD_BY_FILE, FDFS_UPLOAD_BY_FILENAME,
                                     FDFS_UPLOAD_BY_BUFFER
        @meta_dic: dictionary, store metadata in it
        @cmd: int, reference fdfs protol
        @master_filename: string, useful upload slave file
        @prefix_name: string
        @file_ext_name: string
        @Return dictionary
                 {
                     'group_name'      : group_name,
                     'file_id'  : remote_file_id,
                     'file_name'  : file_name,
                     'file_size'   : upload_size,
                     'storage_ip'      : storage_ip
                 }

        '''

        async with await self.pool.get_connection() as store_conn:
            th = Tracker_header()
            master_filename_len = len(master_filename) if master_filename else 0
            prefix_name_len = len(prefix_name) if prefix_name else 0
            upload_slave = len(store_serv.group_name) and master_filename_len
            file_ext_name = str(file_ext_name) if file_ext_name else ''
            # non_slave_fmt |-store_path_index(1)-file_size(8)-file_ext_name(6)-|
            non_slave_fmt = '!B Q %ds' % FDFS_FILE_EXT_NAME_MAX_LEN
            # slave_fmt |-master_len(8)-file_size(8)-prefix_name(16)-file_ext_name(6)
            #           -master_name(master_filename_len)-|
            slave_fmt = '!Q Q %ds %ds %ds' % (FDFS_FILE_PREFIX_MAX_LEN, FDFS_FILE_EXT_NAME_MAX_LEN, master_filename_len)
            th.pkg_len = struct.calcsize(slave_fmt) if upload_slave else struct.calcsize(non_slave_fmt)
            th.pkg_len += file_size
            th.cmd = STORAGE_PROTO_CMD_UPLOAD_FILE
            await th.send_header(store_conn)
            if upload_slave:
                send_buffer = struct.pack(
                    slave_fmt, master_filename_len, file_size, prefix_name, file_ext_name, master_filename)
            else:
                send_buffer = struct.pack(non_slave_fmt, store_serv.store_path_index, file_size, file_ext_name.encode("utf-8"))
            try:
                await tcp_send_data(store_conn, send_buffer)
                send_file_size = await tcp_upload_from_upload_file(store_conn, upload_file)
                await th.recv_header(store_conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
                recv_buffer, recv_size = await tcp_recv_response(store_conn, th.pkg_len)
                if recv_size <= FDFS_GROUP_NAME_MAX_LEN:
                    errmsg = '[-] Error: Storage response length is not match, '
                    errmsg += 'expect: %d, actual: %d' % (th.pkg_len, recv_size)
                    raise ResponseError(errmsg)
                # recv_fmt: |-group_name(16)-remote_file_name(recv_size - 16)-|
                recv_fmt = '!%ds %ds' % (FDFS_GROUP_NAME_MAX_LEN, th.pkg_len - FDFS_GROUP_NAME_MAX_LEN)
                (group_name, remote_name) = struct.unpack(recv_fmt, recv_buffer)
                remote_filename = remote_name.strip(b'\x00')
                if meta_dict and len(meta_dict) > 0:
                    status = await self.__storage_set_metadata(store_conn, store_serv, remote_filename, meta_dict)
                    if status != 0:
                        # rollback
                        await self.__storage_delete_file(store_conn, store_serv, remote_filename)
                        raise DataError('[-] Error: %d, %s' % (status, os.strerror(status)))
                group_name = group_name.strip(b'\x00').decode()
                remote_filename = remote_filename.decode()
            except:
                raise
            ret_dict = {
                'group_name': group_name,
                'file_id': group_name + __os_sep__ + remote_filename,
                'file_name': meta_dict['OriginFileName'],
                'file_size': appromix(send_file_size),
                'storage_ip': store_serv.ip_addr.decode()
            }
            return ret_dict

    async def _storage_do_upload_file(self, tracker_client, store_serv, file_buffer, file_size=None, upload_type=None,
                                meta_dict=None, cmd=None, master_filename=None, prefix_name=None, file_ext_name=None):
        '''
        core of upload file.
        arguments:
        @tracker_client: Tracker_client, it is useful connect to tracker server
        @store_serv: Storage_server, it is return from query tracker server
        @file_buffer: string, file name or file buffer for send
        @file_size: int
        @upload_type: int, optional: FDFS_UPLOAD_BY_FILE, FDFS_UPLOAD_BY_FILENAME,
                                     FDFS_UPLOAD_BY_BUFFER
        @meta_dic: dictionary, store metadata in it
        @cmd: int, reference fdfs protol
        @master_filename: string, useful upload slave file
        @prefix_name: string
        @file_ext_name: string
        @Return dictionary 
                 {
                     'group_name'      : group_name,
                     'file_id'  : remote_file_id,
                     'file_name'  : file_name,
                     'file_size'   : upload_size,
                     'storage_ip'      : storage_ip
                 }

        '''

        async with await self.pool.get_connection() as store_conn:
            th = Tracker_header()
            master_filename_len = len(master_filename) if master_filename else 0
            prefix_name_len = len(prefix_name) if prefix_name else 0
            upload_slave = len(store_serv.group_name) and master_filename_len
            file_ext_name = str(file_ext_name) if file_ext_name else ''
            # non_slave_fmt |-store_path_index(1)-file_size(8)-file_ext_name(6)-|
            non_slave_fmt = '!B Q %ds' % FDFS_FILE_EXT_NAME_MAX_LEN
            # slave_fmt |-master_len(8)-file_size(8)-prefix_name(16)-file_ext_name(6)
            #           -master_name(master_filename_len)-|
            slave_fmt = '!Q Q %ds %ds %ds' % (FDFS_FILE_PREFIX_MAX_LEN, FDFS_FILE_EXT_NAME_MAX_LEN, master_filename_len)
            th.pkg_len = struct.calcsize(slave_fmt) if upload_slave else struct.calcsize(non_slave_fmt)
            th.pkg_len += file_size
            th.cmd = cmd
            await th.send_header(store_conn)
            if upload_slave:
                send_buffer = struct.pack(
                    slave_fmt, master_filename_len, file_size, prefix_name, file_ext_name, master_filename)
            else:
                send_buffer = struct.pack(non_slave_fmt, store_serv.store_path_index, file_size, file_ext_name.encode("utf-8"))
            try:
                await tcp_send_data(store_conn, send_buffer)
                if upload_type == FDFS_UPLOAD_BY_FILENAME or upload_type == FDFS_UPLOAD_BY_FILE:
                    send_file_size = await tcp_send_file(store_conn, file_buffer)
                elif upload_type == FDFS_UPLOAD_BY_BUFFER:
                    await tcp_send_data(store_conn, file_buffer)
                await th.recv_header(store_conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
                recv_buffer, recv_size = await tcp_recv_response(store_conn, th.pkg_len)
                if recv_size <= FDFS_GROUP_NAME_MAX_LEN:
                    errmsg = '[-] Error: Storage response length is not match, '
                    errmsg += 'expect: %d, actual: %d' % (th.pkg_len, recv_size)
                    raise ResponseError(errmsg)
                # recv_fmt: |-group_name(16)-remote_file_name(recv_size - 16)-|
                recv_fmt = '!%ds %ds' % (FDFS_GROUP_NAME_MAX_LEN, th.pkg_len - FDFS_GROUP_NAME_MAX_LEN)
                (group_name, remote_name) = struct.unpack(recv_fmt, recv_buffer)
                remote_filename = remote_name.strip(b'\x00')
                if meta_dict and len(meta_dict) > 0:
                    status = await self.__storage_set_metadata(store_conn, store_serv, remote_filename, meta_dict)
                    if status != 0:
                        # rollback
                        await self.__storage_delete_file(store_conn, store_serv, remote_filename)
                        raise DataError('[-] Error: %d, %s' % (status, os.strerror(status)))
                group_name = group_name.strip(b'\x00').decode()
                remote_filename = remote_filename.decode()
            except:
                raise
            ret_dict = {
                'group_name': group_name,
                'file_id': group_name + __os_sep__ + remote_filename,
                'file_name': file_buffer if (upload_type == FDFS_UPLOAD_BY_FILENAME
                                                   or upload_type == FDFS_UPLOAD_BY_FILE
                                                   ) else '',
                'file_size': appromix(send_file_size) if (upload_type == FDFS_UPLOAD_BY_FILENAME
                                                              or upload_type == FDFS_UPLOAD_BY_FILE
                                                              ) else appromix(len(file_buffer)),
                'storage_ip': store_serv.ip_addr.decode()
            }
            return ret_dict

    async def storage_upload_by_filename(self, tracker_client, store_serv, filename, meta_dict=None):
        file_size = os.stat(filename).st_size
        file_ext_name = get_file_ext_name(filename)
        meta_dict = meta_dict or {}
        meta_dict["OriginFileExtName"] = file_ext_name
        meta_dict["OriginFileName"] = os.path.basename(filename)
        meta_dict["OriginFileSize"] = file_size
        return await self._storage_do_upload_file(tracker_client, store_serv, filename, file_size, FDFS_UPLOAD_BY_FILENAME,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_FILE, None, None, file_ext_name)

    async def storage_upload_by_file(self, tracker_client, store_serv, filename, meta_dict=None):
        file_size = os.stat(filename).st_size
        file_ext_name = get_file_ext_name(filename)
        return await self._storage_do_upload_file(tracker_client, store_serv, filename, file_size, FDFS_UPLOAD_BY_FILE,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_FILE, None, None, file_ext_name)

    async def storage_upload_by_buffer(self, tracker_client, store_serv, file_buffer, file_ext_name=None, meta_dict=None):
        buffer_size = len(file_buffer)
        return await self._storage_do_upload_file(tracker_client, store_serv, file_buffer, buffer_size, FDFS_UPLOAD_BY_BUFFER,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_FILE, None, None, file_ext_name)

    async def storage_upload_slave_by_filename(self, tracker_client, store_serv, filename, prefix_name, remote_filename,
                                         meta_dict=None):
        file_size = os.stat(filename).st_size
        file_ext_name = get_file_ext_name(filename)
        return await self._storage_do_upload_file(tracker_client, store_serv, filename, file_size, FDFS_UPLOAD_BY_FILENAME,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_SLAVE_FILE, remote_filename,
                                            prefix_name, file_ext_name)

    async def storage_upload_slave_by_file(self, tracker_client, store_serv, filename, prefix_name, remote_filename,
                                     meta_dict=None):
        file_size = os.stat(filename).st_size
        file_ext_name = get_file_ext_name(filename)
        return await self._storage_do_upload_file(tracker_client, store_serv, filename, file_size, FDFS_UPLOAD_BY_FILE,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_SLAVE_FILE, remote_filename,
                                            prefix_name, file_ext_name)

    async def storage_upload_slave_by_buffer(self, tracker_client, store_serv, filebuffer, remote_filename, meta_dict,
                                       file_ext_name):
        file_size = len(filebuffer)
        return await self._storage_do_upload_file(tracker_client, store_serv, filebuffer, file_size, FDFS_UPLOAD_BY_BUFFER,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_SLAVE_FILE, None, remote_filename,
                                            file_ext_name)

    async def storage_upload_appender_by_filename(self, tracker_client, store_serv, filename, meta_dict=None):
        file_size = os.stat(filename).st_size
        file_ext_name = get_file_ext_name(filename)
        return await self._storage_do_upload_file(tracker_client, store_serv, filename, file_size, FDFS_UPLOAD_BY_FILENAME,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_APPENDER_FILE, None, None,
                                            file_ext_name)

    async def storage_upload_appender_by_file(self, tracker_client, store_serv, filename, meta_dict=None):
        file_size = os.stat(filename).st_size
        file_ext_name = get_file_ext_name(filename)
        return await self._storage_do_upload_file(tracker_client, store_serv, filename, file_size, FDFS_UPLOAD_BY_FILE,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_APPENDER_FILE, None, None,
                                            file_ext_name)

    async def storage_upload_appender_by_buffer(self, tracker_client, store_serv, file_buffer, meta_dict=None,
                                          file_ext_name=None):
        file_size = len(file_buffer)
        return await self._storage_do_upload_file(tracker_client, store_serv, file_buffer, file_size, FDFS_UPLOAD_BY_BUFFER,
                                            meta_dict, STORAGE_PROTO_CMD_UPLOAD_APPENDER_FILE, None, None,
                                            file_ext_name)

    async def storage_delete_file(self, store_serv, remote_filename):
        async with await self.pool.get_connection() as store_conn:
            return await self.__storage_delete_file(store_conn, store_serv, remote_filename)

    async def __storage_delete_file(self, store_conn: AsyncConnection, store_serv, remote_filename):
        '''
        Delete file from storage server.
        '''
        th = Tracker_header()
        th.cmd = STORAGE_PROTO_CMD_DELETE_FILE
        file_name_len = len(remote_filename)
        th.pkg_len = FDFS_GROUP_NAME_MAX_LEN + file_name_len
        try:
            await th.send_header(store_conn)
            # del_fmt: |-group_name(16)-filename(len)-|
            del_fmt = '!%ds %ds' % (FDFS_GROUP_NAME_MAX_LEN, file_name_len)
            send_buffer = struct.pack(del_fmt, store_serv.group_name, remote_filename)
            await tcp_send_data(store_conn, send_buffer)
            await th.recv_header(store_conn)
            # if th.status == 2:
            #    raise DataError('[-] Error: remote file %s is not exist.'
            #                    % (store_serv.group_name + __os_sep__.encode("utf-8") + remote_filename))
            if th.status != 0:
                raise DataError('Error: %d, %s' % (th.status, os.strerror(th.status)))
                # recv_buffer, recv_size = tcp_recv_response(store_conn, th.pkg_len)
        except:
            raise
        remote_filename = store_serv.group_name + __os_sep__.encode("utf-8") + remote_filename
        return ('Delete file successed.', remote_filename, store_serv.ip_addr)

    async def _storage_do_download_file_to_gen(self, store_serv, offset, download_size,
                                               remote_filename):
        '''
        Core of download file from storage server.
        You can choice download type, optional FDFS_DOWNLOAD_TO_FILE or
        FDFS_DOWNLOAD_TO_BUFFER. And you can choice file offset.
        @Return dictionary
            'Remote file name' : remote_filename,
            'Content' : local_filename or buffer,
            'Download size'   : download_size,
            'Storage IP'      : storage_ip
        '''
        async with await self.pool.get_connection() as store_conn:
            th = Tracker_header()
            remote_filename_len = len(remote_filename)
            th.pkg_len = FDFS_PROTO_PKG_LEN_SIZE * 2 + FDFS_GROUP_NAME_MAX_LEN + remote_filename_len
            th.cmd = STORAGE_PROTO_CMD_DOWNLOAD_FILE
            try:
                await th.send_header(store_conn)
                # down_fmt: |-offset(8)-download_bytes(8)-group_name(16)-remote_filename(len)-|
                down_fmt = '!Q Q %ds %ds' % (FDFS_GROUP_NAME_MAX_LEN, remote_filename_len)
                send_buffer = struct.pack(down_fmt, offset, download_size,
                                          store_serv.group_name, remote_filename.encode('utf-8'))
                await tcp_send_data(store_conn, send_buffer)
                await th.recv_header(store_conn)
                # if th.status == 2:
                #    raise DataError('[-] Error: remote file %s is not exist.' %
                #                    (store_serv.group_name + __os_sep__.encode("utf-8") + remote_filename))
                if th.status != 0:
                    raise DataError('Error: %d %s' % (th.status, os.strerror(th.status)))
                async for recv_buffer in tcp_recv_generator(store_conn, th.pkg_len):
                    yield recv_buffer
            except:
                raise

    async def _storage_do_download_file(self, store_serv, file_buffer, offset, download_size,
                                  download_type, remote_filename):
        '''
        Core of download file from storage server.
        You can choice download type, optional FDFS_DOWNLOAD_TO_FILE or 
        FDFS_DOWNLOAD_TO_BUFFER. And you can choice file offset.
        @Return dictionary
            'file_id' : remote_filename,
            'content' : local_filename or buffer,
            'download_size'   : download_size,
            'storage_ip'      : storage_ip
        '''
        async with await self.pool.get_connection() as store_conn:
            th = Tracker_header()
            remote_filename_len = len(remote_filename)
            th.pkg_len = FDFS_PROTO_PKG_LEN_SIZE * 2 + FDFS_GROUP_NAME_MAX_LEN + remote_filename_len
            th.cmd = STORAGE_PROTO_CMD_DOWNLOAD_FILE
            try:
                await th.send_header(store_conn)
                # down_fmt: |-offset(8)-download_bytes(8)-group_name(16)-remote_filename(len)-|
                down_fmt = '!Q Q %ds %ds' % (FDFS_GROUP_NAME_MAX_LEN, remote_filename_len)
                send_buffer = struct.pack(down_fmt, offset, download_size,
                                          store_serv.group_name, remote_filename.encode('utf-8'))
                await tcp_send_data(store_conn, send_buffer)
                await th.recv_header(store_conn)
                # if th.status == 2:
                #    raise DataError('[-] Error: remote file %s is not exist.' %
                #                    (store_serv.group_name + __os_sep__.encode("utf-8") + remote_filename))
                if th.status != 0:
                    raise DataError('Error: %d %s' % (th.status, os.strerror(th.status)))
                if download_type == FDFS_DOWNLOAD_TO_FILE:
                    total_recv_size = await tcp_recv_file(store_conn, file_buffer, th.pkg_len)
                elif download_type == FDFS_DOWNLOAD_TO_BUFFER:
                    recv_buffer, total_recv_size = await tcp_recv_response(store_conn, th.pkg_len)
            except:
                raise
            ret_dic = {
                'file_id': store_serv.group_name.decode('utf-8') + __os_sep__ + remote_filename,
                'content': file_buffer if download_type == FDFS_DOWNLOAD_TO_FILE else recv_buffer,
                'download_size': appromix(total_recv_size),
                'storage_ip': store_serv.ip_addr
            }
            return ret_dic

    async def storage_download_to_generator(self, store_serv, file_offset, download_bytes,
                                            remote_filename):
        async for recv_buffer in self._storage_do_download_file_to_gen(store_serv, file_offset,
                                                                       download_bytes, remote_filename):
            yield recv_buffer

    async def storage_download_to_file(self, store_serv, local_filename, file_offset, download_bytes,
                                 remote_filename):
        return await self._storage_do_download_file(store_serv, local_filename, file_offset, download_bytes,
                                              FDFS_DOWNLOAD_TO_FILE, remote_filename)

    async def storage_download_to_buffer(self, store_serv, file_buffer, file_offset, download_bytes,
                                   remote_filename):
        return await self._storage_do_download_file(store_serv, file_buffer, file_offset, download_bytes,
                                              FDFS_DOWNLOAD_TO_BUFFER, remote_filename)

    async def storage_set_metadata(self, store_serv, remote_filename, meta_dict,
                             op_flag=STORAGE_SET_METADATA_FLAG_OVERWRITE):
        async with await self.pool.get_connection() as conn:
            return await self.__storage_set_metadata(conn, store_serv, remote_filename, meta_dict, op_flag)


    async def __storage_set_metadata(self, conn: AsyncConnection, store_serv, remote_filename, meta_dict,
                             op_flag=STORAGE_SET_METADATA_FLAG_OVERWRITE):
        ret = 0
        remote_filename_len = len(remote_filename)
        meta_buffer = fdfs_pack_metadata(meta_dict)
        meta_buffer_byte = meta_buffer.encode("utf-8")
        meta_len = len(meta_buffer_byte)
        th = Tracker_header()
        th.pkg_len = FDFS_PROTO_PKG_LEN_SIZE * 2 + 1 + FDFS_GROUP_NAME_MAX_LEN + remote_filename_len + meta_len
        th.cmd = STORAGE_PROTO_CMD_SET_METADATA
        try:
            await th.send_header(conn)
            # meta_fmt: |-filename_len(8)-meta_len(8)-op_flag(1)-group_name(16)
            #           -filename(remote_filename_len)-meta(meta_len)|
            meta_fmt = '!Q Q c %ds %ds %ds' % (FDFS_GROUP_NAME_MAX_LEN, remote_filename_len, meta_len)
            send_buffer = struct.pack(meta_fmt, remote_filename_len, meta_len, op_flag.encode("utf-8"), store_serv.group_name,
                                      remote_filename, meta_buffer_byte)
            await tcp_send_data(conn, send_buffer)
            await th.recv_header(conn)
            if th.status != 0:
                ret = th.status
        except:
            raise
        return ret

    async def storage_get_metadata(self, tracker_client, store_serv, remote_file_name):
        async with await self.pool.get_connection() as store_conn:
            th = Tracker_header()
            remote_filename_len = len(remote_file_name)
            th.pkg_len = FDFS_GROUP_NAME_MAX_LEN + remote_filename_len
            th.cmd = STORAGE_PROTO_CMD_GET_METADATA
            try:
                await th.send_header(store_conn)
                # meta_fmt: |-group_name(16)-filename(remote_filename_len)-|
                meta_fmt = '!%ds %ds' % (FDFS_GROUP_NAME_MAX_LEN, remote_filename_len)
                send_buffer = struct.pack(meta_fmt, store_serv.group_name, remote_file_name.encode("utf-8"))
                await tcp_send_data(store_conn, send_buffer)
                await th.recv_header(store_conn)
                # if th.status == 2:
                #    raise DataError('[-] Error: Remote file %s has no meta data.'
                #                    % (store_serv.group_name + __os_sep__.encode("utf-8") + remote_file_name))
                if th.status != 0:
                    raise DataError('[-] Error:%d, %s' % (th.status, os.strerror(th.status)))
                if th.pkg_len == 0:
                    ret_dict = {}
                meta_buffer, recv_size = await tcp_recv_response(store_conn, th.pkg_len)
            except:
                raise
            ret_dict = fdfs_unpack_metadata(meta_buffer)
            return ret_dict

    async def _storage_do_append_file(self, tracker_client, store_serv, file_buffer, file_size, upload_type,
                                appended_filename):
        async with await self.pool.get_connection() as store_conn:
            th = Tracker_header()
            appended_filename_len = len(appended_filename)
            th.pkg_len = FDFS_PROTO_PKG_LEN_SIZE * 2 + appended_filename_len + file_size
            th.cmd = STORAGE_PROTO_CMD_APPEND_FILE
            try:
                await th.send_header(store_conn)
                # append_fmt: |-appended_filename_len(8)-file_size(8)-appended_filename(len)
                #             -filecontent(filesize)-|
                append_fmt = '!Q Q %ds' % appended_filename_len
                send_buffer = struct.pack(append_fmt, appended_filename_len, file_size, appended_filename)
                await tcp_send_data(store_conn, send_buffer)
                if upload_type == FDFS_UPLOAD_BY_FILENAME or upload_type == FDFS_UPLOAD_BY_FILE:
                    await tcp_send_file(store_conn, file_buffer)
                elif upload_type == FDFS_UPLOAD_BY_BUFFER:
                    await tcp_send_data(store_conn, file_buffer)
                await th.recv_header(store_conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
            except:
                raise
            ret_dict = {}
            ret_dict['Status'] = 'Append file successed.'
            ret_dict['Appender file name'] = store_serv.group_name + __os_sep__.encode("utf-8") + appended_filename
            ret_dict['Appended size'] = appromix(file_size)
            ret_dict['Storage IP'] = store_serv.ip_addr
            return ret_dict

    async def storage_append_by_filename(self, tracker_client, store_serv, local_filename, appended_filename):
        file_size = os.stat(local_filename).st_size
        return await self._storage_do_append_file(tracker_client, store_serv, local_filename, file_size,
                                            FDFS_UPLOAD_BY_FILENAME, appended_filename)

    async def storage_append_by_file(self, tracker_client, store_serv, local_filename, appended_filename):
        file_size = os.stat(local_filename).st_size
        return await self._storage_do_append_file(tracker_client, store_serv, local_filename, file_size, FDFS_UPLOAD_BY_FILE,
                                            appended_filename)

    async def storage_append_by_buffer(self, tracker_client, store_serv, file_buffer, appended_filename):
        file_size = len(file_buffer)
        return await self._storage_do_append_file(tracker_client, store_serv, file_buffer, file_size, FDFS_UPLOAD_BY_BUFFER,
                                            appended_filename)

    async def _storage_do_truncate_file(self, tracker_client, store_serv, truncated_filesize, appender_filename):
        async with await self.pool.get_connection() as store_conn:
            th = Tracker_header()
            th.cmd = STORAGE_PROTO_CMD_TRUNCATE_FILE
            appender_filename_len = len(appender_filename)
            th.pkg_len = FDFS_PROTO_PKG_LEN_SIZE * 2 + appender_filename_len
            try:
                await th.send_header(store_conn)
                # truncate_fmt:|-appender_filename_len(8)-truncate_filesize(8)
                #              -appender_filename(len)-|
                truncate_fmt = '!Q Q %ds' % appender_filename_len
                send_buffer = struct.pack(truncate_fmt, appender_filename_len, truncated_filesize, appender_filename)
                await tcp_send_data(store_conn, send_buffer)
                await th.recv_header(store_conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
            except:
                raise
            ret_dict = {}
            ret_dict['Status'] = 'Truncate successed.'
            ret_dict['Storage IP'] = store_serv.ip_addr
            return ret_dict

    async def storage_truncate_file(self, tracker_client, store_serv, truncated_filesize, appender_filename):
        return await self._storage_do_truncate_file(tracker_client, store_serv, truncated_filesize, appender_filename)

    async def _storage_do_modify_file(self, tracker_client, store_serv, upload_type, filebuffer, offset, filesize,
                                appender_filename):
        async with await self.pool.get_connection() as store_conn:
            th = Tracker_header()
            th.cmd = STORAGE_PROTO_CMD_MODIFY_FILE
            appender_filename_len = len(appender_filename)
            th.pkg_len = FDFS_PROTO_PKG_LEN_SIZE * 3 + appender_filename_len + filesize
            try:
                await th.send_header(store_conn)
                # modify_fmt: |-filename_len(8)-offset(8)-filesize(8)-filename(len)-|
                modify_fmt = '!Q Q Q %ds' % appender_filename_len
                send_buffer = struct.pack(modify_fmt, appender_filename_len, offset, filesize, appender_filename)
                await tcp_send_data(store_conn, send_buffer)
                if upload_type == FDFS_UPLOAD_BY_FILENAME or upload_type == FDFS_UPLOAD_BY_FILE:
                    await tcp_send_file(store_conn, filebuffer)
                elif upload_type == FDFS_UPLOAD_BY_BUFFER:
                    await tcp_send_data(store_conn, filebuffer)
                await th.recv_header(store_conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
            except:
                raise
            ret_dict = {}
            ret_dict['Status'] = 'Modify successed.'
            ret_dict['Storage IP'] = store_serv.ip_addr
            return ret_dict

    async def storage_modify_by_filename(self, tracker_client, store_serv, filename, offset, filesize, appender_filename):
        return await self._storage_do_modify_file(tracker_client, store_serv, FDFS_UPLOAD_BY_FILENAME, filename, offset,
                                            filesize, appender_filename)

    async def storage_modify_by_file(self, tracker_client, store_serv, filename, offset, filesize, appender_filename):
        return await self._storage_do_modify_file(tracker_client, store_serv, FDFS_UPLOAD_BY_FILE, filename, offset, filesize,
                                            appender_filename)

    async def storage_modify_by_buffer(self, tracker_client, store_serv, filebuffer, offset, filesize, appender_filename):
        return await self._storage_do_modify_file(tracker_client, store_serv, FDFS_UPLOAD_BY_BUFFER, filebuffer, offset,
                                            filesize, appender_filename)
