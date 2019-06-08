#!/usr/bin/env python
#-*- coding: utf-8 -*-

from time import sleep
import numpy as np
import threading 


def ZCR(curFrame):
    #过零率
    tmp1 = curFrame[:-1]
    tmp2 = curFrame[1:]
    sings = (tmp1*tmp2<=0)
    diffs = (tmp1-tmp2)>0.02
    zcr = np.sum(sings*diffs)
    return zcr

def STE(curFrame):
    #短时能量
    amp = np.sum(np.abs(curFrame))
    return amp

class Vad(object):
    def __init__(self): 
        #初始短时能量高门限
        self.amp1 = 140
        #初始短时能量低门限
        self.amp2 = 120
        #初始短时过零率高门限
        self.zcr1 = 10
        #初始短时过零率低门限
        self.zcr2 = 5 
        #允许最大静音长度
        self.maxsilence = 150
        #语音的最短长度
        self.minlen = 30
        #偏移值
        self.offsets = 40
        self.offsete = 40
        #能量最大值
        self.max_en = 20000
        #初始状态为静音
        self.status = 0
        self.count = 0
        self.silence = 0
        self.frame_len = 256
        self.frame_inc = 128
        self.cur_status = 0
        self.frames = []
        #数据开始偏移
        self.frames_start = []
        self.frames_start_num = 0
        #数据结束偏移
        self.frames_end = []
        self.frames_end_num = 0
        #缓存数据
        self.cache_frames = []
        self.cache = ""
        #最大缓存长度
        self.cache_frames_num = 0
        self.end_flag = False
        self.wait_flag = False
        self.on = True
        self.callback = None
        self.callback_res = []
        self.callback_kwargs = {}

    def clean(self):
        self.frames = []
        #数据开始偏移
        self.frames_start = []
        self.frames_start_num = 0
        #数据结束偏移
        self.frames_end = []
        self.frames_end_num = 0
        #缓存数据
        self.cache_frames = []
        #最大缓存长度
        self.cache_frames_num = 0
        self.end_flag = False
        self.wait_flag = False

    def go(self):
        self.wait_flag = False

    def wait(self):
        self.wait_flag = True
    def stop(self):
        self.on = False

    def add(self, frame, wait=True):
        if wait:
            frame = self.cache + frame                  
        while len(frame) > self.frame_len: 
           frame_block = frame[:self.frame_len] 
           self.cache_frames.append(frame_block) 
           frame = frame[self.frame_len:]
        if wait:
            self.cache = frame
        else:
            self.cache = ""
            self.cache_frames.append(-1)
       
           
    def run(self):
        print "开始执行音频端点检测"
        while 1:
            #开始端点
            #获得音频文件数字信号
            if self.wait_flag:
                sleep(1)
                continue
            if len(self.cache_frames) <2:
                sleep(0.05)
                continue
             
            if self.cache_frames[1] == -1:
                break
            record_stream = "".join(self.cache_frames[:2])
            wave_data = np.fromstring(record_stream, dtype=np.int16)
            wave_data = wave_data*1.0/self.max_en  
            data = wave_data[np.arange(0, self.frame_len)]
            speech_data = self.cache_frames.pop(0)
            #获得音频过零率
            zcr = ZCR(data)
            #获得音频的短时能量, 平方放大
            amp = STE(data) ** 2
            #返回当前音频数据状态
            res = self.speech_status(amp, zcr)
            print res,
            self.frames_start.append(speech_data)
            self.frames_start_num += 1
            if self.frames_start_num == self.offsets:
                #开始音频开始的缓存部分
                self.frames_start.pop(0)
                self.frames_start_num -= 1
            if res == 2 :
                if self.cur_status in [0, 1]:
                    #添加开始偏移数据到数据缓存
                    self.frames.append(b"".join(self.frames_start))
                #添加当前的语音数据
                self.frames.append(speech_data)
            if res == 3:         
                self.frames.append(speech_data)
                #开启音频结束标志
                self.end_flag = True
                print "record end"
                break
            self.cur_status = res
        return self.frames
               
    def speech_status(self, amp, zcr):
        status = 0
        # 0= 静音， 1= 可能开始
        if self.cur_status in [0, 1]: 
            # 确定进入语音段
            if amp > self.amp1:       
                status = 2
                self.silence = 0
                self.count += 1
            #可能处于语音段 
            elif amp > self.amp2 or zcr > self.zcr2: 
                status = 1
                self.count += 1
            #静音状态
            else:  
                status = 0
                self.count = 0
                self.count =0
        # 2 = 语音段
        elif self.cur_status == 2:              
            # 保持在语音段
            if amp > self.amp2 or zcr > self.zcr2:
                self.count += 1
                status = 2
            #语音将结束
            else:
                #静音还不够长，尚未结束
                self.silence += 1
                if self.silence < self.maxsilence:
                    self.count += 1
                    status = 2
                #语音长度太短认为是噪声
                elif self.count < self.minlen:
                    status = 0
                    self.silence = 0
                    self.count = 0
                #语音结束
                else:
                    status = 3
                    self.silence = 0
                    self.count = 0
        return status
