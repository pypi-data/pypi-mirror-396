import requests
import concurrent.futures as cf
import time

from typing import Dict, Any, Generator, Tuple, Optional, Union, List,Sequence


__all__ = ['send_simultanesous_post_requests','run_functions_in_parallel']

###############################################################################
def run_functions_in_parallel(funcs,
            args_list:Optional[Sequence[Sequence]]=None,
            kwargs_list:Optional[Sequence[Dict[str,Any]]]=None):

    """runs the functions in parallel as fast as possible to mimic simultanesous execution. 

    :param funcs: list of functions to run in paralle;
    :param args_list: list of arguments passed to each function. Should be a
        list of lists for each function
    :param kwargs_list: list of keyworkd-arguments passed to each function. Should be a
        list of dictionarys for each function

    :return: tuple containing (time_taken_to_complete_in_nanoseconds, 
        list of results from each function)

    """
    start_ns = time.monotonic_ns()
    if not isinstance(funcs, (tuple,list)):
        raise TypeError("funcs must a be list or tuple of functions to call")
    if args_list is None:
        args_list = [tuple()] * len(funcs)
    if kwargs is None:
        kwargs = [tuple()] * len(funcs)
    
    assert len(args) == len(funcs), "not enough positional arguments provided for each function call"
    assert len(kwargs) == len(funcs), "not enough keyword arguments provided for each function call"

    def mapped_func(func_to_run, *args, **kwargs):
        return func_to_run(*args, **kwargs)

    mapped_args_list = ([func] + list(args) for func,args in zip(funcs,args_list))

    executor = cf.ThreadPoolExecutor( max_workers=len(funcs) )
    futures = executor.map(mapped_func, *mapped_args_list, **kwargs_list)

    cf.wait(futures)
    end_ns = time.monotonic_ns()
    return (end_ns - start_ns), [fut.result() for fut in futures]

###############################################################################
def send_simultanesous_post_requests(*transmit_infos:Sequence, timeout=3):
    """ Sends the specified post requests in parallel as fast as possible to 
    mimic simultanesous execution. 

    :param transmit_infos: list or tuple of sub-tuples containing (url, json_data)
        for each post request to send

    :return: tuple containing (time_taken_to_complete_in_nanoseconds, 
        list of responses from all post requests)
    """
    start_ns = time.monotonic_ns()

    def send_post(url, data_dict):
        return requests.post(url, json=data_dict, timeout=timeout)

    executor = cf.ThreadPoolExecutor( max_workers=len(transmit_infos) )
    futures = executor.map(send_post, *transmit_infos)

    cf.wait(futures)
    
    end_ns = time.monotonic_ns()

    return (end_ns - start_ns), [fut.result() for fut in futures]

