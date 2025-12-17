# # # -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 12:15:23 2023
@author: israe
"""
import logging
import time
import traceback
from datetime import datetime
import json
from functools import wraps
import inspect
from pprint import pformat
import asyncio
import typing
from icclogger.paths import logpath,logfile
from icclogger.colors import ConsoleColors

C = ConsoleColors.C
Y = ConsoleColors.Y
G = ConsoleColors.G
W = ConsoleColors.W
R = ConsoleColors.R
P = ConsoleColors.P
GR = ConsoleColors.GR
BR = ConsoleColors.BR
BG = ConsoleColors.BG
BY = ConsoleColors.BY
BBLUE = ConsoleColors.BBLUE
BP = ConsoleColors.BP
BC = ConsoleColors.BC
BW = ConsoleColors.BW

class CustomFormatter(logging.Formatter):
    # Formatos básicos de mensagens
    FORMATS = {
        logging.DEBUG: f"{C}[%(asctime)s] - %(message)s{W}",
        logging.INFO: f"{G}[%(asctime)s] - %(message)s{W}",
        logging.WARNING: f"{Y}[%(asctime)s] - %(message)s{W}",
        logging.ERROR: f"{R}[%(asctime)s] - %(message)s{W}",
    }

    def __init__(self,max_width=100):
        super().__init__()
        self.max_width = max_width

    def format(self, record):
        if isinstance(record.msg,(dict,list)):
            record.msg = pformat(record.msg,width=self.max_width)
        
        log_fmt = self.FORMATS.get(record.levelno, f"{W}%(message)s")
        formatter = logging.Formatter(log_fmt, datefmt='%d/%m/%Y %H:%M:%S')
        return formatter.format(record)

LOGGER = logging.getLogger('custom_logger')
LOGGER.setLevel(logging.INFO)

# Adiciona o formatter ao handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
LOGGER.addHandler(ch)

file_handler = logging.FileHandler(logfile, mode='a')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%d/%m/%Y-%H:%M:%S'))
LOGGER.addHandler(file_handler)

# função para registrar um log de erros no arquivo .txt na pasta logpath
def _log_error(error_msg):
    
    if not logpath.exists():
        print('Creating logs folder: ' + str(logpath))
        logpath.mkdir(parents=True,exist_ok=True)
    
    LOGGER.error(error_msg)
    return

#função para registrar o tempo de execução de uma função dentro do decorator log
def _register_time(mode,function,elapsed,args,kwargs):
    '''
    Register every functions inputs/data in "logs/" folder for further debug/analysis

    Parameters
    ----------
    mode : register log in csv or json format.
    function : function name.
    elapsed: elapsed time.
    args : register tuple of arguments that function executed.
    kwargs :register dict of kwargs that function executed.
    '''
    
    if mode.lower() not in ['json','csv']:
        
        print('\nmode not informed. Converted to csv')
        mode = 'csv'
    
    now = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
    
    if mode.lower() == 'json':
    
        dic = [{'date':f'{now}',
                'function_name':f'{function}',
                'exectime(s)':f'{round(elapsed,3):.3f}',
                # 'memory_used(kb)':f'{memory}',
                'args':f'{args}',
                'kwargs':f'{kwargs}'}]
    
        if not (logpath / 'functions_times.json').exists():
    
            # se não existir, cria o arquivo e dumpa direto
            with open((logpath / 'functions_times.json'),'w') as file:
                # file.write('[]')
                json.dump(dic,file)
    
        else:
    
            # se exitir, lê o arquivo antigo e atualiza as infos
            with open((logpath / 'functions_times.json'),'r') as file:
                old_data = json.load(file)
                
            old_data.append(dic[0])
        
            with open((logpath / 'functions_times.json'),'w') as file:
                json.dump(old_data,file)
                
    if mode.lower() == 'csv':
        
        string = f'{now};{function};{round(elapsed,3)};{args};{kwargs}'
        
        if not (logpath / 'functions_times.csv').exists():
    
            # se não existir, cria o arquivo e dumpa direto
            with open((logpath / 'functions_times.csv'),'a') as file:
                file.write('time;function_name;exectime(s);args;kwargs' + '\n')
                file.write(string + '\n')
        
        else:
            with open((logpath / 'functions_times.csv'),'a') as file:
                file.write(string + '\n')
    
    return

def __get_funclogs():
    '''
    Displays all def functions logs saved in rootfolder/logs/functions_times.csv
    by "log" decorator with time_it = "True".
    
    '''
    with open((logpath / 'functions_times.csv'),'r') as file:
        data = file.read()
        
        print(f'file location:\n\n{logpath}functions_times.csv')
        
    return data

def get_errorlogs():
    
    '''
    If you used @log decorator from "config" module, this function displays all
    error logs ocurred in def functions. Logs are saved in rootfolder/logs/error_logs.txt
    '''
    if not (logpath / 'error_logs.txt').exists():
        with open((logpath / 'error_logs.txt'),'w') as file:
            file.write('')

    with open((logpath / 'error_logs.txt'),'r') as file:
        
        data = file.read()
        print(f'file location:\n\n{logpath}\\error_logs.txt')
        
    return data
 
#função principal como decorator
def log(
        # timeit=False,
        error_log:bool = True,
        retry:bool = False,
        max_retries:int = 3,
        delay:int = 3,
        delay_retry_multiplier:int = 2,
        ):
    
    '''
    Use log as decorator for any function.\
    \nIt logs execution time. Also similar to Pydantic, it can validate function params type hints when informed.

    Examples:
    @log\
    \ndef my_func(param1:int, param2:list, param3:str, param4:dict):

    Parameters:
        error_log (bool) : If True, it will log the error message in a file named 'error_logs.txt' in the root folder.
    
    Returns:
        A decorator function that logs the execution time of the decorated function.
    '''
    global C,Y,G,W,R,P

    global LOGGER
    def decorator(func):

        def check_type(value, expected_type):
                # Handle Union types
                if typing.get_origin(expected_type) is typing.Union:
                    # Check if the value matches any of the Union types
                    return any(
                        (value is None and type(None) in typing.get_args(expected_type)) or 
                        _safe_isinstance(value, arg) 
                        for arg in typing.get_args(expected_type)
                    )
                
                # Handle List and other generic types
                if typing.get_origin(expected_type) is list:
                    # Check if it's a list and all elements match the list's type
                    if not isinstance(value, list):
                        return False
                    
                    # Get the type of list elements
                    list_type = typing.get_args(expected_type)[0]
                    return all(_safe_isinstance(item, list_type) for item in value)
                
                # Regular type checking
                return _safe_isinstance(value, expected_type)

        def _safe_isinstance(obj, type_):
            """
            Safely check isinstance for both regular and generic types
            """
            # Handle parameterized generics
            origin = typing.get_origin(type_)
            if origin is not None:
                # For generics like List[str], check against the origin (list)
                return (
                    isinstance(obj, origin) and 
                    (not typing.get_args(type_) or 
                        all(_safe_isinstance(item, typing.get_args(type_)[0]) for item in obj))
                )
            
            # Standard isinstance for non-generic types
            return isinstance(obj, type_)

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args,max_retries:int = max_retries,**kwargs):
                new_delay = delay  # Mantem o delay atual
                if not retry:
                    max_retries = 1

                for attempt in range(max_retries):
                    try:
                        # if not isinstance(timeit, bool):
                        #     raise Exception ('timeit decorator must be "bool" type ')
                        
                        LOGGER.info(f'{BP}Executing [--->] {func.__name__}{W}')

                        type_hints = func.__annotations__
                        for arg_name, arg_value in zip(func.__code__.co_varnames, args):
                            if arg_name in type_hints:
                                expected_type = type_hints[arg_name]
                                if not check_type(arg_value, expected_type):
                                    LOGGER.info(f"{R}PARAM Error: {func.__name__} expected {C}{arg_name}{R} to be {G}{expected_type}{R}, but got {Y}{type(arg_value).__name__}{R}")
                                    LOGGER.error(f"PARAM Error: {func.__name__} expected {arg_name} to be {expected_type}, but got {type(arg_value).__name__}")
                            else:
                                if arg_name not in ['self','cls']:
                                    LOGGER.warning(f"PARAM Missing: {G}{func.__name__}{Y} is missing type hint for param {C}{arg_name}{Y}")
                                    
                        for kwarg_name, kwarg_value in kwargs.items():
                            if kwarg_name in type_hints:
                                expected_type = type_hints[kwarg_name]
                                if not check_type(kwarg_value, expected_type):
                                    LOGGER.info(f"{R}PARAM Error: {func.__name__} expected {C}{kwarg_name}{R} to be {G}{expected_type}{R}, but got {Y}{type(kwarg_value).__name__}{R}")
                                    LOGGER.error(f"PARAM Error: {func.__name__} expected {kwarg_name} to be {expected_type}, but got {type(kwarg_value).__name__}")
                            else:
                                if kwarg_name not in ['self','cls']:
                                    LOGGER.warning(f"PARAM Missing: {G}{func.__name__}{Y} is missing type hint for param {C}{kwarg_name}{Y}")
                                
                        start = time.time()
                        result = await func(*args,**kwargs)
                        end = time.time()
                        elapsed = end - start
                        
                        LOGGER.info(f'{P}Finished [--->] {func.__name__} in : {round(elapsed,3)} seconds{W}')
                                
                        # if timeit:
                        #     _register_time(mode='csv',
                        #                 function = func.__name__,
                        #                 elapsed = elapsed,
                        #                 args=args,
                        #                 kwargs=kwargs) 
                            
                        return result

                    except Exception as e:
                        LOGGER.info(f"{R}{traceback.format_exc()}{W}")
                        
                        if error_log:
                            # tb = traceback.format_exc()
                            exc_type, exc_value, exc_tb = e.__class__, e, e.__traceback__
                            ERROR_STRING = f"[--->] Exception Class: {exc_type.__name__} | Message: {exc_value} | Traceback: "

                            traceback_details = traceback.extract_tb(exc_tb)
                            # Iterando sobre os detalhes do traceback para capturar a linha do erro
                            for tb_detail in traceback_details:
                                ERROR_STRING += "file: " + str(tb_detail.filename).split('\\')[-1] + " | "  
                                ERROR_STRING += "function: " + str(tb_detail.name) + " | " 
                                ERROR_STRING += "line: " + str(tb_detail.lineno) + " | " 
                                ERROR_STRING += "detail: " +str(tb_detail.line) + " | "

                            full_error_message = f"{ERROR_STRING}"
                            _log_error(full_error_message)

                        if attempt + 1 == max_retries:
                            LOGGER.info(f"{R}{'try number:'} {attempt + 1}/{max_retries} failed{W}")
                            #logging retries only if > 1
                            if attempt + 1 > 1:
                                LOGGER.info(f"{R}Max retries reached. Propagating error.\n{e}{W}")
                                LOGGER.error(f"Max retries reached. Propagating error.{e}")
                            return

                        new_delay *= delay_retry_multiplier
                        LOGGER.info(f"{R}try number: {attempt + 1}/{max_retries} failed{W}")
                        LOGGER.info(f"{R}retrying number {attempt + 2} in:' {new_delay} seconds{W}")
                        LOGGER.info(f"{R}'retrying number {attempt + 2} in:' {new_delay} seconds{W}")
                        await asyncio.sleep(new_delay)
                        
            return async_wrapper
        
        else:
            @wraps(func)
            def sync_wrapper(*args,max_retries:int = max_retries,**kwargs):
                if not retry:
                    max_retries = 1

                new_delay = delay  # Mantem o delay atual
                for attempt in range(max_retries):
                    try:
                        # if not isinstance(timeit, bool):
                        #     raise Exception ('timeit decorator must be "bool" type ')

                        LOGGER.info(f'{BP}Executing [--->] {func.__name__}{W}')
                        type_hints = func.__annotations__
                        for arg_name, arg_value in zip(func.__code__.co_varnames, args):
                            if arg_name in type_hints:
                                expected_type = type_hints[arg_name]
                                if not check_type(arg_value, expected_type):
                                    LOGGER.info(f"{R}PARAM Error: {func.__name__} expected {C}{arg_name}{R} to be {G}{expected_type}{R}, but got {Y}{type(arg_value).__name__}{R}")
                                    LOGGER.error(f"PARAM Error: {func.__name__} expected {arg_name} to be {expected_type}, but got {type(arg_value).__name__}")
                            else:
                                if arg_name not in ['self','cls']:
                                    LOGGER.warning(f"PARAM Missing: {G}{func.__name__}{Y} is missing type hint for param {C}{arg_name}{Y}") 
  
                        for kwarg_name, kwarg_value in kwargs.items():
                            if kwarg_name in type_hints:
                                expected_type = type_hints[kwarg_name]
                                if not check_type(kwarg_value, expected_type):
                                    LOGGER.info(f"{R}PARAM Error: {func.__name__} expected {C}{kwarg_name}{R} to be {G}{expected_type}{R}, but got {Y}{type(kwarg_value).__name__}{R}")
                                    LOGGER.error(f"PARAM Error: {func.__name__} expected {kwarg_name} to be {expected_type}, but got {type(kwarg_value).__name__}")    
                            else:
                                if kwarg_name not in ['self','cls']:
                                    LOGGER.warning(f"PARAM Missing: {G}{func.__name__}{Y} is missing type hint for param {C}{kwarg_name}{Y}")
            
                        start = time.time()
                        result = func(*args,**kwargs)
                        end = time.time()
                        elapsed = end - start
                        
                        LOGGER.info(f'{P}Finished [--->] {func.__name__} in : {round(elapsed,3)} seconds{W}')
                        
                        # if timeit:
                        #     _register_time(mode='csv',
                        #                 function = func.__name__,
                        #                 elapsed = elapsed,
                        #                 args=args,
                        #                 kwargs=kwargs) 
                        return result

                    except Exception as e:
                        LOGGER.info(f"{R}{traceback.format_exc()}{W}")

                        if error_log:
                            # tb = traceback.format_exc()
                            exc_type, exc_value, exc_tb = e.__class__, e, e.__traceback__
                            ERROR_STRING = f"[--->] Exception Class: {exc_type.__name__} | Message: {exc_value} | Traceback: "

                            traceback_details = traceback.extract_tb(exc_tb)
                            # Iterando sobre os detalhes do traceback para capturar a linha do erro
                            for tb_detail in traceback_details:
                                ERROR_STRING += "file: " + str(tb_detail.filename).split('\\')[-1] + " | "  
                                ERROR_STRING += "function: " + str(tb_detail.name) + " | " 
                                ERROR_STRING += "line: " + str(tb_detail.lineno) + " | " 
                                ERROR_STRING += "detail: " +str(tb_detail.line) + " | "

                            full_error_message = f"{ERROR_STRING}"
                            _log_error(full_error_message)

                        if attempt + 1 == max_retries:
                            LOGGER.info(f"{R}{'try number:'} {attempt + 1}/{max_retries} failed{W}")
                            #logging retries only if > 1
                            if attempt + 1 > 1: 
                                LOGGER.info(f"{R}Max retries reached. Propagating error.\n{e}{W}")
                                LOGGER.error(f"Max retries reached. Propagating error.{e}")
                            return

                        new_delay *= delay_retry_multiplier
                        LOGGER.info(f"{R}try number: {attempt + 1}/{max_retries} failed{W}")
                        LOGGER.info(f"{R}retrying number {attempt + 2} in:' {new_delay} seconds{W}")
                        time.sleep(new_delay)

            return sync_wrapper
    return decorator
