# -*- coding: utf-8 -*-
"""
PostProcessBuffer Handling with HighspeedPort using giutility.
"""
from ctypes import *
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


class PostProcessBufferManager:
    '''
    Following functions allow creation of PostProcess buffers / data stream
    Depending on environmental settings, different data backends are supported
    '''
    def __init__(self):
        self.GINSDll = load_giutility()
        print(f"Loaded GiUtility from: {self.GINSDll._name}")

        #New v3.0
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Create.argtypes = [c_char_p,c_char_p,c_double,c_ulonglong,c_ulonglong,c_double,c_char_p,POINTER(c_int),c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AddVariableDefinition.argtypes = [c_int,c_char_p,c_char_p,c_char_p,c_int,c_int,c_int,c_int,c_double,c_double,c_char_p,c_int]        
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Initialize.argtypes =[c_int,c_int,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_WriteDoubleToFrameBuffer.argtypes =[c_int,c_int,c_int,c_double,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_WriteTimestampToFrameBuffer.argtypes =[c_int,c_int,c_ulonglong,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AppendFrameBuffer.argtypes =[c_int,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AppendDataBuffer.argtypes =[c_int,c_char_p,c_ulonglong,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Close.argtypes =[c_int,c_char_p,c_int]
        self.GINSDll._CD_eGateHighSpeedPort_SleepMS.argtypes =[c_int]
        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_CreateUDBFFileBuffer.argtypes = [
            c_char_p,     # fullFilePath
            c_char_p,     # sourceID
            c_char_p,     # sourceName
            c_double,     # sampleRateHz
            c_uint64,     # maxLengthSeconds
            c_uint16,     # options
            POINTER(c_int32),  # bufferHandle
            c_char_p,     # errorMsg
            c_uint32      # errorMsgLen
        ]

        self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_CreateUDBFFileBuffer.restype = c_int32


        self.buffersize=50000000
        self.segmentsize=50000000
        self.bufferHandle=c_int(-1)
        self.errorlen=0
        self.frameBufferLength=10
        self.errorMsg=ctypes.create_string_buffer(30)


    def create_udbf_buffer(self, file_path: str, source_id: str, source_name: str,
                           sample_rate: float, max_length: int, options: int) -> int:

        file_path_c = file_path.encode("utf-8")
        source_id_c = source_id.encode("utf-8")
        source_name_c = source_name.encode("utf-8")

        sample_rate_c = c_double(sample_rate)
        max_length_c = c_uint64(max_length)
        options_c = c_uint16(options)

        ret = self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_CreateUDBFFileBuffer(
            file_path_c,
            source_id_c,
            source_name_c,
            sample_rate_c,
            max_length_c,
            options_c,
            byref(self.bufferHandle),
            self.errorMsg,
            self.errorlen
        )
        return ret

    
    def create_buffer(self,ID,BufferName,StreamSampleRate):
        """create post process buffer"""
        self.ID= ID.encode('UTF-8')
        self.BufferName=BufferName.encode('UTF-8')
        self.StreamSampleRate=StreamSampleRate

        dataTypeIdent='raw'
        self.dataTypeIdent=dataTypeIdent.encode('UTF-8')
        #self._CD_eGateHighSpeedPort_PostProcessBufferServer_Create.argtypes = [c_char_p,c_char_p,c_double,c_int,c_int,c_double,c_char_p,POINTER(c_int),c_char_p,c_int]
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Create(self.ID, self.BufferName, self.StreamSampleRate, self.buffersize, self.segmentsize,0, self.dataTypeIdent, byref(self.bufferHandle),self.errorMsg, self.errorlen)
        if ret!=0:
            print("Error at create buffer!")

    def add_channel(self,variableID,variableName,Unit):
        """Add a variable definition to the PostProcess buffer / SystemStream"""
        self.variableID=variableID.encode('UTF-8')
        self.variableName=variableName.encode('UTF-8')
        self.Unit=Unit.encode('UTF-8')
        self.DataTypeCode=8
        self.VariableKindCode=6
        self.Precision=4
        self.FieldLength=8
        self.RangeMin=-100
        self.RangeMax=100
        self.errorMsgLen=self.errorlen
        #self._CD_eGateHighSpeedPort_PostProcessBufferServer_Create.argtypes = [c_char_p,c_char_p,c_double,c_int,c_int,c_double,c_char_p,POINTER(c_int),c_char_p,c_int]
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AddVariableDefinition(self.bufferHandle, self.variableID, self.variableName, self.Unit,self.DataTypeCode,self.VariableKindCode,self.Precision,self.FieldLength,self.RangeMin,self.RangeMax,self.errorMsg,self.errorMsgLen)
        if ret!=0:
            print("Error adding channel")
            
    def init_buffer(self):
        """Initialize Post Process Buffer"""
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Initialize(self.bufferHandle, self.frameBufferLength, self.errorMsg, self.errorMsgLen)
        if ret!=0:
            print("Error buffer initialized")
            self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Close(self.bufferHandle,self.errorMsg, self.errorMsgLen)
        else :
            print("success buffer ini",self.bufferHandle) 
    def write_timestamps(self,frameIndex,timestamp_ns):
        """Write timestamp to frame buffer"""
        #self.frameIndex=frameIndex
        #self.valueInt=timestamp_ns
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_WriteTimestampToFrameBuffer(self.bufferHandle,frameIndex,timestamp_ns,None, self.errorMsgLen)
        if ret!=0:
            print("error writing timestamps")
            
    def write_to_framebuffer(self,frameIndex,variableIndex,valueDouble):
        '''
        Write data to internal frame buffer
        '''
        #self.frameIndex=frameIndex
        #self.variableIndex=variableIndex
        #self.valueDouble=valueDouble
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_WriteDoubleToFrameBuffer(self.bufferHandle,frameIndex,variableIndex,valueDouble,self.errorMsg, self.errorMsgLen)
        if ret!=0:
            print("error filling frame")

    def append_to_framebuffer(self):
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AppendFrameBuffer(self.bufferHandle,None,0)
        if ret!=0:
            print("error append to framebuffer")
            
    def append_data_to_framebuffer(self,data,dataLength):
        '''
        Append the internal temporary frame buffer to the post process buffer
        '''
        self.data=data
        self.dataLength=dataLength
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_AppendDataBuffer(self.bufferHandle,self.data,self.dataLength,self.errorMsg,self.errorMsgLen)
        if ret!=0:
            print("error append_data")

    def close_buffer(self, bufferHandle = None):
        '''
        Close post process buffer server
        '''
        if bufferHandle is None:
            bufferHandle = self.bufferHandle
        else:
            self.bufferHandle = bufferHandle
        ret=self.GINSDll._CD_eGateHighSpeedPort_PostProcessBufferServer_Close(self.bufferHandle,self.errorMsg, self.errorMsgLen)
        if ret!=0:
            print("error closing connection")
    def buffer_sleep(self,sleep_time):
        '''Can be used to sleep'''
        #self.sleep_time=sleep_time
        ret=self.GINSDll._CD_eGateHighSpeedPort_SleepMS(sleep_time)
        if ret!=0:
            print("error by sleeping")
        

    def get_buffer_info(self,bufferIndex):
        '''Get info about PostProcess buffer'''
        ret=self.GINSDll._CD_eGateHighSpeedPort_GetPostProcessBufferInfo(bufferIndex,self.bufferID,len(self.bufferID),self.bufferName,len(self.bufferName))
        if ret!=0:
            print("error get_buffer_info")
        else:
            print("buffer index:",bufferIndex,"buffer name:",self.bufferName.value.decode('UTF-8'),"buffer ID:",self.bufferID.value.decode('UTF-8'))
        return(self.bufferName.value.decode('UTF-8'),self.bufferID.value.decode('UTF-8'))
    
    def init_buffer_conn(self,sbufferID):
        '''Initialize connection to PostProcess buffer'''
        client_instance = ctypes.c_int()
        connection_instance = ctypes.c_int()
        self.sbufferID=sbufferID.encode('UTF-8')
        ret=self.GINSDll._CD_eGateHighSpeedPort_Init_PostProcessBuffer(self.sbufferID,byref(self.HCLIENT),byref(self.HCONNECTION))
        if(ret!=0):
            print("Init Connection Failed - ret:",ret)
        self.HCLIENT=c_int(client_instance.value)
        self.HCONNECTION=c_int(connection_instance.value)