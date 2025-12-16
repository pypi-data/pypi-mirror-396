import sys
from colorama import Fore,Style
import datetime



class Logger:
    __slots__ = ("file","debugflag","do_log","filing","log_file")
    
    def __log(self,msg:tuple[str,str], error=False):
        out = sys.stderr if error else sys.stdout
        if self.do_log:
            print(msg[1], file=out)
            if self.filing:
                print(msg[0], file=self.log_file)
    
    def __init__(self,file:str,debug=True,filing=True):
        self.file = file
        self.debugflag = debug
        self.do_log = True
        self.filing = filing
        self.log_file = open(f"{file}-{datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.log", mode="w")
    
    def debug(self, msg:str):
        if self.debugflag:
            self.__log(self.fmt(msg, Fore.GREEN ,"DEBUG"))
    
    def info(self,msg:str):
        self.__log(self.fmt(msg, Fore.BLUE ,"INFO"))
    
    def warn(self,msg:str):
        self.__log(self.fmt(msg, Fore.YELLOW ,"WARN"))
    
    def error(self,msg:str):
        self.__log(self.fmt(msg, Fore.RED ,"ERROR"),True)
    
    def on(self):
        self.do_log = True
    
    def off(self):
        self.do_log = False
    
    def switch(self):
        self.do_log = not self.do_log
    
    def fmt(self,msg,cl,ll):
        tlate = f"{self.file} | [{{}}{ll}{{}}]:{msg}"
        nc = tlate.format("","")
        cl_ret = tlate.format(cl,Style.RESET_ALL)
        return nc,cl_ret
    
    def __del__(self):
        self.log_file.close()
    
    __exit__ = __del__
    
    def __call__(self ,msg:str):
        self.info(msg)