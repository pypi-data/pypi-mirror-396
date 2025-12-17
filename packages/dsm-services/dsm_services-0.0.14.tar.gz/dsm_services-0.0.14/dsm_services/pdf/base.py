import requests
import time
from tqdm.auto import tqdm
from .. import utils
import uuid
import io
import os

class PDF2Text:
    def __init__(self, service_uri, api_key, extract_type='Normal', _timeout=100):
        """_summary_

        Args:
            service_uri (str): _description_
            api_key (str): _description_
        """
        self._service_uri = service_uri
        self._header = {
            'Authorization': f'Api-Key {api_key}'
        }
        res = requests.get(f"{self._service_uri}/pdf2text/api/")
        utils.handle.check_http_status_code(response=res, extra_text="Can not connect to service")
        self.result = []
        
        if extract_type not in ['Normal', 'Advance-OCR']:
            raise Exception("`extract_type` must be 'Normal' or 'Advance-OCR'")
        self.extract_type = extract_type
        self._timeout = _timeout
        
        
    def _get_status(self):
        _id = self._file_data.get('id', 0)
        res = requests.get(f"{self._service_uri}/pdf2text/api/file/{_id}/is_finish/", headers=self._header)
        utils.handle.check_http_status_code(response=res)
        return res.json().get('is_finish')
    
    def _wait_finish(self):
        _status = self._get_status()
        for count in tqdm(range(self._timeout//10)):
            if not _status: 
                time.sleep(10)
                _status = self._get_status()
            time.sleep(0.1)
            
    def upload_file(self, file, name=None, description='-', wait_finish=True):
        if io.BufferedReader == type(file):
            res = requests.post(f"{self._service_uri}/pdf2text/api/file/", headers=self._header,
                data={
                    'extract_type': self.extract_type,
                    'name': uuid.uuid4().hex,
                    'description': description
                },
                files={
                    'file': file
                }
            )
        elif type(file) == str or os.path.exists(file):
            f_name = os.path.basename(file)[:96] if name == None else name[:96]
            res = requests.post(f"{self._service_uri}/pdf2text/api/file/", headers=self._header,
                data={
                    'extract_type': self.extract_type,
                    'name': f_name,
                    'description': description
                },
                files={
                    'file': (f'{f_name}.pdf', open(file,'rb').read())
                }
            )
        else:
            raise Exception(f"path {file} does not exists or expect `io.BufferedReader` but got {type(file)}")
        utils.handle.check_http_status_code(response=res)
        self._file_data = res.json()
        if wait_finish: self._wait_finish()
        return self._file_data
    
    def fetch_result(self):
        self.result = []
        _id = self._file_data.get('id', 0)
        _url = f"{self._service_uri}/pdf2text/api/page/?file={_id}"
        while True:
            res = requests.get(_url, headers=self._header)
            utils.handle.check_http_status_code(response=res)
            _data = res.json()
            self.result += _data.get('results', [])
            if _data.get('next'): _url = _data.get('next')
            else: break
        self.result = sorted(self.result, key=lambda elm: elm.get('page'))
        return self.result