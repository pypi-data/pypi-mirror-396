import requests
from typing import Any, Dict


class CollectorNodeController():
    def __init__(self, hostname_or_ip:str, verbose=False):
        """Initializes the controller for the SkuTek CollectorNode Computer associated with the specified URL
        
        :param hostname_or_ip: url or IP address for target devices
        """
                
        if hostname_or_ip.startswith("https://"):
            raise ValueError("Secure http not supported! (Collector Node url must begin with 'http' not 'https')")
        # add http:// manually if not provided
        elif not hostname_or_ip.startswith("http://"):
            hostname_or_ip = f"http://{hostname_or_ip}"
        self.address = hostname_or_ip
        self.verbose = verbose

    # _________________________________________________________________________
    def __get(self, route: str, data: Dict[str, Any] = {}) -> Dict[str, Any]:
        if self.verbose:
            print(f"sending GET to {route} with payload {data}")

        resp = requests.get(route, json=data, timeout=5)
        if resp.ok:
            return resp.json()
        else:
            if resp.headers.get('content-type') == 'application/json':
                resp_data = resp.json()
                error_code = resp_data['code']
                error_msg  = resp.reason + '\n' + resp_data['error']
            else:
                error_code = resp.status_code
                error_msg  = resp.reason
            raise requests.ConnectionError(f"GET Request to {route} failed due to {error_code}:{error_msg}")


    # _________________________________________________________________________
    def __post(self, route: str, data: Dict[str, Any] = {}) -> Dict[str, Any]:
        if self.verbose:
            print(f"sending POST to {route} with payload {data}")

        resp = requests.post(route, json=data, timeout=5)
        if resp.ok:
            return resp.json()
        else:
            if resp.headers.get('content-type') == 'application/json':
                resp_data = resp.json()
                error_code = resp_data['code']
                error_msg  = resp.reason + '\n' + resp_data['error']
            else:
                error_code = resp.status_code
                error_msg  = resp.reason
            raise requests.ConnectionError(f"POST Request to {route} failed due to {error_code}:{error_msg}")

    # _________________________________________________________________________
    @property
    def rest_url(self):
        """url for the REST interface of the target CollectorNode"""
        return self.address + '/rest'
    
    # _________________________________________________________________________
    def get_pipeline_url(self, pipeline_id:int):
        """URL for the desired Pipeline"""
        return self.rest_url + f"/pipelines/{pipeline_id}"

    # _________________________________________________________________________
    def get_reception_info(self, pipeline_id:int):
        """Retrieves the streaming reception information for this pipeline

        :return: a dictionary containing the ip address (str), port (int), and mac address (str) on which 
            this pipeline is listening for incoming streams. Keys are ('ip', 'port', 'mac')
        """
        url = self.get_pipeline_url(pipeline_id) + '/listening_on'
        return self.__get(url)

    # _________________________________________________________________________
    def set_reception_port(self, pipeline_id:int, port:int):
        """Sets the listening port for the desired pipeline

        :return: a dictionary containing the ip address (str), port (int), and mac address (str) on which 
            this pipeline is listening for incoming streams. Keys are ('ip', 'port', 'mac')
        """
        url = self.get_pipeline_url(pipeline_id) + '/listening_on'
        return self.__post(url, data={'port':port})
        
    # _________________________________________________________________________
    def send_signal(self, pipeline_id:int, signal:str):
        """Sets the listening port for the desired pipeline

        :return: a dictionary containing the ip address (str), port (int), and mac address (str) on which 
            this pipeline is listening for incoming streams. Keys are ('ip', 'port', 'mac')
        """
        url = self.get_pipeline_url(pipeline_id) + '/listening_on'
        return self.__post(url, data={'signal':signal.upper()})
        