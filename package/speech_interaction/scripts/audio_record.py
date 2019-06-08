#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys 
import time
import threading
import rospy
import wave
from vad import Vad
from std_msgs.msg import String
from std_msgs.msg import Int8
from RecordParser import StreamParser

class audio_record():
    def __init__(self):
        self.count = 0
        self.channels=1
        self.sampwidth=2
        self.rate=16000
        self.project_name = '/home/keaixin/catkin_ws/src/homework/sounds/audio_record'
        self.pub_index = rospy.Publisher('/audio_index', Int8, queue_size=1)
        rospy.Subscriber('record_wakeup', String, self.wakeup)

    def wakeup(self,msg):
        stream_test = StreamParser()
        file_name = self.project_name + '_' + str(self.count) + '.wav'
        if msg.data == 'ok':
            stream_test.open_mic()
            cache_frames=stream_test.run()
            
            data = "".join(cache_frames)
            write_file = wave.open(file_name, 'wb')
            write_file.setnchannels(self.channels)
            write_file.setsampwidth(self.sampwidth)
            write_file.setframerate(self.rate)
            write_file.writeframes(data)
            write_file.close()
            
            self.pub_index.publish(self.count)
            self.count += 1

if __name__ == "__main__":
    rospy.init_node('audio_record')
    audio = audio_record()
    rospy.spin()