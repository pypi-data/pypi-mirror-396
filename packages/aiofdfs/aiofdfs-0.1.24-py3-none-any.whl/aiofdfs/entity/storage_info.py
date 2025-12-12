from datetime import datetime

from ..async_fdfs_protol import *
from ..util import appromix


def parse_storage_status(status_code):
    try:
        ret = {
            FDFS_STORAGE_STATUS_INIT: lambda: 'INIT',
            FDFS_STORAGE_STATUS_WAIT_SYNC: lambda: 'WAIT_SYNC',
            FDFS_STORAGE_STATUS_SYNCING: lambda: 'SYNCING',
            FDFS_STORAGE_STATUS_IP_CHANGED: lambda: 'IP_CHANGED',
            FDFS_STORAGE_STATUS_DELETED: lambda: 'DELETED',
            FDFS_STORAGE_STATUS_OFFLINE: lambda: 'OFFLINE',
            FDFS_STORAGE_STATUS_ONLINE: lambda: 'ONLINE',
            FDFS_STORAGE_STATUS_ACTIVE: lambda: 'ACTIVE',
            FDFS_STORAGE_STATUS_RECOVERY: lambda: 'RECOVERY'
        }[status_code]()
    except KeyError:
        ret = 'UNKNOW'
    return ret


class Storage_info(object):
    def __init__(self):
        self.status = 0
        self.id = ''
        self.ip_addr = ''
        self.domain_name = ''
        self.src_id = ''
        self.version = ''
        self.join_time = datetime.fromtimestamp(0).isoformat()
        self.up_time = datetime.fromtimestamp(0).isoformat()
        self.totalMB = ''
        self.freeMB = ''
        self.upload_prio = 0
        self.store_path_count = 0
        self.subdir_count_per_path = 0
        self.curr_write_path = 0
        self.storage_port = 23000
        self.storage_http_port = 80
        self.alloc_count = 0
        self.current_count = 0
        self.max_count = 0
        self.total_upload_count = 0
        self.success_upload_count = 0
        self.total_append_count = 0
        self.success_append_count = 0
        self.total_modify_count = 0
        self.success_modify_count = 0
        self.total_truncate_count = 0
        self.success_truncate_count = 0
        self.total_setmeta_count = 0
        self.success_setmeta_count = 0
        self.total_del_count = 0
        self.success_del_count = 0
        self.total_download_count = 0
        self.success_download_count = 0
        self.total_getmeta_count = 0
        self.success_getmeta_count = 0
        self.total_create_link_count = 0
        self.success_create_link_count = 0
        self.total_del_link_count = 0
        self.success_del_link_count = 0
        self.total_upload_bytes = 0
        self.success_upload_bytes = 0
        self.total_append_bytes = 0
        self.success_append_bytes = 0
        self.total_modify_bytes = 0
        self.success_modify_bytes = 0
        self.total_download_bytes = 0
        self.success_download_bytes = 0
        self.total_sync_in_bytes = 0
        self.success_sync_in_bytes = 0
        self.total_sync_out_bytes = 0
        self.success_sync_out_bytes = 0
        self.total_file_open_count = 0
        self.success_file_open_count = 0
        self.total_file_read_count = 0
        self.success_file_read_count = 0
        self.total_file_write_count = 0
        self.success_file_write_count = 0
        self.last_source_sync = datetime.fromtimestamp(0).isoformat()
        self.last_sync_update = datetime.fromtimestamp(0).isoformat()
        self.last_synced_time = datetime.fromtimestamp(0).isoformat()
        self.last_heartbeat_time = datetime.fromtimestamp(0).isoformat()
        self.if_trunk_server = ''
        # fmt = |-status(1)-ipaddr(16)-domain(128)-srcipaddr(16)-ver(6)-52*8-|
        self.fmt = '!B 16s 16s 128s 16s 6s 10Q 4s4s4s 42Q?'

    def set_info(self, bytes_stream):
        (self.status, self.id, ip_addr, domain_name, self.src_id, version, join_time, up_time, totalMB, freeMB,
         self.upload_prio, self.store_path_count, self.subdir_count_per_path, self.curr_write_path, self.storage_port,
         self.storage_http_port, self.alloc_count, self.current_count, self.max_count, self.total_upload_count,
         self.success_upload_count, self.total_append_count, self.success_append_count, self.total_modify_count,
         self.success_modify_count, self.total_truncate_count, self.success_truncate_count, self.total_setmeta_count,
         self.success_setmeta_count, self.total_del_count, self.success_del_count, self.total_download_count,
         self.success_download_count, self.total_getmeta_count, self.success_getmeta_count,
         self.total_create_link_count, self.success_create_link_count, self.total_del_link_count,
         self.success_del_link_count, self.total_upload_bytes, self.success_upload_bytes, self.total_append_bytes,
         self.total_append_bytes, self.total_modify_bytes, self.success_modify_bytes, self.total_download_bytes,
         self.success_download_bytes, self.total_sync_in_bytes, self.success_sync_in_bytes, self.total_sync_out_bytes,
         self.success_sync_out_bytes, self.total_file_open_count, self.success_file_open_count,
         self.total_file_read_count, self.success_file_read_count, self.total_file_write_count,
         self.success_file_write_count, last_source_sync, last_sync_update, last_synced_time, last_heartbeat_time,
         self.if_trunk_server,) = struct.unpack(self.fmt, bytes_stream)
        try:
            self.ip_addr = ip_addr.strip(b'\x00')
            self.domain_name = domain_name.strip(b'\x00')
            self.version = version.strip(b'\x00')
            self.totalMB = appromix(totalMB, FDFS_SPACE_SIZE_BASE_INDEX)
            self.freeMB = appromix(freeMB, FDFS_SPACE_SIZE_BASE_INDEX)
        except ValueError as e:
            raise ResponseError('[-] Error: disk space overrun, can not represented it.')
        self.join_time = datetime.fromtimestamp(join_time).isoformat()
        self.up_time = datetime.fromtimestamp(up_time).isoformat()
        self.last_source_sync = datetime.fromtimestamp(last_source_sync).isoformat()
        self.last_sync_update = datetime.fromtimestamp(last_sync_update).isoformat()
        self.last_synced_time = datetime.fromtimestamp(last_synced_time).isoformat()
        self.last_heartbeat_time = datetime.fromtimestamp(last_heartbeat_time).isoformat()
        return True

    def __str__(self):
        '''Transform to readable string.'''

        s = 'Storage information:\n'
        s += '\tip_addr = %s (%s)\n' % (self.ip_addr, parse_storage_status(self.status))
        s += '\thttp domain = %s\n' % self.domain_name
        s += '\tversion = %s\n' % self.version
        s += '\tjoin time = %s\n' % self.join_time
        s += '\tup time = %s\n' % self.up_time
        s += '\ttotal storage = %s\n' % self.totalMB
        s += '\tfree storage = %s\n' % self.freeMB
        s += '\tupload priority = %d\n' % self.upload_prio
        s += '\tstore path count = %d\n' % self.store_path_count
        s += '\tsubdir count per path = %d\n' % self.subdir_count_per_path
        s += '\tstorage port = %d\n' % self.storage_port
        s += '\tstorage HTTP port = %d\n' % self.storage_http_port
        s += '\tcurrent write path = %d\n' % self.curr_write_path
        s += '\tsource ip_addr = %s\n' % self.ip_addr
        s += '\tif_trunk_server = %d\n' % self.if_trunk_server
        s += '\ttotal upload count = %ld\n' % self.total_upload_count
        s += '\tsuccess upload count = %ld\n' % self.success_upload_count
        s += '\ttotal download count = %ld\n' % self.total_download_count
        s += '\tsuccess download count = %ld\n' % self.success_download_count
        s += '\ttotal append count = %ld\n' % self.total_append_count
        s += '\tsuccess append count = %ld\n' % self.success_append_count
        s += '\ttotal modify count = %ld\n' % self.total_modify_count
        s += '\tsuccess modify count = %ld\n' % self.success_modify_count
        s += '\ttotal truncate count = %ld\n' % self.total_truncate_count
        s += '\tsuccess truncate count = %ld\n' % self.success_truncate_count
        s += '\ttotal delete count = %ld\n' % self.total_del_count
        s += '\tsuccess delete count = %ld\n' % self.success_del_count
        s += '\ttotal set_meta count = %ld\n' % self.total_setmeta_count
        s += '\tsuccess set_meta count = %ld\n' % self.success_setmeta_count
        s += '\ttotal get_meta count = %ld\n' % self.total_getmeta_count
        s += '\tsuccess get_meta count = %ld\n' % self.success_getmeta_count
        s += '\ttotal create link count = %ld\n' % self.total_create_link_count
        s += '\tsuccess create link count = %ld\n' % self.success_create_link_count
        s += '\ttotal delete link count = %ld\n' % self.total_del_link_count
        s += '\tsuccess delete link count = %ld\n' % self.success_del_link_count
        s += '\ttotal upload bytes = %ld\n' % self.total_upload_bytes
        s += '\tsuccess upload bytes = %ld\n' % self.success_upload_bytes
        s += '\ttotal download bytes = %ld\n' % self.total_download_bytes
        s += '\tsuccess download bytes = %ld\n' % self.success_download_bytes
        s += '\ttotal append bytes = %ld\n' % self.total_append_bytes
        s += '\tsuccess append bytes = %ld\n' % self.success_append_bytes
        s += '\ttotal modify bytes = %ld\n' % self.total_modify_bytes
        s += '\tsuccess modify bytes = %ld\n' % self.success_modify_bytes
        s += '\ttotal sync_in bytes = %ld\n' % self.total_sync_in_bytes
        s += '\tsuccess sync_in bytes = %ld\n' % self.success_sync_in_bytes
        s += '\ttotal sync_out bytes = %ld\n' % self.total_sync_out_bytes
        s += '\tsuccess sync_out bytes = %ld\n' % self.success_sync_out_bytes
        s += '\ttotal file open count = %ld\n' % self.total_file_open_count
        s += '\tsuccess file open count = %ld\n' % self.success_file_open_count
        s += '\ttotal file read count = %ld\n' % self.total_file_read_count
        s += '\tsuccess file read count = %ld\n' % self.success_file_read_count
        s += '\ttotal file write count = %ld\n' % self.total_file_write_count
        s += '\tsucess file write count = %ld\n' % self.success_file_write_count
        s += '\tlast heartbeat time = %s\n' % self.last_heartbeat_time
        s += '\tlast source update = %s\n' % self.last_source_sync
        s += '\tlast sync update = %s\n' % self.last_sync_update
        s += '\tlast synced time = %s\n' % self.last_synced_time
        return s

    def get_fmt_size(self):
        return struct.calcsize(self.fmt)
