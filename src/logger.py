from datetime import datetime

import colorama
from colorama import Back, Fore, Style


class Logger():
    def __init__(self, task: str):
        self.task = task
        colorama.init(True)

    def important(self, message: str):
        formatted_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Style.BRIGHT}{Fore.BLACK}{formatted_date_time}{Style.RESET_ALL}{Style.BRIGHT}{Fore.MAGENTA} IMPT     {Style.RESET_ALL}{Fore.MAGENTA}{self.task}{Style.RESET_ALL} {message}")
    
    def info(self, message: str):
        formatted_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Style.BRIGHT}{Fore.BLACK}{formatted_date_time}{Style.RESET_ALL}{Style.BRIGHT}{Fore.BLUE} INFO     {Style.RESET_ALL}{Fore.MAGENTA}{self.task}{Style.RESET_ALL} {message}")

    def success(self, message: str):
        formatted_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Style.BRIGHT}{Fore.BLACK}{formatted_date_time}{Style.RESET_ALL}{Style.BRIGHT}{Fore.GREEN} SCCS     {Style.RESET_ALL}{Fore.MAGENTA}{self.task}{Style.RESET_ALL} {message}")

    def error(self, message: str):
        formatted_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Style.BRIGHT}{Fore.BLACK}{formatted_date_time}{Style.RESET_ALL}{Style.BRIGHT}{Fore.RED} ERR      {Style.RESET_ALL}{Fore.MAGENTA}{self.task}{Style.RESET_ALL} {message}")
    
    def debug(self, message: str):
        formatted_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Style.BRIGHT}{Fore.BLACK}{formatted_date_time}{Style.RESET_ALL}{Style.BRIGHT}{Fore.YELLOW} DBUG     {Style.RESET_ALL}{Fore.MAGENTA}{self.task}{Style.RESET_ALL} {message}")