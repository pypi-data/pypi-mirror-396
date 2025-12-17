from petl.io.remotes import RemoteSource
from paramiko import SSHClient, AutoAddPolicy

class SftpServer(object):
    def __init__(self, hostname, base_path="", **kwargs):
        self.hostname = hostname
        self.remote_args = kwargs
    def open(self, file_path):
        return RemoteSource(
            f"sftp://{ self.hostname }{ file_path }",
            **self.remote_args
        )
    def listdir(self, *args, **kwargs):
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(self.hostname, **self.remote_args)
        with ssh.open_sftp() as sftp:
            list = sftp.listdir(*args, **kwargs)
        ssh.close()
        return list
    def listdir_attr(self, *args, **kwargs):
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(self.hostname, **self.remote_args)
        with ssh.open_sftp() as sftp:
            list = sftp.listdir_attr(*args, **kwargs)
        ssh.close()
        return list