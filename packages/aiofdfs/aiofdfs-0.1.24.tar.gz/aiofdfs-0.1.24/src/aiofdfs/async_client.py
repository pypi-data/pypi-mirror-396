#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: client.py

'''
  Client module for Fastdfs 3.08
  author: scott yuan scottzer8@gmail.com
  date: 2012-06-21
'''

from .fdfs_conf import FastDfsConf
from .async_storage_client import *
from .async_tracker_client import *
from .util import *


def get_tracker_conf(conf: FastDfsConf):
    tracker = {}
    try:
        tracker['host_tuple'] = tuple(conf.tracker_servers)
        tracker['connect_timeout'] = conf.connect_timeout
        tracker['network_timeout'] = conf.network_timeout
        # tracker['name'] = 'Tracker Pool'
    except:
        raise
    return tracker


class Async_Fdfs_Client(object):
    '''
    Class Fdfs_client implemented Fastdfs client protol ver 3.08.

    It's useful upload, download, delete file to or from fdfs server, etc. It's uses
    connection pool to manage connection to server.
    '''

    def __init__(self, conf: FastDfsConf, poolclass=AsyncConnectionPool):
        self.trackers = get_tracker_conf(conf)
        self.tracker_pool = poolclass(**self.trackers)
        self.connect_timeout = self.trackers['connect_timeout']
        self.network_timeout = self.trackers['network_timeout']
        self.store_path_index = conf.store_path_index

    async def close(self):
        try:
            await self.tracker_pool.close_all()
            self.tracker_pool = None
        except:
            pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def upload_by_filename(self, filename, meta_dict=None):
        '''
        Upload a file to Storage server.
        arguments:
        @filename: string, name of file that will be uploaded
        @meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        } meta_dict can be null
        @return dict {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        } if success else None
        '''
        isfile, errmsg = await async_fdfs_check_file(filename)
        if not isfile:
            raise DataError(errmsg + '(uploading)')
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_stor_without_group()
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_upload_by_filename(tc, store_serv, filename, meta_dict)


    async def upload_by_upload_file(self, upload_file, meta_dict=None):
        '''
        Upload a file to Storage server.
        arguments:
        @upload_file: upload_file
        @meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        } meta_dict can be null
        @return dict  {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        } if success else None
        '''
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_stor_without_group()

        file_name = upload_file.filename
        file_ext_name = get_file_ext_name(file_name)
        file_size = upload_file.size
        meta_dict = meta_dict or {}
        meta_dict["OriginFileExtName"] = file_ext_name
        meta_dict["OriginFileName"] = file_name
        meta_dict["OriginFileSize"] = file_size
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_upload_from_upload_file(store_serv, upload_file, upload_file.size, meta_dict,
                                                               file_ext_name=file_ext_name)

    async def upload_by_file(self, filename, meta_dict=None):
        isfile, errmsg = await async_fdfs_check_file(filename)
        if not isfile:
            raise DataError(errmsg + '(uploading)')
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_stor_without_group()
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_upload_by_file(tc, store_serv, filename, meta_dict)

    async def upload_by_buffer(self, filebuffer, file_ext_name=None, meta_dict=None):
        '''
        Upload a buffer to Storage server.
        arguments:
        @filebuffer: string, buffer
        @file_ext_name: string, file extend name
        @meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        }
        @return dict {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        } if success else None
        '''
        if not filebuffer:
            raise DataError('[-] Error: argument filebuffer can not be null.')
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_stor_without_group()
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_upload_by_buffer(tc, store_serv, filebuffer, file_ext_name, meta_dict)

    async def upload_slave_by_filename(self, filename, remote_file_id, prefix_name, meta_dict=None):
        '''
        Upload slave file to Storage server.
        arguments:
        @filename: string, local file name
        @remote_file_id: string, remote file id
        @prefix_name: string
        @meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        }
        @return dictionary {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        }
        '''
        isfile, errmsg = await async_fdfs_check_file(filename)
        if not isfile:
            raise DataError(errmsg + '(uploading slave)')
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(uploading slave)')
        if not prefix_name:
            raise DataError('[-] Error: prefix_name can not be null.')
        group_name, remote_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv = await tc.tracker_query_storage_stor_with_group(group_name)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            try:
                ret_dict = await store.storage_upload_slave_by_filename(tc, store_serv,
                                                                        filename, prefix_name, remote_filename,
                                                                        meta_dict=meta_dict)
            except:
                raise
            ret_dict['Status'] = 'Upload slave file successed.'
            return ret_dict

    async def upload_slave_by_file(self, filename, remote_file_id, prefix_name, meta_dict=None):
        '''
        Upload slave file to Storage server.
        arguments:
        @filename: string, local file name
        @remote_file_id: string, remote file id
        @prefix_name: string
        @meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        }
        @return dictionary {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        }
        '''
        isfile, errmsg = await async_fdfs_check_file(filename)
        if not isfile:
            raise DataError(errmsg + '(uploading slave)')
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(uploading slave)')
        if not prefix_name:
            raise DataError('[-] Error: prefix_name can not be null.')
        group_name, remote_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv = await tc.tracker_query_storage_stor_with_group(group_name)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            try:
                ret_dict = await store.storage_upload_slave_by_file(tc, store_serv,
                                                                    filename, prefix_name, remote_filename,
                                                                    meta_dict=meta_dict)
            except:
                raise
            ret_dict['Status'] = 'Upload slave file successed.'
            return ret_dict

    async def upload_slave_by_buffer(self, filebuffer, remote_file_id, meta_dict=None, file_ext_name=None):
        '''
        Upload slave file by buffer
        arguments:
        @filebuffer: string
        @remote_file_id: string
        @meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        }
        @return dictionary {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        }
        '''
        if not filebuffer:
            raise DataError('[-] Error: argument filebuffer can not be null.')
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(uploading slave)')
        group_name, remote_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_update(group_name, remote_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_upload_slave_by_buffer(tc, store_serv, filebuffer, remote_filename, meta_dict,
                                                        file_ext_name)

    async def upload_appender_by_filename(self, local_filename, meta_dict=None):
        '''
        Upload an appender file by filename.
        arguments:
        @local_filename: string
        @meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        }    Notice: it can be null
        @return dict {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        } if success else None
        '''
        isfile, errmsg = await async_fdfs_check_file(local_filename)
        if not isfile:
            raise DataError(errmsg + '(uploading appender)')
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_stor_without_group()
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_upload_appender_by_filename(tc, store_serv, local_filename, meta_dict)

    async def upload_appender_by_file(self, local_filename, meta_dict=None):
        '''
        Upload an appender file by file.
        arguments:
        @local_filename: string
        @meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        }    Notice: it can be null
        @return dict {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        } if success else None
        '''
        isfile, errmsg = await async_fdfs_check_file(local_filename)
        if not isfile:
            raise DataError(errmsg + '(uploading appender)')
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_stor_without_group()
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_upload_appender_by_file(tc, store_serv, local_filename, meta_dict)

    async def upload_appender_by_buffer(self, filebuffer, file_ext_name=None, meta_dict=None):
        '''
        Upload a buffer to Storage server.
        arguments:
        @filebuffer: string
        @file_ext_name: string, can be null
        @meta_dict: dictionary, can be null
        @return dict {
            'group_name'      : group_name,
            'file_id'  : remote_file_id,
            'file_name'  : file_name,
            'file_size'   : upload_size,
            'storage_ip'      : storage_ip
        } if success else None
        '''
        if not filebuffer:
            raise DataError('[-] Error: argument filebuffer can not be null.')
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_stor_without_group()
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_upload_appender_by_buffer(tc, store_serv, filebuffer, meta_dict, file_ext_name)

    async def delete_file(self, remote_file_id):
        '''
        Delete a file from Storage server.
        arguments:
        @remote_file_id: string, file_id of file that is on storage server
        @return tuple ('Delete file successed.', remote_file_id, storage_ip)
        '''
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(in delete file)')
        group_name, remote_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_update(group_name, remote_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_delete_file(store_serv, remote_filename)

    async def download_to_file(self, local_filename, remote_file_id, offset=0, down_bytes=0):
        '''
        Download a file from Storage server.
        arguments:
        @local_filename: string, local name of file 
        @remote_file_id: string, file_id of file that is on storage server
        @offset: long
        @downbytes: long
        @return dict {
            'file_id' : remote_filename,
            'content' : local_filename or buffer,
            'download_size'   : download_size,
            'storage_ip'      : storage_ip
        }
        '''
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(in download file)')
        group_name, remote_filename = tmp
        if not offset:
            file_offset = int(offset)
        if not down_bytes:
            download_bytes = int(down_bytes)
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_fetch(group_name, remote_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_download_to_file(store_serv, local_filename, file_offset, download_bytes,
                                                        remote_filename)

    async def download_to_generator(self, remote_file_id, offset=0, down_bytes=0):
        '''
        Download a file from Storage server.
        arguments:
        @remote_file_id: string, file_id of file that is on storage server
        @offset: long
        @downbytes: long
        @return generator
        '''
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(in download file)')
        group_name, remote_filename = tmp
        file_offset = 0
        download_bytes = 0
        if not offset:
            file_offset = int(offset)
        if not down_bytes:
            download_bytes = int(down_bytes)
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_fetch(group_name, remote_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            async for buffer in store.storage_download_to_generator(store_serv, file_offset, download_bytes,
                                                        remote_filename):
                yield buffer

    async def download_to_buffer(self, remote_file_id, offset=0, down_bytes=0):
        '''
        Download a file from Storage server and store in buffer.
        arguments:
        @remote_file_id: string, file_id of file that is on storage server
        @offset: long
        @down_bytes: long
        @return dict {
            'file_id' : remote_filename,
            'content' : buffer,
            'download_size'   : download_size,
            'storage_ip'      : storage_ip
        }
        '''
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(in download file)')
        group_name, remote_filename = tmp
        if not offset:
            file_offset = int(offset)
        if not down_bytes:
            download_bytes = int(down_bytes)
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_fetch(group_name, remote_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            file_buffer = None
            return await store.storage_download_to_buffer(store_serv, file_buffer, file_offset, download_bytes,
                                                    remote_filename)

    async def list_one_group(self, group_name):
        '''
        List one group information.
        arguments:
        @group_name: string, group name will be list
        @return Group_info,  instance
        '''
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        return await tc.tracker_list_one_group(group_name)

    async def list_servers(self, group_name, storage_ip=None):
        '''
        List all storage servers information in a group
        arguments:
        @group_name: string
        @return dictionary {
            'Group name' : group_name,
            'Servers'    : server list,
        }
        '''
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        return await tc.tracker_list_servers(group_name, storage_ip)

    async def list_all_groups(self):
        '''
        List all group information.
        @return dictionary {
            'Groups count' : group_count,
            'Groups'       : list of groups
        }
        '''
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        return await tc.tracker_list_all_groups()

    async def get_meta_data(self, remote_file_id):
        '''
        Get meta data of remote file.
        arguments:
        @remote_fileid: string, remote file id
        @return dictionary, meta data
        '''
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(in get meta data)')
        group_name, remote_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_update(group_name, remote_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_get_metadata(tc, store_serv, remote_filename)

    async def set_meta_data(self, remote_file_id, meta_dict, op_flag=STORAGE_SET_METADATA_FLAG_OVERWRITE):
        '''
        Set meta data of remote file.
        arguments:
        @remote_file_id: string
        @meta_dict: dictionary
        @op_flag: char, 'O' for overwrite, 'M' for merge
        @return dictionary {
            'Status'     : status,
            'Storage IP' : storage_ip
        }
        '''
        tmp = split_remote_fileid(remote_file_id)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(in set meta data)')
        group_name, remote_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        try:
            store_serv = await tc.tracker_query_storage_update(group_name, remote_filename)
            async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
                status = await store.storage_set_metadata(store_serv, remote_filename, meta_dict)
        except (ConnectionError, ResponseError, DataError):
            raise
        # if status == 2:
        #    raise DataError('[-] Error: remote file %s is not exist.' % remote_file_id)
        if status != 0:
            raise DataError('[-] Error: %d, %s' % (status, os.strerror(status)))
        ret_dict = {}
        ret_dict['Status'] = 'Set meta data success.'
        ret_dict['Storage IP'] = store_serv.ip_addr
        return ret_dict

    async def append_by_filename(self, local_filename, remote_fileid):
        isfile, errmsg = await async_fdfs_check_file(local_filename)
        if not isfile:
            raise DataError(errmsg + '(append)')
        tmp = split_remote_fileid(remote_fileid)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(append)')
        group_name, appended_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_update(group_name, appended_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_append_by_filename(tc, store_serv, local_filename, appended_filename)

    async def append_by_file(self, local_filename, remote_fileid):
        isfile, errmsg = await async_fdfs_check_file(local_filename)
        if not isfile:
            raise DataError(errmsg + '(append)')
        tmp = split_remote_fileid(remote_fileid)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(append)')
        group_name, appended_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_update(group_name, appended_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_append_by_file(tc, store_serv, local_filename, appended_filename)

    async def append_by_buffer(self, file_buffer, remote_fileid):
        if not file_buffer:
            raise DataError('[-] Error: file_buffer can not be null.')
        tmp = split_remote_fileid(remote_fileid)
        if not tmp:
            raise DataError('[-] Error: remote_file_id is invalid.(append)')
        group_name, appended_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_update(group_name, appended_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_append_by_buffer(tc, store_serv, file_buffer, appended_filename)

    async def truncate_file(self, truncated_filesize, appender_fileid):
        '''
        Truncate file in Storage server.
        arguments:
        @truncated_filesize: long
        @appender_fileid: remote_fileid
        @return: dictionary {
            'Status'     : 'Truncate successed.',
            'Storage IP' : storage_ip
        }
        '''
        trunc_filesize = int(truncated_filesize)
        tmp = split_remote_fileid(appender_fileid)
        if not tmp:
            raise DataError('[-] Error: appender_fileid is invalid.(truncate)')
        group_name, appender_filename = tmp
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv = await tc.tracker_query_storage_update(group_name, appender_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_truncate_file(tc, store_serv, trunc_filesize, appender_filename)

    async def modify_by_filename(self, filename, appender_fileid, offset=0):
        '''
        Modify a file in Storage server by file.
        arguments:
        @filename: string, local file name
        @offset: long, file offset
        @appender_fileid: string, remote file id
        @return: dictionary {
            'Status'     : 'Modify successed.',
            'Storage IP' : storage_ip
        }
        '''
        isfile, errmsg = await async_fdfs_check_file(filename)
        if not isfile:
            raise DataError(errmsg + '(modify)')
        filesize = os.stat(filename).st_size
        tmp = split_remote_fileid(appender_fileid)
        if not tmp:
            raise DataError('[-] Error: remote_fileid is invalid.(modify)')
        group_name, appender_filename = tmp
        if not offset:
            file_offset = int(offset)
        else:
            file_offset = 0
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv: Storage_server = await tc.tracker_query_storage_update(group_name, appender_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_modify_by_filename(tc, store_serv, filename, file_offset, filesize, appender_filename)

    async def modify_by_file(self, filename, appender_fileid, offset=0):
        '''
        Modify a file in Storage server by file.
        arguments:
        @filename: string, local file name
        @offset: long, file offset
        @appender_fileid: string, remote file id
        @return: dictionary {
            'Status'     : 'Modify successed.',
            'Storage IP' : storage_ip
        }
        '''
        isfile, errmsg = await async_fdfs_check_file(filename)
        if not isfile:
            raise DataError(errmsg + '(modify)')
        filesize = os.stat(filename).st_size
        tmp = split_remote_fileid(appender_fileid)
        if not tmp:
            raise DataError('[-] Error: remote_fileid is invalid.(modify)')
        group_name, appender_filename = tmp
        if not offset:
            file_offset = int(offset)
        else:
            file_offset = 0
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv = await tc.tracker_query_storage_update(group_name, appender_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_modify_by_file(tc, store_serv, filename, file_offset, filesize, appender_filename)

    async def modify_by_buffer(self, filebuffer, appender_fileid, offset=0):
        '''
        Modify a file in Storage server by buffer.
        arguments:
        @filebuffer: string, file buffer
        @offset: long, file offset
        @appender_fileid: string, remote file id
        @return: dictionary {
            'Status'     : 'Modify successed.',
            'Storage IP' : storage_ip
        }
        '''
        if not filebuffer:
            raise DataError('[-] Error: filebuffer can not be null.(modify)')
        filesize = len(filebuffer)
        tmp = split_remote_fileid(appender_fileid)
        if not tmp:
            raise DataError('[-] Error: remote_fileid is invalid.(modify)')
        group_name, appender_filename = tmp
        if not offset:
            file_offset = int(offset)
        else:
            file_offset = 0
        tc = Async_Tracker_Client(self.tracker_pool, self.store_path_index)
        store_serv = await tc.tracker_query_storage_update(group_name, appender_filename)
        async with Async_Storage_Client(store_serv.ip_addr, store_serv.port,
                                        self.connect_timeout, self.network_timeout) as store:
            return await store.storage_modify_by_buffer(tc, store_serv, filebuffer, file_offset, filesize, appender_filename)
