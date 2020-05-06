"""
This is the second version of file for retaining all common settings and calling from reusable functions
"""
import multiprocessing
import struct
import socket
import time

lru_ip = { "MU-A_IP": "10.1.1.1", "MU-B_IP": "10.1.1.2", "IFUC1_IP": "10.1.1.3", "IFUC2_IP":"10.1.1.4","CSC_IP": "10.1.1.61",
           "CSLS1_IP": "10.1.1.62", "CSLS2_IP": "10.1.1.63", "CSVG_IP": "10.1.1.64",
           "CSLR_IP": "10.1.1.68", "CSIE1_IP": "10.1.1.69", "CSIE2_IP": "10.1.1.70",
           "DVC_IP": "10.1.1.71", "DVLS_IP": "10.1.1.72", "DVVP_IP": "10.1.1.73",
           "DVLR_IP": "10.1.1.74", "DVVD_IP": "10.1.1.75"
           }

lru_port = { "MU_port": 10001, "IFUC1_port": 10010, "IFUC2_port": 10020 }

lru_id = { "MU_ID": 0x00, "MU-A_ID": 0x01, "MU-B_ID": 0x02, "IFUC1_ID": 0x64, "IFUC2_ID":0x65,"CSC_ID": 0x75, "CSLS1_ID": 0x76,
           "CSLS2_ID": 0x77, "CSVG_ID": 0x78, "CSLR_ID": 0x79, "CSIE1_ID": 0x80, "CSIE2_ID": 0x81,
           "DVC_ID": 0x85, "DVLS_ID": 0x84, "DVVP_ID": 0x86, "DVLR_ID": 0x83, "DVVD_ID": 0x87
           }

lru_hlt_msgcode = dict( IFUC_HC=0x2101, CSC_HC=0x4201, CSLS_HC=4301, CSVG_HC=4001, CSLR_HC=4101, CSIE_HC=4201,
                        DVC_HC=5201, DVLS_ID=5301,
                        DVVP_HC=5401, DVLR_HC=5101, DVVD_HC=5501 )

lru_sw_msgcode = dict( IFUC_SC=0x2104, CSC_SC=0x4210, CSLS_SC=4310, CSVG_SC=4002, CSIL_SC=4003, CSTID_SC=4004,
                       CSVP_SC=4005, CSLR_SC=4104,
                       CSIE_SC=4202, DVC_SC=5210, DVLS_SC=5310, DVVP_SC=5410, DVLR_SC=5104, DVVD_SC=5510 )

lru_lnk_slt_msgcode = dict( CSLS_LNK=0x4414, CSLS_SLT=4314, CSLR_LNK=4214, CSLR_SLT=4114 )

hdr_spare = 0x00
msg_counter = 0
msg_lnt_hlt = 20
msg_lnt_sw = 62
lru_msg_param = dict( param1=0x0000, param2=0x0000, param3=0x0000, param4=0x0000, param5=0x0000, param6=0x0000 )
lru_sw_param = dict( param1=0x0000, param2=0x0000, param3=0x0000, param4=0x0000 )

param1 = lru_msg_param['param1']
param2 = lru_msg_param['param2']
param3 = lru_msg_param['param3']
param4 = lru_msg_param['param4']
param5 = lru_msg_param['param5']
param6 = lru_msg_param['param6']


class MulticastSend:
    ''':arg
    This class will have all general setting required to load to LRUs
    '''

    def __init__( self ):

        self.dest_ip = lru_ip["MU-A_IP"]
        self.dest_port = lru_port["MU_port"]
        self.dest_address = (self.dest_ip, self.dest_port)
        self.lock = multiprocessing.Lock()

    def multicastconfig( self, source_address, data ):

        self.lock.acquire()

        self.source_address = source_address
        self.data = data

        multicast_group = '226.10.0.1'

        # Create the socket
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

        # Bind to the server address
        sock.bind( self.source_address )

        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton( multicast_group )
        mreq = struct.pack( '4sL', group, socket.INADDR_ANY )
        sock.setsockopt( socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq )

        if not data is None:
            try:
                sock.sendto( data, self.dest_address )
                print( data )
            except Exception as e:
                print( e )

            finally:
                self.lock.release()


multicast_send = MulticastSend()


class IFUCMsg( MulticastSend ):

    def __init__( self ):
        MulticastSend.__init__( self )

    def IFUChltmsg( self, source_address, src_id, msgcnt, param1, param2 ):

        self.lock.acquire()

        self.source_address = source_address
        self.dstid = lru_id['MU-A_ID']
        self.srcid = src_id
        self.msgcnt = msgcnt
        self.msgcode = lru_hlt_msgcode['IFUC_HC']
        self.hdrspr = hdr_spare
        self.msglnt = msg_lnt_hlt

        self.param1 = param1
        self.param2 = param2
        self.param3 = param3  # from global variable
        self.param4 = param4  # from global variable
        self.param5 = param5  # from global variable
        self.param6 = param6  # from global variable

        try:
            self.data = struct.pack( '2BH2B7H', self.srcid, self.dstid, self.msgcode, self.msgcnt, self.hdrspr,
                                     self.msglnt, self.param1, self.param2, self.param3, self.param4, self.param5,
                                     self.param6 )
        except Exception as e:
            print( e )

        ifuchltmsg = MulticastSend()
        ifuchltmsg.multicastconfig( source_address=self.source_address, data=self.data )
        self.lock.release()
        return ifuchltmsg

    def IFUCswmsg( self, source_address, src_id, msgcnt, param1, param2, param3, param4 ):

        self.lock.acquire()
        self.source_address = source_address
        self.dstid = lru_id['MU-A_ID']
        self.srcid = src_id
        self.msgcnt = msgcnt
        self.msgcode = lru_sw_msgcode['IFUC_SC']
        self.hdrspr = hdr_spare
        self.msglnt = msg_lnt_sw

        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.param4 = param4

        try:
            self.data = struct.pack( '2BH2BH2BH50s', self.srcid, self.dstid, self.msgcode, self.msgcnt, self.hdrspr,
                                     self.msglnt, self.param1, self.param2, self.param3, self.param4 )
        except Exception as e:
            print( e )

        ifucswmsg = MulticastSend()
        ifucswmsg.multicastconfig( source_address=self.source_address, data=self.data )

        self.lock.release()
        return ifucswmsg

    def IFUC1hltmsg( self ):
        ifuc1hltmsgcnt = 0

        while True:

            self.src_ip = lru_ip['IFUC1_IP']
            self.src_port = lru_port['IFUC1_port']
            self.src_add = (self.src_ip, self.src_port)
            self.src_id = lru_id['IFUC1_ID']
            self.ifuc1param1 = 0x0001
            self.ifuc1param2 = 0x0000

            if ifuc1hltmsgcnt <= 255:
                ifuc1hltmsgcnt += 1
            else:
                ifuc1hltmsgcnt = 0

            ifucmsg = IFUCMsg()
            ifucmsg.IFUChltmsg( source_address=self.src_add, src_id=self.src_id, msgcnt=ifuc1hltmsgcnt,
                                param1=self.ifuc1param1, param2=self.ifuc1param2 )

            time.sleep( 1 )

    def IFUC2hltmsg( self ):
        ifuc2hltmsgcnt = 0

        while True:

            self.src_ip = lru_ip['IFUC2_IP']
            self.src_port = lru_port['IFUC2_port']
            self.src_add = (self.src_ip, self.src_port)
            self.src_id = lru_id['IFUC2_ID']
            self.ifuc2param1 = 0x0001
            self.ifuc2param2 = 0x0001

            if ifuc2hltmsgcnt <= 255:
                ifuc2hltmsgcnt += 1
            else:
                ifuc2hltmsgcnt = 0

            ifucmsg = IFUCMsg()
            ifucmsg.IFUChltmsg( source_address=self.src_add, src_id=self.src_id, msgcnt=ifuc2hltmsgcnt,
                                param1=self.ifuc2param1, param2=self.ifuc2param2 )

            time.sleep( 1 )

    def IFUC1swmsg( self ):
        ifuc1swmsgcnt = 0

        while True:

            self.src_ip = lru_ip['IFUC1_IP']
            self.src_port = lru_port['IFUC1_port']
            self.src_add = (self.src_ip, self.src_port)
            self.src_id = lru_id['IFUC1_ID']
            self.ifuc1param1 = 30
            self.ifuc1param2 = 4
            self.ifuc1param3 = 2020
            self.ifuc1param4 = b'IFUC1 Ver 2.2'

            if ifuc1swmsgcnt <= 255:
                ifuc1swmsgcnt += 1
            else:
                ifuc1swmsgcnt = 0

            ifucmsg = IFUCMsg()
            ifucmsg.IFUCswmsg( source_address=self.src_add, src_id=self.src_id, msgcnt=ifuc1swmsgcnt,
                               param1=self.ifuc1param1,
                               param2=self.ifuc1param2, param3=self.ifuc1param3, param4=self.ifuc1param4 )

            time.sleep( 300 )

    def IFUC2swmsg( self ):
        ifuc2swmsgcnt = 0

        while True:

            self.src_ip = lru_ip['IFUC2_IP']
            self.src_port = lru_port['IFUC2_port']
            self.src_add = (self.src_ip, self.src_port)
            self.src_id = lru_id['IFUC2_ID']
            self.ifuc2param1 = 28
            self.ifuc2param2 = 4
            self.ifuc2param3 = 2020
            self.ifuc2param4 = b'IFUC2 Ver 4.8'

            if ifuc2swmsgcnt <= 255:
                ifuc2swmsgcnt += 1
            else:
                ifuc2swmsgcnt = 0

            ifucmsg = IFUCMsg()
            ifucmsg.IFUCswmsg( source_address=self.src_add, src_id=self.src_id, msgcnt=ifuc2swmsgcnt,
                               param1=self.ifuc2param1,
                               param2=self.ifuc2param2, param3=self.ifuc2param3, param4=self.ifuc2param4 )

            time.sleep( 300 )

if __name__ == '__main__':

    ifucmsg = IFUCMsg()

    ifuc1hltmtrd = multiprocessing.Process( target=ifucmsg.IFUC1hltmsg )
    ifuc2hltmtrd = multiprocessing.Process( target=ifucmsg.IFUC2hltmsg )
    ifuc1swtrd = multiprocessing.Process( target=ifucmsg.IFUC1swmsg )
    ifuc2swtrd = multiprocessing.Process( target=ifucmsg.IFUC2swmsg)

    ifuc1hltmtrd.start()
    ifuc2hltmtrd.start()
    ifuc1swtrd.start()
    ifuc2swtrd.start()
