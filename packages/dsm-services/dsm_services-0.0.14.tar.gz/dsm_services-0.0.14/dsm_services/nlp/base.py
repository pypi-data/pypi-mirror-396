import requests
import time
from tqdm.auto import tqdm
from .. import utils

class Base:
    def __init__(self, service_uri, api_key, _timeout=100):
        """_summary_

        Args:
            service_uri (str): _description_
            api_key (str): _description_
        """
        self._service_uri = service_uri
        self._header = {
            'Authorization': f'Api-Key {api_key}'
        }
        res = requests.get(f"{self._service_uri}/keyword-extract/api/")
        utils.handle.check_http_status_code(response=res, extra_text="Can not connect to service")
        self._timeout = _timeout
    
    def submit_job(self, texts, wait_finish=True):
        utils.check.check_type(variable=texts, variableName='texts', dtype=list, child=str)
        res = requests.post(
            f"{self._service_uri}/keyword-extract/api/job/", headers=self._header,
            json={
                'type': self._type,
                'bulk': texts
            }
        )
        utils.handle.check_http_status_code(response=res)
        self._job_data = res.json()
        if wait_finish: self._wait_finish_job()
        return self._job_data
    
    def _get_job_status(self):
        job_id = self._job_data.get('job_id', 0)
        res = requests.get(f"{self._service_uri}/keyword-extract/api/job/{job_id}/is_finish/", headers=self._header)
        utils.handle.check_http_status_code(response=res)
        return res.json().get('is_finish')
    
    def _wait_finish_job(self):
        _status = self._get_job_status()
        for count in tqdm(range(self._timeout//10)):
            if not _status: 
                time.sleep(10)
                _status = self._get_job_status()
            time.sleep(0.1)
                
    def get_result(self):
        job_id = self._job_data.get('job_id', 0)
        res = requests.get(f"{self._service_uri}/keyword-extract/api/job/{job_id}/", headers=self._header)
        utils.handle.check_http_status_code(response=res)
        return res.json().get('output')