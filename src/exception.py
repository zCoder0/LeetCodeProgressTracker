import sys
from src.logger import logging
class ProjectException(Exception):


    def __init__(self,error_message, error_info:sys):
        self.error_message = error_message
        _,_,exc_tb = error_info.exc_info()

        if exc_tb is not None:
            self.file_name = exc_tb.tb_frame.f_code.co_filename
            self.line_number = exc_tb.tb_lineno
        else:
            self.file_name = "Unknown"
            self.line_number = 0

        logging.info(self.__str__())
    
    def __str__(self):
        return f"[Error] {self.error_message} ->  file path: {self.file_name}, ->  line no: {self.line_number}"