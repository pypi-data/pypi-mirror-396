import time
from . import ECanVci
from can.bus import BusABC
from can import Message
from typing import List
from loguru import logger

logger.disable(__name__)

class GcUsbCanBus(BusABC):
    dev_type = ECanVci.USBCAN2      # 设备类型
    opening_status = dict()         # 打开状态表

    @staticmethod
    def set_dev_type(dev_type):
        GcUsbCanBus.dev_type = dev_type

    @staticmethod
    def is_open(dev_index) -> bool:
        if dev_index in GcUsbCanBus.opening_status:
            return GcUsbCanBus.opening_status.get(dev_index)
        return False

    def _usbcan_init(self, baud, channel=0, dev_index=0, mode=0):
        dev = GcUsbCanBus.dev_type
        # 初始化参数
        config = ECanVci.INIT_CONFIG()
        config.AccCode = 0xE0000000   # 验收码。SJA1000的帧过滤验收码。
        config.AccMask = 0x1FFFFFFF   # 屏蔽码。SJA1000的帧过滤屏蔽码。屏蔽码推荐设置为0xFFFF FFFF，即全部接收。
        config.Filter = 0           # 滤波使能。0=不使能，1=使能。使能时，请参照SJA1000验收滤波器设置验收码和屏蔽码。
        config.Mode = mode             # 模式。=0为正常模式，=1为只听模式，=2为自发自收模式。

        baud_map = {
            1000: (0, 0x14),
            800: (0, 0x16),
            666: (0x80, 0xb6),
            500: (0, 0x1c),
            400: (0x80, 0xfa),
            250: (0x01, 0x1c),
            200: (0x81, 0xfa),
            125: (0x03, 0x1c),
            100: (0x04, 0x1c),
            80: (0x83, 0xff),
            50: (0x09, 0x1c),
        }
        a, b = baud_map[baud]
        config.Timing0 = a
        config.Timing1 = b

        if not GcUsbCanBus.is_open(dev_index):
            ret = ECanVci.OpenDevice(dev, dev_index, channel)
            logger.debug(f"OpenDevice {dev} {dev_index} {channel} = {ret}")
            if ret == 0:
                return -1
            GcUsbCanBus.opening_status[dev_index] = True

        ret = ECanVci.ResetCAN(dev, dev_index, channel)
        logger.debug(f"ResetCAN {dev} {dev_index} {channel} = {ret}")
        if ret == 0:
            return -4

        ret = ECanVci.InitCAN(dev, dev_index, channel, config)
        logger.debug(f"InitCAN {dev} {dev_index} {channel} {baud} = {ret}")
        if ret == 0:
            return -2

        ret = ECanVci.StartCAN(dev, dev_index, channel)
        logger.debug(f"StartCAN {dev} {dev_index} {channel} = {ret}")
        if ret == 0:
            return -3

        self.dev = dev
        self.dev_index = dev_index
        self.baud = baud
        self.channel = channel
        self.init_timestamp = time.time()       # 初始化时间

        return 0

    def __init__(self, channel=0, baud=500, dev_index=0, **kwargs):
        channel = int(channel)
        super(GcUsbCanBus, self).__init__(channel, **kwargs)
        self.channel_info = f"gc_[{dev_index}]_channel_[{channel}]"
        receive_own_messages = kwargs.get('receive_own_messages', False)
        if receive_own_messages:
            mode = 2
        else:
            mode = kwargs.get('mode', 0)
        ret = self._usbcan_init(baud, channel, dev_index, mode)
        if ret != 0:
            logger.error(f"init error code={ret}")
            raise Exception(f"init error code={ret}")

    def send(self, msg: List[Message]):
        if type(msg) is not list:
            msg = [msg]

        buflen = len(msg)
        frameinfo = (ECanVci.CAN_OBJ * buflen)()

        for i, c in enumerate(msg):
            frameinfo[i].ID = c.arbitration_id
            for j, v in enumerate(c.data):
                frameinfo[i].Data[j] = v
            frameinfo[i].DataLen = c.dlc
            frameinfo[i].SendType = 0
            frameinfo[i].RemoteFlag = c.is_remote_frame
            frameinfo[i].ExternFlag = c.is_extended_id

        rc = ECanVci.Transmit(self.dev, 0, self.channel, frameinfo, buflen)
        logger.debug(f"Transmit: {rc} {c}")
        if rc != buflen:
            logger.warn("Transmit %d" % rc)
        return rc

    def _recv_internal(self, timeout):
        if timeout is None:
            timeout = -1
        else:
            timeout = int(timeout*1000)
        num = ECanVci.GetReceiveNum(self.dev, 0, self.channel)
        if num == 0 :
            return None, False
        for i in range(num):
            rx = self._recv_one()
            if rx is None:
                return None, False
            if self._matches_filters(rx):
                logger.debug(f"{self.channel_info} {num} recv {rx}")
                return rx, True
        return None, False
        
    def _recv_one(self):
        buflen = 1
        frameinfo = (ECanVci.CAN_OBJ * buflen)()
        len = ECanVci.Receive(self.dev, 0, self.channel,
                            frameinfo, buflen, 0)
        # print("_try_recv:", len)
        # struct__CAN_OBJ._fields_ = [
        #     ('ID', c_uint32),                 # 报文帧ID
        #     ('TimeStamp', c_uint32),          # 接收到信息帧时的时间标识，从CAN控制器初始化开始计时，单位微秒。
        #     ('TimeFlag', c_uint8),            # 是否使用时间标识，为1时TimeStamp有效，TimeFlag和TimeStamp只在此帧为接收帧时有意义。
        #     ('SendType', c_uint8),            # 发送帧类型。=0时为正常发送，=1时为单次发送（不自动重发），=2时为自发自收（用于测试CAN卡是否损坏），=3时为单次自发自收（只发送一次，用于自测试），只在此帧为发送帧时有意义。
        #     ('RemoteFlag', c_uint8),          # 是否是远程帧。=0时为数据帧，=1时为远程帧。
        #     ('ExternFlag', c_uint8),          # 是否是扩展帧。=0时为标准帧（11位帧ID），=1时为扩展帧（29位帧ID）。
        #     ('DataLen', c_uint8),             # 数据长度DLC(<=8)，即Data的长度
        #     ('Data', c_uint8 * int(8)),       # CAN报文的数据。空间受DataLen的约束。
        #     ('Reserved', c_uint8 * int(3)),
        # ]

        if len > 0:
            frame = frameinfo[0]
            # print(frame.TimeStamp)

            rx = Message(
                # timestamp=float(frame.TimeStamp),
                timestamp=time.time(),
                is_remote_frame=frame.RemoteFlag,
                is_extended_id=frame.ExternFlag,
                is_error_frame=False,
                is_fd=False,
                arbitration_id=frame.ID,
                dlc=frame.DataLen,
                data=frame.Data)

            return rx
        return None

    # def _try_recv(self, timeout):
    #     timeout = int(timeout*1000)
    #     print("_try_recv timeout", timeout)
    #     buflen = 1
    #     frameinfo = (ECanVci.CAN_OBJ * buflen)()
    #     len = ECanVci.Receive(self.dev, 0, self.channel, frameinfo, buflen, timeout)
    #     print("_try_recv:", len)
    #     return (frameinfo[0].ID, frameinfo[0].Data, frameinfo[0].TimeStamp)

    def shutdown(self):
        self.close()

    def close(self):
        # if self.dev is not None:
        #     ECanVci.CloseDevice(self.dev, self.dev_index)
        #     GcUsbCanBus.opening_status[self.dev_index] = False
        pass

    def __del__(self):
        self.close()
