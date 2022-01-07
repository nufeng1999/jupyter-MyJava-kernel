###%file:c_kernel.py
#
#   MyJava Jupyter Kernel 
#   generated by MyPython
#
from math import exp
from queue import Queue
from threading import Thread
from ipykernel.kernelbase import Kernel
from pexpect import replwrap, EOF
from jinja2 import Environment, PackageLoader, select_autoescape,Template
from abc import ABCMeta, abstractmethod
from typing import List, Dict, Tuple, Sequence
from shutil import copyfile,move
from urllib.request import urlopen
import socket
import copy
import mmap
import contextlib
import atexit
import platform
import atexit
import base64
import urllib.request
import urllib.parse
import pexpect
import signal
import typing 
import typing as t
import re
import signal
import subprocess
import tempfile
import os
import stat
import sys
import traceback
import os.path as path
import codecs
import time
import importlib
import importlib.util
import inspect
from . import ipynbfile
from plugins.ISpecialID import IStag,IDtag,IBtag,ITag,ICodePreproc
from plugins._filter2_magics import Magics
try:
    zerorpc=__import__("zerorpc")
    # import zerorpc
except:
    pass
fcntl = None
msvcrt = None
bLinux = True
if platform.system() != 'Windows':
    fcntl = __import__("fcntl")
    bLinux = True
else:
    msvcrt = __import__('msvcrt')
    bLinux = False
from .MyKernel import MyKernel
class JavaKernel(MyKernel):
    implementation = 'jupyter-MyC-kernel'
    implementation_version = '1.0'
    language = 'Java'
    language_version = ''
    language_info = {'name': 'text/java',
                     'mimetype': 'text/java',
                     'file_extension': '.java'}
    runfiletype='class'
    banner = "MyJava kernel.\n" \
             "Uses JavaC, compiles in Java, and creates source code files and executables in temporary folder.\n"
    main_head = "#include <stdio.h>\n" \
            "#include <math.h>\n" \
            "int main(int argc, char* argv[], char** env){\n"
    main_foot = "\nreturn 0;\n}"
##//%include:src/comm_attribute.py
    def __init__(self, *args, **kwargs):
        super(JavaKernel, self).__init__(*args, **kwargs)
        self.runfiletype='class'
        self.kernelinfo="[MyJavaKernel{0}]".format(time.strftime("%H%M%S", time.localtime()))
        
#################
    def compile_with_javac(self, source_filename, binary_filepath=None, cflags=None, ldflags=None,env=None,coptions=None):
        # cflags = ['-std=c89', '-pedantic', '-fPIC', '-shared', '-rdynamic'] + cflags
        outpath=os.path.dirname(source_filename)
        sf = os.path.basename(source_filename)
        binary_filename = sf.split(".")[0]
        # if self.linkMaths:
        #     cflags = cflags + ['-lm']
        # if self.wError:
        #     cflags = cflags + ['-Werror']
        # if self.wAll:
        #     cflags = cflags + ['-Wall']
        # if self.readOnlyFileSystem:
        #     cflags = ['-DREAD_ONLY_FILE_SYSTEM'] + cflags
        # if self.bufferedOutput:
        #     cflags = ['-DBUFFERED_OUTPUT'] + cflags
        # target=os.path.dirname(binary_filepath)
        index=-1
        if coptions==None:
            coptions=[]
        for s in coptions:
            index=index+1
            if s=='-d':
                outpath=coptions[index+1]
                if not outpath.startswith('-'):
                    #剔除 -d参数和值
                    outpath=coptions.pop(index+1)
                    coptions.pop(index)
            else:
                if binary_filepath!=None:
                    outpath=binary_filepath
        args = ['javac']+coptions+ ['-d', outpath]+[ source_filename]
        self._logln(' '.join((' '+ str(s) for s in args)))
        binary_filename=os.path.join(outpath,binary_filename)
        return self.create_jupyter_subprocess(args,env=env,magics=magics),binary_filename+".class",args
##调用 javac 编译源代码
    def _exec_javac_(self,source_filename,magics):
        self._write_to_stdout('Generating binary file\n')
        magics['status']='compiling'
        p,outfile,ccmd = self.compile_with_javac(
            source_filename, 
            None,
            self.get_magicsSvalue(magics,'cflags'),
            self.get_magicsSvalue(magics,'ldflags'),
            self.get_magicsbykey(magics,'env'),
            self.get_magicsSvalue(magics,'coptions')
            )
        returncode=p.wait_end(magics)
        p.write_contents()
        magics['status']=''
        if returncode != 0:  # Compilation failed
            self._logln(''.join((str(s) for s in ccmd)),3)
            self._logln("Javac exited with code {}, the executable will not be executed".format(returncode),3)
            # delete source files before exit
            # os.remove(source_filename)
            # os.remove(binary_file.name)
        return p.returncode,outfile
##do_runcode
    def do_runcode(self,return_code,fil_ename,class_filename,outpath,magics,code, silent, store_history=True,
                    user_expressions=None, allow_stdin=True):
        return_code=return_code
        fil_ename=fil_ename
        bcancel_exec=False
        retinfo=self.mymagics.get_retinfo()
        retstr=''
        ##代码运行前
        mainclass=magics['package']+"."+class_filename
        self.mymagics.chkjoptions(magics,'/usr/share/java/groovy.jar',outpath)
        self.mymagics._write_to_stdout("The process :"+class_filename+"\n")
        ################# repl mode run code files
        #FIXME:
        if magics['st']['runmode']=='repl':
            self.mymagics._start_replprg('java',magics['st']['joptions']+[mainclass] + magics['st']['args'],magics)
            return_code=p.returncode
            bcancel_exec,retstr=self.mymagics.raise_plugin(code,magics,return_code,fil_ename,3,2)
            return bcancel_exec,retinfo,magics, code,fil_ename,retstr
        ############################################
    ############################################
        #################dynamically load and execute code
        #FIXME:
        # if len(magics['dlrun'])>0:
        #     p = self.create_jupyter_subprocess([self.master_path, class_filename] + magics['args'],env=self.addkey2dict(magics,'env'))
        # #################
        # else:
        cmdstr = ['java']+magics['st']['joptions']+[mainclass] + magics['st']['args']
        self.mymagics._log(' '.join((' '+ str(s) for s in cmdstr))+"\n") 
        p = self.mymagics.create_jupyter_subprocess(['java']+magics['st']['joptions']+[mainclass] + magics['st']['args'],env=self.mymagics.addkey2dict(magics,'env'),magics=magics)
        self.mymagics.subprocess=p
        self.mymagics.g_rtsps[str(p.pid)]=p
        return_code=p.returncode
        ##代码启动后
        bcancel_exec,retstr=self.mymagics.raise_plugin(code,magics,return_code,fil_ename,3,2)
        # if bcancel_exec:return bcancel_exec,retinfo,magics, code,fil_ename,retstr
        
        if len(self.mymagics.addkey2dict(magics,'showpid'))>0:
            self.mymagics._write_to_stdout("The process PID:"+str(p.pid)+"\n")
        return_code=p.wait_end(magics)
        ##代码运行结束
        # now remove the files we have just created
        # if(os.path.exists(source_file.name)):
            # os.remove(source_file.name)
        # if(os.path.exists(class_filename)):
            # os.remove(class_filename)
        # if p.returncode != 0:
            # self._write_to_stderr("[C kernel] Executable exited with code {}".format(p.returncode))
        return bcancel_exec,retinfo,magics, code,fil_ename,retstr
##do_compile_code
    def do_compile_code(self,return_code,fil_ename,magics,code, silent, store_history=True,
                    user_expressions=None, allow_stdin=True):
        return_code=0
        fil_ename=fil_ename
        sourcefilename=fil_ename
        bcancel_exec=False
        retinfo=self.mymagics.get_retinfo()
        retstr=''
        
        returncode,class_filename=self._exec_javac_(fil_ename,magics)
        fil_ename=class_filename
        outpath=os.path.dirname(class_filename)
        sf = os.path.basename(class_filename)
        class_filename = sf.split(".")[0]
        return_code=returncode
        mainclass=class_filename
        
        if returncode!=0:return True,self.mymagics.get_retinfo(),magics, code,fil_ename,class_filename,outpath,retstr
        # Generate executable file :end
        return bcancel_exec,retinfo,magics, code,fil_ename,class_filename,outpath,retstr
##do_create_codefile
    def do_create_codefile(self,magics,code, silent, store_history=True,
                    user_expressions=None, allow_stdin=True):
        return_code=0
        fil_ename=''
        bcancel_exec=False
        retinfo=self.mymagics.get_retinfo()
        retstr=''
        class_filename=''
        outpath=''
        
        # magics['pubclass']
        # self._log(magics['pubclass']+"\n")
        source_file=self.mymagics.create_codetemp_file(magics,code,suffix='.java')
        newsrcfilename=source_file.name
        fil_ename=newsrcfilename
        srcpath=os.path.dirname(source_file.name)
        sf = os.path.basename(source_file.name)
        newsrcfilename=os.path.join(srcpath,magics['pubclass']+".java")
        # self._log(newsrcfilename+"\n")
        os.rename(source_file.name ,newsrcfilename)
        fil_ename=newsrcfilename
        outpath=os.path.dirname(fil_ename)
        sf = os.path.basename(fil_ename)
        class_filename = sf.split(".")[0]
        
        return_code=True
        ############# only run gcc，no not run executable file
        if len(self.mymagics.addkey2dict(magics,'onlyrungcc'))>0:
            self.mymagics._log("only run gcc \n")
        return  bcancel_exec,self.mymagics.get_retinfo(),magics, code,fil_ename,class_filename,outpath,retstr
            
            
##do_preexecute
    def do_preexecute(self,code,magics, silent, store_history=True,
                user_expressions=None, allow_stdin=False):
        bcancel_exec=False
        retinfo=self.mymagics.get_retinfo()
        ##扫描代码
        #############send replcmd's command
        if magics['st']['runmode']=='repl':
            if hasattr(self, 'replcmdwrapper'):
                if self.mymagics.replcmdwrapper :
                    bcancel_exec=True
                    retinfo= self.mymagics.repl_sendcmd(code, silent, store_history,
                        user_expressions, allow_stdin,magics)
                    return bcancel_exec,retinfo,magics, code
        return bcancel_exec,retinfo,magics, code
