# -*- coding: utf-8 -*-
"""
PostProcessBuffer Handling with HighspeedPort using giutility.
"""
from ctypes import*
import ctypes

from ginsapy.giutility.loader import load_giutility

#//////////////////////////////////////////////////////////////////////////////////////////
#/*------------- PostProcess buffer server handling -------------------------------------*/
#/*																						*/
#/*	Description:																		*/
#/*																						*/
#/*		Following functions allow creation of PostProcess buffers / data stream			*/
#/*		Depending on environmental settings, different data backends are supported   	*/
#/*																						*/
#//////////////////////////////////////////////////////////////////////////////////////////
#/**
# * @brief Create new PostProcess buffer / SystemStream
# *
# * @param sourceID			source UUID (SID) of this buffer
# * @param sourceName		name of this buffer
# * @param measurementID		measurement UUID (MID) of the actual mesurement
# * @param measurementName	name of the actual measurement
# * @param sampleRateHz		the desired sample rate for this measurement
# * @param bufferSizeByte	the maximum size of this buffer in bytes
# * @param segmentSizeByte	the size of a buffer segment (if supported)
# * @param retentionTimeSec  data retention time of this buffer (if supported)
# *
# * @param bufferHandle		the result handle
# * @param errorMsg			buffer for error message text if not successful
# * @param errorMsgLen		length of the error message buffer
# *
# * @return General return codes
# */

#const char* -->c_char_p
#double      -->c_double
#double*      -->POINTER(c_double)
#uint64_t    -->? probably c_int
#int32_t      -->c_int
#int32_t*    -->POINTER(c_int)
#char*       -->c_char_p
#uint32_t    -->c_int



        
class PostProcessBufferClient:
    '''
    Following functions provide communication possibilities for buffered data.
    Connection and buffer has to be initialized first and config data functions
    can beused to read some channel information's first.
    For initialisation, Communication type "HSP_BUFFER" or "HSP_ECONLOGGER" has
    to be used:
    HSP_BUFFER ..... read data from the int32_ternal circle buffer
    HSP_ECONLOGGER . read data from a e.con dataLogger
    The cyclic data transmission between controller and PC is done by the DLL.
    which are already decoded.
    Following functions provide read access to this DLL Buffers.
    '''
    def __init__(self):
        self.GINSDll = load_giutility()
        print(f"Loaded GiUtility from: {self.GINSDll._name}")

        self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferInfo.argtypes = [c_int,c_char_p,c_size_t,c_char_p,c_size_t]   
        self.GINSDll._CD_eGateHighSpeedPort_Init_PostProcessBuffer.argtypes = [c_char_p,POINTER(c_int),POINTER(c_int)]
        self.bufferID=ctypes.create_string_buffer(50)
        self.bufferName=ctypes.create_string_buffer(50)
        self.HCLIENT=c_int(-1)
        self.HCONNECTION=c_int(-1)

    def get_buffer_count(self):
        """Number of available post process buffers"""
        self.count=self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferCount()
        return(self.count)

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
    
    def init_buffer_conn(self,sbufferID):
        '''
        Initialize connection to PostProcess buffer
        '''
        client_instance = ctypes.c_int()
        connection_instance = ctypes.c_int()
        self.sbufferID=sbufferID.encode('UTF-8')
        ret=self.GINSDll._CD_eGateHighSpeedPort_Init_PostProcessBuffer(self.sbufferID,byref(self.HCLIENT),byref(self.HCONNECTION))
        if(ret!=0):
            print("Init Connection Failed - ret:",ret)
        self.HCLIENT=c_int(client_instance.value)
        self.HCONNECTION=c_int(connection_instance.value)            
