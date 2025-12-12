#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: tracker_client.py
import os

from .async_connection import AsyncConnectionPool, tcp_send_data, tcp_recv_response
from .async_fdfs_protol import *
from .entity.group_info import Group_info
from .entity.storage_info import Storage_info
from .exceptions import (
    ConnectionError,
    ResponseError,
    DataError
)


class Async_Tracker_Client(object):
    '''Class Tracker client.'''

    def __init__(self, pool: AsyncConnectionPool, store_path_index: int):
        self.pool = pool
        self.store_path_index = store_path_index

    async def tracker_list_servers(self, group_name, storage_ip=None):
        '''
        List servers in a storage group
        '''
        async with await self.pool.get_connection() as conn:
            th = Tracker_header()
            ip_len = len(storage_ip) if storage_ip else 0
            if ip_len >= IP_ADDRESS_SIZE:
                ip_len = IP_ADDRESS_SIZE - 1
            th.pkg_len = FDFS_GROUP_NAME_MAX_LEN + ip_len
            th.cmd = TRACKER_PROTO_CMD_SERVER_LIST_STORAGE
            group_fmt = '!%ds' % FDFS_GROUP_NAME_MAX_LEN
            store_ip_addr = storage_ip or ''
            storage_ip_fmt = '!%ds' % ip_len
            try:
                await th.send_header(conn)
                send_buffer = struct.pack(group_fmt, group_name) + struct.pack(storage_ip_fmt, store_ip_addr)
                await conn.send(send_buffer)
                await th.recv_header(conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
                recv_buffer, recv_size = await tcp_recv_response(conn, th.pkg_len)
                si = Storage_info()
                si_fmt_size = si.get_fmt_size()
                recv_size = len(recv_buffer)
                if recv_size % si_fmt_size != 0:
                    errinfo = '[-] Error: response size not match, expect: %d, actual: %d' % (th.pkg_len, recv_size)
                    raise ResponseError(errinfo)
            except ConnectionError:
                raise
            num_storage = recv_size / si_fmt_size
            si_list = []
            i = 0
            while num_storage:
                si.set_info(recv_buffer[(i * si_fmt_size): ((i + 1) * si_fmt_size)])
                si_list.append(si)
                si = Storage_info()
                num_storage -= 1
                i += 1
            ret_dict = {}
            ret_dict['Group name'] = group_name
            ret_dict['Servers'] = si_list
            return ret_dict

    async def tracker_list_one_group(self, group_name):
        async with await self.pool.get_connection() as conn:
            th = Tracker_header()
            th.pkg_len = FDFS_GROUP_NAME_MAX_LEN
            th.cmd = TRACKER_PROTO_CMD_SERVER_LIST_ONE_GROUP
            # group_fmt: |-group_name(16)-|
            group_fmt = '!%ds' % FDFS_GROUP_NAME_MAX_LEN
            try:
                await th.send_header(conn)
                send_buffer = struct.pack(group_fmt, group_name)
                await conn.send(send_buffer)
                await th.recv_header(conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
                recv_buffer, recv_size = await tcp_recv_response(conn, th.pkg_len)
                group_info = Group_info()
                group_info.set_info(recv_buffer)
            except ConnectionError:
                raise
            return group_info

    async def tracker_list_all_groups(self):
        async with await self.pool.get_connection() as conn:
            th = Tracker_header()
            th.cmd = TRACKER_PROTO_CMD_SERVER_LIST_ALL_GROUPS
            try:
                await th.send_header(conn)
                await th.recv_header(conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
                recv_buffer, recv_size = await tcp_recv_response(conn, th.pkg_len)
            except:
                raise
            gi = Group_info()
            gi_fmt_size = gi.get_fmt_size()
            if recv_size % gi_fmt_size != 0:
                errmsg = '[-] Error: Response size is mismatch, except: %d, actul: %d' % (th.pkg_len, recv_size)
                raise ResponseError(errmsg)
            num_groups = recv_size / gi_fmt_size
            ret_dict = {}
            ret_dict['Groups count'] = num_groups
            gi_list = []
            i = 0
            while num_groups:
                gi.set_info(recv_buffer[i * gi_fmt_size: (i + 1) * gi_fmt_size])
                gi_list.append(gi)
                gi = Group_info()
                i += 1
                num_groups -= 1
            ret_dict['Groups'] = gi_list
            return ret_dict

    async def tracker_query_storage_stor_without_group(self):
        '''Query storage server for upload, without group name.
        Return: Storage_server object'''
        async with await self.pool.get_connection() as conn:
            th = Tracker_header()
            th.cmd = TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITHOUT_GROUP_ONE
            try:
                await th.send_header(conn)
                await th.recv_header(conn)
                if th.status != 0:
                    raise DataError('[-] Error: %d, %s' % (th.status, os.strerror(th.status)))
                recv_buffer, recv_size = await tcp_recv_response(conn, th.pkg_len)
                if recv_size != TRACKER_QUERY_STORAGE_STORE_BODY_LEN:
                    errmsg = '[-] Error: Tracker response length is invaild, '
                    errmsg += 'expect: %d, actual: %d' % (TRACKER_QUERY_STORAGE_STORE_BODY_LEN, recv_size)
                    raise ResponseError(errmsg)
            except ConnectionError:
                raise
            # recv_fmt |-group_name(16)-ipaddr(16-1)-port(8)-store_path_index(1)|
            recv_fmt = '!%ds %ds Q B' % (FDFS_GROUP_NAME_MAX_LEN, IP_ADDRESS_SIZE - 1)
            store_serv: Storage_server = Storage_server()
            (group_name, ip_addr, store_serv.port, store_serv.store_path_index) = struct.unpack(recv_fmt, recv_buffer)
            store_serv.group_name = group_name.strip(b'\x00')
            store_serv.ip_addr = ip_addr.strip(b'\x00')
            if -1 < self.store_path_index < 256:
                store_serv.store_path_index = self.store_path_index
            return store_serv

    async def tracker_query_storage_stor_with_group(self, group_name):
        '''Query storage server for upload, based group name.
        arguments:
        @group_name: string
        @Return Storage_server object
        '''
        async with await self.pool.get_connection() as conn:
            th = Tracker_header()
            th.cmd = TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITH_GROUP_ONE
            th.pkg_len = FDFS_GROUP_NAME_MAX_LEN
            await th.send_header(conn)
            group_fmt = '!%ds' % FDFS_GROUP_NAME_MAX_LEN
            send_buffer = struct.pack(group_fmt, group_name)
            try:
                await tcp_send_data(conn, send_buffer)
                await th.recv_header(conn)
                if th.status != 0:
                    raise DataError('Error: %d, %s' % (th.status, os.strerror(th.status)))
                recv_buffer, recv_size = await tcp_recv_response(conn, th.pkg_len)
                if recv_size != TRACKER_QUERY_STORAGE_STORE_BODY_LEN:
                    errmsg = '[-] Error: Tracker response length is invaild, '
                    errmsg += 'expect: %d, actual: %d' % (TRACKER_QUERY_STORAGE_STORE_BODY_LEN, recv_size)
                    raise ResponseError(errmsg)
            except ConnectionError:
                raise
            # recv_fmt: |-group_name(16)-ipaddr(16-1)-port(8)-store_path_index(1)-|
            recv_fmt = '!%ds %ds Q B' % (FDFS_GROUP_NAME_MAX_LEN, IP_ADDRESS_SIZE - 1)
            store_serv = Storage_server()
            (group, ip_addr, store_serv.port, store_serv.store_path_index) = struct.unpack(recv_fmt, recv_buffer)
            store_serv.group_name = group.strip(b'\x00')
            store_serv.ip_addr = ip_addr.strip(b'\x00')
            return store_serv

    async def _tracker_do_query_storage(self, group_name, filename, cmd):
        '''
        core of query storage, based group name and filename. 
        It is useful download, delete and set meta.
        arguments:
        @group_name: string
        @filename: string. remote file_id
        @Return: Storage_server object
        '''
        async with await self.pool.get_connection() as conn:
            th = Tracker_header()
            file_name_len = len(filename)
            th.pkg_len = FDFS_GROUP_NAME_MAX_LEN + file_name_len
            th.cmd = cmd
            await th.send_header(conn)
            # query_fmt: |-group_name(16)-filename(file_name_len)-|
            query_fmt = '!%ds %ds' % (FDFS_GROUP_NAME_MAX_LEN, file_name_len)
            send_buffer = struct.pack(query_fmt, group_name.encode(), filename.encode())
            try:
                await tcp_send_data(conn, send_buffer)
                await th.recv_header(conn)
                if th.status != 0:
                    raise DataError('Error: %d, %s' % (th.status, os.strerror(th.status)))
                recv_buffer, recv_size = await tcp_recv_response(conn, th.pkg_len)
                if recv_size != TRACKER_QUERY_STORAGE_FETCH_BODY_LEN:
                    errmsg = '[-] Error: Tracker response length is invaild, '
                    errmsg += 'expect: %d, actual: %d' % (th.pkg_len, recv_size)
                    raise ResponseError(errmsg)
            except ConnectionError:
                raise
            # recv_fmt: |-group_name(16)-ip_addr(16)-port(8)-|
            recv_fmt = '!%ds %ds Q' % (FDFS_GROUP_NAME_MAX_LEN, IP_ADDRESS_SIZE - 1)
            store_serv = Storage_server()
            (group_name, ipaddr, store_serv.port) = struct.unpack(recv_fmt, recv_buffer)
            store_serv.group_name = group_name.strip(b'\x00')
            store_serv.ip_addr = ipaddr.strip(b'\x00')
            return store_serv

    async def tracker_query_storage_update(self, group_name, filename):
        '''
        Query storage server to update(delete and set_meta).
        '''
        return await self._tracker_do_query_storage(group_name, filename, TRACKER_PROTO_CMD_SERVICE_QUERY_UPDATE)

    async def tracker_query_storage_fetch(self, group_name, filename):
        '''
        Query storage server to download.
        '''
        return await self._tracker_do_query_storage(group_name, filename, TRACKER_PROTO_CMD_SERVICE_QUERY_FETCH_ONE)
