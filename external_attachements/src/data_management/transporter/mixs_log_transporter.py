#!/usr/bin/env python

import logging
import glob
import json
import sys,os
import re
import time
import datetime as dt
import os
import zipfile
import socket
from transporter import Transporter
from collections import defaultdict
from ftplib import FTP


class MixsLogTransporter(Transporter):
    """
    """
    local_data_path = "/data/mixs_logs"
        
    # ftp
    host = "43.196.176.103"
    user = "stcssg"
    passwd = "0p1eh1sG"
    remote_path = "/stc-ftp/SSG/HCDM/WP2/"
    tmp_path = "/tmp"

    # rsync
    remote_user = "re-user"
    remote_host = "43.4.16.123"
    remote_data_base_path = "/data"
    ssh_skey_path = "/home/mixs/.ssh/id_rsa"
    rsync = os.popen("which rsync").read().strip()
    rsync_archive_opt = "-a"
    rsync_exclude_opt = "--exclude */*/all/"
    
    def __init__(self, local_data_path = local_data_path, remote_data_base_path = remote_data_base_path):
        """
        """
        
        # logger
        logger = logging.getLogger("MixsLogTransporter")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        self.logger = logger
        
        self.logger.info("init starts")

        # init base class 
        super(MixsLogTransporter, self).__init__()

        self.local_data_path = local_data_path
        self.remote_data_base_path = remote_data_base_path
        
        self.logger.info("init finished")

        pass

    def transport(self, ):
        """
        """
        
        self.logger.info("transport starts")
        st = time.time()

        # archive
        self._archive()
        
        # transport
        self._transport()

        et = time.time()
        self.logger.info("%f [s]" % (et - st))
        self.logger.info("transport finshed")

        pass

    def _transport(self, ):
        """
        """
        
        ftp = FTP(host=self.host, user=self.user, passwd=self.passwd)
        ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
        ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)

        ftp.cwd(self.remote_path)
        fpin = open(self.save_path, "rb")
        os.chdir(self.tmp_path)
        ftp.storbinary("STOR %s" % (self.save_file), fpin)
        fpin.close()
        ftp.quit()
        
        pass

    def transport_to_local(self, ):
        """
        transport local data to remote server with rsync.
        zipping is not needed.
        """
        
        self.logger.info("transport_to_local starts")
        st = time.time()

        # transport
        self._transport_to_local()

        et = time.time()
        self.logger.info("%f [s]" % (et - st))
        self.logger.info("transport_to_local finshed")

        pass

    def _transport_to_local(self, ):
        """
        transport local data to remote server with rsync.
        """
        ssh_i = "'ssh -i %s'" % (self.ssh_skey_path)
        rsync_command = "%s -e %s %s %s %s %s@%s:%s" % (self.rsync,
                                                     ssh_i,
                                                     self.rsync_archive_opt,
                                                     self.rsync_exclude_opt,
                                                     self.local_data_path, 
                                                     self.remote_user,
                                                     self.remote_host,
                                                     self.remote_data_base_path)

        self.logger.info(rsync_command)

        os.system(rsync_command)

        pass


    def _archive(self,):
        """
        """

        data_dir = self.local_data_path.split("/")[-1]
        save_file = "%s_%s.zip" % (data_dir, dt.datetime.fromtimestamp(time.time()).strftime("%Y%m%d"))
        save_path = "%s/%s" % (self.tmp_path, save_file)
        self.save_path = save_path
        self.save_file = save_file
        if os.path.exists(save_path):
            os.remove(save_path)
            pass
        
        zf = zipfile.ZipFile(save_path, "w", allowZip64=True)
        self._zipdir(self.local_data_path, zf)
        
        pass
        
    def _zipdir(self, target_path, zf):
        for root, dirs, files in os.walk(target_path):
            for fin in files:
                zf.write(os.path.join(root, fin))

def main():
    #transporter = MixsLogTransporter()
    #transporter.transport()

    local_data_path = "/data/mixs_launcher_logs"
    remote_data_base_path = "/data"
    
    transporter = MixsLogTransporter(local_data_path=local_data_path, remote_data_base_path=remote_data_base_path)
    transporter.transport_to_local()

if __name__ == '__main__':
    main()
