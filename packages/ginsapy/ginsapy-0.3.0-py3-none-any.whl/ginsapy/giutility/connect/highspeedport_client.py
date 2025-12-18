#-*- coding: utf-8 -*-

"""
Connects to a Gantner Bench/Controller/Q.core via HighSpeedPort and sets up communication.
"""

from ctypes import*
import ctypes
import numpy as np

from ginsapy.giutility.loader import load_giutility

class HighSpeedPortClient:
    def __init__(self):
        self.GINSDll = load_giutility()
        print(f"Loaded GiUtility from: {self.GINSDll._name}")

        #function prototypes
        self.GINSDll._CD_eGateHighSpeedPort_Init.argtypes = [c_char_p,c_int,c_int,c_int,POINTER(c_int),POINTER(c_int)]
        self.GINSDll._CD_eGateHighSpeedPort_SetBackTime.argtypes = [c_int, c_double]
        self.GINSDll._CD_eGateHighSpeedPort_InitBuffer.argtypes=[c_int,c_int,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_DecodeFile_Select.argtypes = [POINTER(c_int), POINTER(c_int), c_char_p]
        self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo.argtypes = [c_int, c_int, c_int, POINTER(c_double), c_char_p]
        self.GINSDll._CD_eGateHighSpeedPort_GetChannelInfo_String.argtypes = [c_int, c_int, c_int,c_int,c_char_p]
        self.GINSDll._CD_eGateHighSpeedPort_GetChannelInfo_Int.argtypes = [c_int, c_int, c_int,c_int,POINTER(c_int)]
        self.GINSDll._CD_eGateHighSpeedPort_ReadBufferToDoubleArray.argtypes = [c_int, POINTER(c_double), c_int, c_int,POINTER(c_int), POINTER(c_int), POINTER(c_int)]
        self.GINSDll._CD_eGateHighSpeedPort_ReadBufferToDoubleArray_StraightTimestamp.argtypes = [c_int, POINTER(c_double), c_int, c_int,POINTER(c_int), POINTER(c_int), POINTER(c_int)]
        self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_Single_Immediate.argtypes = [c_int, c_int, c_double]
        self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_Single.argtypes = [c_int, c_int, c_double]
        self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_ReleaseOutputData.argtypes = [c_int]
        self.GINSDll._CD_eGateHighSpeedPort_ReadOnline_Single.argtypes = [c_int, c_int, POINTER(c_double)]
        self.GINSDll._CD_eGateHighSpeedPort_Close.argtypes = [c_int, c_int]
        self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferInfo.argtypes = [c_int, c_char_p, c_size_t, c_char_p,
                                                                                 c_size_t]

        self.GINSDll._CD_eGateHighSpeedPort_Init_WebSocketStream.argtypes = [
            c_char_p,  # const char *url
            c_int32,  # int32_t port
            c_char_p,  # const char *route
            c_char_p,  # const char *username
            c_char_p,  # const char *password
            c_char_p,  # const char *streamId
            c_int64,  # int64_t startEpochTimeMs
            c_int64,  # int64_t endEpochTimeMs
            c_double,  # double timeoutSec
            c_int32,  # int32_t bufferType
            POINTER(c_int32),  # int32_t *clientInstance
            POINTER(c_int32)  # int32_t *connectionInstance
        ]
        self.GINSDll._CD_eGateHighSpeedPort_Init_WebSocketStreamExt.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_int, c_double, c_int, c_char_p, POINTER(c_int), POINTER(c_int)]


        #self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferInfo.argtypes = [c_int,c_char_p,c_size_t,c_char_p,c_size_t]
        self.GINSDll._CD_eGateHighSpeedPort_Init_PostProcessBuffer.argtypes = [c_char_p,POINTER(c_int),POINTER(c_int)]

        self.GINSDll._CD_eGateHighSpeedPort_LogToUDBF_File.argtypes = [
            c_int32,        # connectionInstance
            c_uint64,       # framecount
            c_char_p,       # variableIDs
            c_char_p        # fullFileName
        ]
        self.GINSDll._CD_eGateHighSpeedPort_LogToUDBF_File.restype = c_int32


        #self.bufferID=ctypes.create_string_buffer(50)
        #self.bufferName=ctypes.create_string_buffer(50)

        """"  parameters for Init connection """
        self.controllerIP=0#controllerIP.encode('UTF-8')
        self.timeout=5
        self.HSP_BUFFER=2#  1 for online; 2 for buffered values
        self.HSP_ONLINE=1#  1 for online; 2 for buffered values
        self.sampleRate=100
        # parameters for file decoding
        self.FilePath=0# = FilePath.encode('UTF-8')
        self.FileDecodeComplete=False
        #general used parameters
        self.HCLIENT=c_int(-1) #clientInstance
        self.HCONNECTION=c_int(-1) # connectionInstance
        #parameters for Init buffer
        self.bufferindex=0
        self.autoRun=0
        #parameters to empty the circular buffer
        self.backtime=0
        #parameters to read information from devices
        self.location=10
        self.Adress=11
        self.SampleRate=16
        self.SerialNumber=15
        self.ChannelCount=18
        self.Channel_InfoName=0
        self.Channel_Unit=1
        self.info=c_double(0)
        self.ret=0
        self.char=ctypes.create_string_buffer(30)
        self.CHINFO_INDX=7#total index
        self.DADI_INOUT=2#input/output
        self.ChannelInfo=c_int(-1)
        self.channelInfoStr=ctypes.create_string_buffer(30)
        self.bufferID=ctypes.create_string_buffer(50)
        self.bufferName=ctypes.create_string_buffer(50)
        #parameters to read buffer


    def convert_to_buffer_types(self, string):
        self.mapping = {
            "HSP_BUFFER": 2,
            "HSP_ARCHIVES": 4,
            "HSP_FILES": 5,
            "2": 2,
            "4": 4,
            "5": 5
        }
        return self.mapping.get(string, -1)
    
    def log_to_udbf_file(self, framecount, variable_ids, full_file_name):
        ret = self.GINSDll._CD_eGateHighSpeedPort_LogToUDBF_File(self.HCONNECTION, framecount, variable_ids, full_file_name)
        if ret != 0:
            print("log_to_udbf failed - ret:",ret)
        else:
            print("log to udbf started!")
        
    def init_connection(self,controllerIP):
        self.controllerIP=controllerIP.encode('UTF-8')
        """Initialisation of the connection to a controller - buffer connection \
		self.GINSDll._CD_eGateHighSpeedPort_Init(self.controllerIP,self.timeout, \
        self.HSP_BUFFER,self.sampleRate,byref(self.HCLIENT),byref(self.HCONNECTION))"""
        client_instance = ctypes.c_int()
        connection_instance = ctypes.c_int()
        ret=self.GINSDll._CD_eGateHighSpeedPort_Init(self.controllerIP,self.timeout,self.HSP_BUFFER,self.sampleRate,byref(self.HCLIENT),
        byref(self.HCONNECTION))
        if(ret!=0):
            print("Init Connection Failed - ret:",ret)
            self.ret=ret
            return False

        #Init buffer (this is mainly to select a certain buffer by index)
        ret=self.GINSDll._CD_eGateHighSpeedPort_InitBuffer(self.HCONNECTION.value,self.bufferindex,self.autoRun)
        if(ret!=0):
            print("Init Buffer Failed - ret:",ret)
            return False
        #empty the circular buffer to get only actual data
        ret=self.GINSDll._CD_eGateHighSpeedPort_SetBackTime(self.HCONNECTION.value,self.backtime)
        if(ret!=0):
            print("SetBackTime Failed - ret:",ret)
            return False
        self.HCLIENT=c_int(client_instance.value)
        self.HCONNECTION=c_int(connection_instance.value)
        print("Connection initialized. IP: ", controllerIP)
        return True


    def init_online_connection(self,controllerIP):
        self.controllerIP=controllerIP.encode('UTF-8')
        """Initialisation of the connection to a controller - online connection 
		self.GINSDll._CD_eGateHighSpeedPort_Init(self.controllerIP,self.timeout, 
        self.HSP_ONLINE,self.sampleRate,byref(self.HCLIENT),byref(self.HCONNECTION))"""
        client_instance = ctypes.c_int()
        connection_instance = ctypes.c_int()
        ret=self.GINSDll._CD_eGateHighSpeedPort_Init(self.controllerIP,self.timeout,self.HSP_ONLINE,self.sampleRate,byref(self.HCLIENT),byref(self.HCONNECTION))
        if(ret!=0):
            print("Init Connection Failed - ret:",ret)
            self.ret=ret
            return False

        #Init buffer (this is mainly to select a certain buffer by index)
        ret=self.GINSDll._CD_eGateHighSpeedPort_InitBuffer(self.HCONNECTION.value,self.bufferindex,self.autoRun)
        if(ret!=0):
            print("Init Buffer Failed - ret:",ret)
            return False
        #empty the circular buffer to get only actual data
        ret=self.GINSDll._CD_eGateHighSpeedPort_SetBackTime(self.HCONNECTION.value,self.backtime)
        if(ret!=0):
            print("SetBackTime Failed - ret:",ret)
            return False
        self.HCLIENT=c_int(client_instance.value)
        self.HCONNECTION=c_int(connection_instance.value)
        print("Connection initialized. IP: ", controllerIP)
        return True

    def init_websocket_connection(self, url, port, route, username, password, timeout_sec, add_config):
        '''
        Initialize online web-socket connection
        '''
        client_instance = c_int()
        connection_instance = c_int()

        ret = self.GINSDll._CD_eGateHighSpeedPort_InitWebSocket(
            c_char_p(url.encode('utf-8')),
            c_int(port),
            c_char_p(route.encode('utf-8')),
            c_char_p(username.encode('utf-8')),
            c_char_p(password.encode('utf-8')),
            c_double(timeout_sec),
            c_char_p(add_config.encode('utf-8')),
            ctypes.byref(client_instance),
            ctypes.byref(connection_instance)
        )
        if(ret!=0):
            print("Init Connection Failed - ret:",ret)
            self.ret=ret
            return False
        else:
            print("WebSocket connection initialized successfully")
            self.HCLIENT=c_int(client_instance.value)
            self.HCONNECTION=c_int(connection_instance.value)
            return client_instance.value, connection_instance.value

    def init_websocket_stream(
            self, url, port, route, username, password,
            stream_id, start_time, end_time,
            timeout_sec, buffer_type, add_config=None
    ):
        """
        Initialize web socket based data stream (Ext version)
        """
        client_instance = ctypes.c_int()
        connection_instance = ctypes.c_int()

        buffer_type = self.convert_to_buffer_types(buffer_type)

        ret = self.GINSDll._CD_eGateHighSpeedPort_Init_WebSocketStreamExt(
            ctypes.c_char_p(url.encode("utf-8")),
            ctypes.c_int(port),
            ctypes.c_char_p(route.encode("utf-8")),
            ctypes.c_char_p(username.encode("utf-8")),
            ctypes.c_char_p(password.encode("utf-8")),
            ctypes.c_char_p(stream_id.encode("utf-8")),
            ctypes.c_int(start_time),  # 32-bit only!
            ctypes.c_int(end_time),  # 32-bit only!
            ctypes.c_double(timeout_sec),
            ctypes.c_int(buffer_type),
            ctypes.c_char_p(add_config.encode("utf-8")) if add_config else None,
            ctypes.byref(client_instance),
            ctypes.byref(connection_instance),
        )

        if ret != 0:
            print("Init Stream Connection Failed - ret:", ret)
            self.ret = ret
            return False
        else:
            print("WebSocket Stream connection initialized successfully")
            self.HCLIENT = ctypes.c_int(client_instance.value)
            self.HCONNECTION = ctypes.c_int(connection_instance.value)
            return client_instance.value, connection_instance.value

    def init_file(self,FilePath):
        """Initialisation of the dat-file decoding \
		self.GINSDll._CD_eGateHighSpeedPort_DecodeFile_Select(byref(self.HCLIENT), \
        byref(self.HCONNECTION),self.FilePath)"""
        self.FilePath= FilePath.encode('UTF-8')
        ret=self.GINSDll._CD_eGateHighSpeedPort_DecodeFile_Select(byref(self.HCLIENT),byref(self.HCONNECTION),self.FilePath)
        if ret==0:
            print("File Load OK!", self.FilePath.decode('UTF-8'))
            return True
        else:
            print("Error Loading File ", self.FilePath.decode('UTF-8'))
            return False

    def read_serial_number(self):
        """Read the serial number of the connected device \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.SerialNumber,0,self.info,None)"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.SerialNumber,0,self.info,None)
        if(ret==0):
            print("controller serial number", self.info.value)
            return self.info.value
        else:
            print("error reading serial number!")
            return 0

    def read_sample_rate(self):
        """Read a buffer sampling rate \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.SampleRate,0,self.info,None)"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.SampleRate,0,self.info,None)
        if(ret==0):
            print("controller sample rate", self.info.value)
            return self.info.value
        else:
            print("Error reading sample rate!")
            return 0

    def read_channel_count(self):
        """Count the number of channels connected to a controller \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.ChannelCount,0,self.info,None)"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.ChannelCount,0,self.info,None)
        if(ret==0):
            print("controller channel count", self.info.value)
            return self.info.value
        else:
            print("Error reading channel count!")
            return ""

    def read_controller_name(self):
        """Read a controller name  \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.location,0,None,self.char)"""
        #p=ctypes.create_string_buffer(30)#this function works for python 3.6, for lower version the name of functions to create mutable character buffer is different
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.location,0,None,self.char)
        if(ret==0):
            print("controller name", self.char.value.decode('UTF-8'))
            return self.char.value.decode('UTF-8')
        else:
            print("Error reading controller name!")
            return ""

    def read_controller_address(self):
        """Read the adress of a connected controller \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.Adress,0,None,self.char)"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.Adress,0,None,self.char)
        if(ret==0):
            print("controller adress", self.char.value.decode('UTF-8'))
            return self.char.value.decode('UTF-8')
        else:
            print("Error reading controller address")
            return ""

    def read_channel_names(self):
        """Read the channel name and corresponding index \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.ChannelCount,0,self.info,None)"""
        i=0
        self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.ChannelCount,0,self.info,None)
        ChannelNb=self.info.value
        while i<ChannelNb:
            self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.Channel_InfoName,i,None,self.char)
            print("Controller index:",i," channel name:", self.char.value.decode('UTF-8'))
            i+=1
    def read_channels_unit(self):
        """Read the channel unit \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.ChannelCount,0,self.info,None)"""
        i=0
        self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.ChannelCount,0,self.info,None)
        ChannelNb=self.info.value
        while i<ChannelNb:
            self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.Channel_Unit,i,None,self.char)
            try:
                print("Controller index:",i," channel unit:", self.char.value.decode('UTF-8'))
            except UnicodeDecodeError:
                print("Controller index:",i," channel unit:", "NAN")
            i+=1

    def read_index_unit(self,IndexNb):
        """Read the channel name corresponding to an index \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.Channel_Unit,IndexNb,None,self.char)"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.Channel_Unit,IndexNb,None,self.char)
        if(ret==0):
            try:
                return(self.char.value.decode('UTF-8'))
            except UnicodeDecodeError:
                # we decode °C
                if self.char.value == b'\xb0C':
                    return (u'\u00b0C')
                # we decode
                if self.char.value == b'\xb5m/m':
                    return (u'\u00b5m/m')
                #we decode

                else:
                    return("Unit")
        else:
            print("Error reading channel unit, index",IndexNb)
            return ""

    def read_index_name(self,IndexNb):
        """Read the channel name corresponding to an index \
		self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value, \
        self.Channel_InfoName,IndexNb,None,self.char)"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.Channel_InfoName,IndexNb,None,self.char)
        if(ret==0):
            return(self.char.value.decode('UTF-8'))
        else:
            print("Error reading channel name, index",IndexNb)
            return ""

    def write_online_value(self,IndexNb,WriteValue):
        """Write a single double value to a specific channel on the connection, \
        selected with connectionIndex immeadiately. \
		self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_Single_Immediate(self.HCONNECTION.value,IndexNb,WriteValue)"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_Single_Immediate(self.HCONNECTION.value,IndexNb,WriteValue)
        if(ret==0):
            print("Value:",WriteValue,"Was added to index:",IndexNb)
            return True
        else:
            print("Could not write value:",WriteValue,"to index:",IndexNb)
            return False


    def write_single(self,IndexNb,WriteValue):
        """Writte a single double value to a specific channel selected \
        with connectionIndex. \
        They will be stored in the DLL output buffer \
        until "eGateHighSpeedPort_WriteOnline_ReleaseOutputData" is called for this connection. \
		self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_Single(self.HCONNECTION.value,IndexNb,WriteValue)"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_Single(self.HCONNECTION.value,IndexNb,WriteValue)
        if(ret==0):
            print("Value:",WriteValue,"Was added to index:",IndexNb)
            return ""
        else:
            print("Could not write value:",WriteValue,"to index:",IndexNb)
            return ""
    def relase_output(self):
       """Release all bufered output values. This ensures that all channels are written simultaniously.
	   self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_ReleaseOutputData(self.HCONNECTION.value)"""
       ret=self.GINSDll._CD_eGateHighSpeedPort_WriteOnline_ReleaseOutputData(self.HCONNECTION.value)
       if(ret==0):
           print("Value was released")
           return ""
       else:
           print("Error releasing data")
           return ""

    #def read_buffer_frame(self):
    #    self.GINSDll._CD_eGateHighSpeedPort_GetBufferFrames.argtypes=[c_int,c_int]
    #    self.GINSDll._CD_eGateHighSpeedPort_GetBufferFrames(self.HCONNECTION.value,self.HCLIENT.value)
    #    print("buffer frame number:",)

    def read_online_single(self, IndexNb):
        '''read value from a specific channel on the connection
        self.GINSDll._CD_eGateHighSpeedPort_ReadOnline_Single(self.HCONNECTION.value, IndexNb, ctypes.byref(value))'''
        value = ctypes.c_double()
        ret = self.GINSDll._CD_eGateHighSpeedPort_ReadOnline_Single(self.HCONNECTION.value, IndexNb, ctypes.byref(value))
        if ret == 0:
            print("Value:", value.value, "was read from index:", IndexNb)
            return value.value
        else:
            print("Error reading channel value, index", IndexNb)
            return None

    def read_online_multiple(self,IndexNb):
        '''read value from multiple channels on the connection
        self.GINSDll._CD_eGateHighSpeedPort_ReadOnline_FrameToDoubleArray(self.HCONNECTION.value, value_array, array_length, start_index, channel_count)'''

        #find out how many channels have to be read/returned
        start_index = min(IndexNb)
        end_index = max(IndexNb)
        array_length = end_index - start_index + 1
        value_array = (ctypes.c_double * array_length)()

        ret = self.GINSDll._CD_eGateHighSpeedPort_ReadOnline_FrameToDoubleArray(
            self.HCONNECTION.value,
            value_array,
            array_length,
            start_index,
            #length of array_length and channel_count are the same
            array_length
        )
        #Only return the values of indices in IndexNb
        if ret == 0:
            return_values = [value_array[i-start_index] for i in range(start_index, start_index + array_length) if i in IndexNb]
            return return_values
        else:
            print("Error reading channel values, startIndex:", min(IndexNb))
            return None

    def read_online_all(self, array_length=0, start_index=0):
            '''Read all channel values into a double array
            Argument array_length: number of channels being read from start_index
            If start_index is not specified, the first array_length channels will be read
            self.GINSDll._CD_eGateHighSpeedPort_ReadOnline_FrameToDoubleArray(self.HCONNECTION.value, value_array, array_length, start_index, channel_count)'''
            if array_length == 0:
                array_length = self.ChannelCount
            value_array = (ctypes.c_double * array_length)()
            channel_count = -1  # Read all channels

            ret = self.GINSDll._CD_eGateHighSpeedPort_ReadOnline_FrameToDoubleArray(
                self.HCONNECTION.value,
                value_array,
                array_length,
                start_index,
                channel_count
            )

            if ret == 0:
                return [value_array[i] for i in range(array_length)]
            else:
                print("Error reading channel values, startIndex:", start_index)
                return None

    def yield_buffer(self,NbFrames=int(100000),fillArray=0):
        '''function used to receive the buffer content - the stream is considered
        a generator
        self.GINSDll._CD_eGateHighSpeedPort_ReadBufferToDoubleArray(self.HCONNECTION.value,
        valuesPtr,(NbFrames*ChannelNb),fillArray,ReceivedFrames,ReceivedChannels,ReceivedComplete)'''

        self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.ChannelCount,0,self.info,None)
        ChannelNb=int(self.info.value)
        valuesPtr=(c_double*(NbFrames*ChannelNb))()
        ReceivedFrames=c_int(0)#pointer
        ReceivedChannels=c_int(0)#pointer
        ReceivedComplete=c_int(0)#pointer
        ret=0
        while(ret==0):
            ret=self.GINSDll._CD_eGateHighSpeedPort_ReadBufferToDoubleArray(self.HCONNECTION.value,valuesPtr,(NbFrames*ChannelNb),fillArray,ReceivedFrames,ReceivedChannels,ReceivedComplete)
            chcnt=ReceivedChannels.value
            BUF=valuesPtr[0:chcnt*ReceivedFrames.value]
            buffer=np.reshape(BUF,(ReceivedFrames.value,chcnt))
            yield buffer

    def yield_buffer_st(self,NbFrames=int(100000),fillArray=0):
        '''function used to receive the buffer content (timestamp as int) - the stream is considered
        a generator
        self.GINSDll._CD_eGateHighSpeedPort_ReadBufferToDoubleArray_StraightTimestamp(self.HCONNECTION.value,
        valuesPtr,(NbFrames*ChannelNb),fillArray,ReceivedFrames,ReceivedChannels,ReceivedComplete)'''

        self.GINSDll._CD_eGateHighSpeedPort_GetDeviceInfo(self.HCONNECTION.value,self.ChannelCount,0,self.info,None)
        ChannelNb=int(self.info.value)
        valuesPtr=(c_double*(NbFrames*ChannelNb))()
        ReceivedFrames=c_int(0)#pointer
        ReceivedChannels=c_int(0)#pointer
        ReceivedComplete=c_int(0)#pointer
        ret=0
        while(ret==0):
            ret=self.GINSDll._CD_eGateHighSpeedPort_ReadBufferToDoubleArray_StraightTimestamp(self.HCONNECTION.value,valuesPtr,(NbFrames*ChannelNb),fillArray,ReceivedFrames,ReceivedChannels,ReceivedComplete)
            chcnt=ReceivedChannels.value
            BUF=valuesPtr[0:chcnt*ReceivedFrames.value]
            buffer=np.reshape(BUF,(ReceivedFrames.value,chcnt))
            yield buffer

    def close_connection(self):
        '''close the connection
        self.GINSDll._CD_eGateHighSpeedPort_Close(self.HCONNECTION.value,self.HCLIENT.value)'''
        self.GINSDll._CD_eGateHighSpeedPort_Close(self.HCONNECTION.value,self.HCLIENT.value)


    def init_buffer_conn(self,sbufferID):
        '''Initialize connection to PostProcess buffer
        self.GINSDll._CD_eGateHighSpeedPort_Init_PostProcessBuffer(self.sbufferID,
        byref(self.HCLIENT),byref(self.HCONNECTION))'''
        if isinstance(sbufferID, str):
            buf_id = sbufferID.encode("utf-8")
        elif isinstance(sbufferID, (bytes, bytearray)):
            buf_id = bytes(sbufferID)
        else:
            raise TypeError("sbufferID must be str or bytes")

        ret = self.GINSDll._CD_eGateHighSpeedPort_Init_PostProcessBuffer(
            c_char_p(buf_id),
            byref(self.HCONNECTION),
            byref(self.HCLIENT),
        )
        if ret != 0:
            print("Init PostProcess Buffer connection failed - ret:", ret)
            self.ret = ret
            return False

        print("PostProcess Buffer connection initialized.")
        return True

    def get_channel_info(self,IndexNb):
        """Read the channel total index"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetChannelInfo_Int(self.HCONNECTION.value,self.CHINFO_INDX,self.DADI_INOUT,IndexNb,byref(self.ChannelInfo))
        if(ret==0):
            print("Total index of selected channel", self.ChannelInfo.value)
            return self.ChannelInfo.value
        else:
            print("Error reading channel info!")
            return ""

    def get_channel_info_name(self,IndexNb):
        """Read the channel name corresponding to the upper index"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetChannelInfo_String(self.HCONNECTION.value,0,self.DADI_INOUT,IndexNb,self.channelInfoStr)
        if(ret==0):
            return self.channelInfoStr.value.decode('UTF-8')
        else:
            print("Error reading channel info!")
            return ""

    def get_buffer_info(self,bufferIndex):
        '''
        Get info about PostProcess buffer
        '''
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferInfo(bufferIndex,self.bufferID,len(self.bufferID),self.bufferName,len(self.bufferName))
        if ret!=0:
            print("error get_buffer_info")
        else:
            print("buffer index:",bufferIndex,"buffer name:",self.bufferName.value.decode('UTF-8'),"buffer ID:",self.bufferID.value.decode('UTF-8'))
        return(self.bufferName.value.decode('UTF-8'),self.bufferID.value.decode('UTF-8'))

    def get_buffer_count(self):
        """Number of available post process buffers"""
        self.count=self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferCount()
        return(self.count)

#This function is needeed for file saved with high number of frames
def read_again_buffer(buffer):
    '''help function called in read_gins_dat'''
    read_next_buffer=next(buffer)
    new_buffer_values= read_next_buffer[:,:]
    return (new_buffer_values)


def read_gins_dat(connection):
    '''function calls to read dat file and ensure that all frames are read.
    Indeed the number of frames is not known in the header of udbf file, a check
    of the timestampl is done in this loop'''
    #Call function to store buffer into the variable buffer
    buffer=connection.yield_buffer()
    #We read the dat file and save it into the variable disp
    readbuffer=next(buffer)
    Logged_file = readbuffer[:,:]
    #This function is needed for reading the full dat file with several buffer frames
    while True:
        #print('we enter while')
        new_disp=read_again_buffer(buffer)
        try:
            new_time=new_disp[0,0]
        except:
            break
        last_time=Logged_file[-1,0]
        if new_time>last_time:
            Logged_file=np.vstack((Logged_file,new_disp))
        else:
            break
    print ('dat file was read')
    return Logged_file

def create_list_channel(connection):
    '''Go through the buffer and return some list of channels names or unit'''
    Nb=0
    list_channels=[]
    list_unit=[]
    while Nb<int(connection.read_channel_count()):
        try:
            #list_channels.append(connection.read_index_name(Nb).encode('UTF-8'))
            list_channels.append(str(connection.read_index_name(Nb)))
        except AttributeError:
            list_channels.append(str(connection.read_index_name(Nb)))
        list_unit.append(connection.read_index_unit(Nb).lstrip())
        Nb+=1
    return (list_channels,list_unit)
