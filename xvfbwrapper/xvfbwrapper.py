#!/usr/bin/env python
#
#   wrapper for running display inside X virtual framebuffer (Xvfb)
#
#   - inspired by PyVirtualDisplay: http://pypi.python.org/pypi/PyVirtualDisplay
#   - Corey Goldberg, 2012


import os
import fnmatch
import random
import subprocess
import time



class Xvfb(object):
    
    def __init__(self, width=1024, height=768, colordepth=24):
        self.width = width
        self.height = height
        self.colordepth = colordepth
        
        self.xvfb_proc = None
        self.old_display_num = \
            os.environ['DISPLAY'].split(':')[1] if 'DISPLAY' in os.environ else 0


    def start(self):
        self.vdisplay_num = self.search_for_free_display()
        self.xvfb_cmd = 'Xvfb :{0} -screen 0 {1}x{2}x{3} 2>&1 >{4}'.format(
            self.vdisplay_num, 
            self.width,
            self.height,
            self.colordepth,
            os.devnull
        )
        self.xvfb_proc = subprocess.Popen(self.xvfb_cmd,
            stdout=open(os.devnull),
            stderr=open(os.devnull),
            shell=True
        )
        time.sleep(0.1)  # give Xvfb time to start
        self._redirect_display(self.vdisplay_num)
        
    
    def stop(self):
        self._redirect_display(self.old_display_num)
        if self.xvfb_proc is not None:
            self.xvfb_proc.kill()
            self.xvfb_proc.wait()
            self.xvfb_proc = None

    
    def search_for_free_display(self):
        ls = map(lambda x:int(x.split('X')[1].split('-')[0]), self._lock_files())
        min_display_num = 1000
        if len(ls):
            display_num = max(min_display_num, max(ls) + 1)
        else:
            display_num = min_display_num
        random.seed()
        display_num += random.randint(0, 100)        
        return display_num
    
    
    def _lock_files(self):
        tmpdir = '/tmp'
        pattern = '.X*-lock'
        names = fnmatch.filter(os.listdir(tmpdir), pattern)
        ls = [os.path.join(tmpdir, child) for child in names]
        ls = [p for p in ls if os.path.isfile(p)]
        return ls
        

    def _redirect_display(self, display_num):
        os.environ['DISPLAY'] = ':%s' % display_num
