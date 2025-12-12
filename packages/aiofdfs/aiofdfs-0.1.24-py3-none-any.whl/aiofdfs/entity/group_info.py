from ..async_fdfs_protol import *
from ..exceptions import DataError
from ..util import appromix


class Group_info(object):
    def __init__(self):
        self.group_name = ''
        self.totalMB = ''
        self.freeMB = ''
        self.trunk_freeMB = ''
        self.count = 0
        self.storage_port = 0
        self.store_http_port = 0
        self.active_count = 0
        self.curr_write_server = 0
        self.store_path_count = 0
        self.subdir_count_per_path = 0
        self.curr_trunk_file_id = 0
        self.fmt = '!%ds 11Q' % (FDFS_GROUP_NAME_MAX_LEN + 1)

    def __str__(self):

        s = 'Group information:\n'
        s += '\tgroup name = %s\n' % self.group_name
        s += '\ttotal disk space = %s\n' % self.totalMB
        s += '\tdisk free space = %s\n' % self.freeMB
        s += '\ttrunk free space = %s\n' % self.trunk_freeMB
        s += '\tstorage server count = %d\n' % self.count
        s += '\tstorage port = %d\n' % self.storage_port
        s += '\tstorage HTTP port = %d\n' % self.store_http_port
        s += '\tactive server count = %d\n' % self.active_count
        s += '\tcurrent write server index = %d\n' % self.curr_write_server
        s += '\tstore path count = %d\n' % self.store_path_count
        s += '\tsubdir count per path = %d\n' % self.subdir_count_per_path
        s += '\tcurrent trunk file id = %d\n' % self.curr_trunk_file_id
        return s

    def set_info(self, bytes_stream):
        (group_name, totalMB, freeMB, trunk_freeMB, self.count, self.storage_port, self.store_http_port,
         self.active_count, self.curr_write_server, self.store_path_count, self.subdir_count_per_path,
         self.curr_trunk_file_id) = struct.unpack(self.fmt, bytes_stream)
        try:
            self.group_name = group_name.strip(b'\x00')
            self.freeMB = appromix(freeMB, FDFS_SPACE_SIZE_BASE_INDEX)
            self.totalMB = appromix(totalMB, FDFS_SPACE_SIZE_BASE_INDEX)
            self.trunk_freeMB = appromix(trunk_freeMB, FDFS_SPACE_SIZE_BASE_INDEX)
        except ValueError:
            raise DataError('[-] Error disk space overrun, can not represented it.')

    def get_fmt_size(self):
        return struct.calcsize(self.fmt)