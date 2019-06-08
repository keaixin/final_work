#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys 
import pyaudio
from vad import Vad 
import threading
import rospy

class StreamParser(Vad):
    def __init__(self):
        self.record = pyaudio.PyAudio()
        self.chunk =1024
        self.r_stream = None
        self.active = False
        Vad.__init__(self)      
   
    """
    开启mic 
    """ 
    def record_stream_start(self, format=pyaudio.paInt16, channels=1, rate=16000, buffer=None):
        if buffer is None:
            buffer = self.chunk
        else:
            self.chunk = buffer
        if self.r_stream:
            self.record_stream_end()
        self.r_stream = self.record.open(format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=buffer)
        print ("开始录音")  

    """
    关闭mic
    """
    def record_stream_end(self):
        if self.r_stream is not None:
            self.r_stream.stop_stream()
            self.r_stream.close()
            print ("录音关闭")
        self.r_stream = None

    def open_mic(self):
        print ("start recording")
        t = threading.Thread(target=self.mic_record)
        t.setDaemon(True)
        t.start()

    def mic_record(self):
        self.record_stream_start()
        self.active = True
        print ("The microphone has opened")
        while self.active: 
            data = self.record_read()
            self.add(data)
        self.record_stream_end()
        print ("exit mic")
         

    def close_mic(self):
        print ("stop recording")
        if self.record:
            print (self.active)
            self.active = False

    """ 
    读取指定块数数据
    """
    def record_read(self, num=1):
        return self.r_stream.read(self.chunk*num)