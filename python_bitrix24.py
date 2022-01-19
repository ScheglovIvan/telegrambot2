import sys
import requests
import json


class Bitrix24Connection(object):
    api_main_url = None
    _api_login = None
    _api_password = None
    _api_url = None

    def __init__(self, api_login, api_password, api_main_url):
        self._api_login = api_login
        self._api_password = api_password
        self.api_main_url = api_main_url
        self._api_url = api_main_url

    def _build_url(self, path):
        return "%s%s" % (self._api_url, path)

    def _build_data(self, data=None):
        _data = {
            'LOGIN': self._api_login,
            'PASSWORD': self._api_password,
        }

        if data:
            _data.update(data)

        result_data = {}

        for k, v in _data.items():
            if sys.version_info.major < 3:
                result_data[unicode(k).encode('utf-8')] = unicode(v).encode('utf-8')
            else:
                result_data[str(k).encode('utf-8')] = str(v).encode('utf-8')


        return result_data
    
    def GetRequest(self, url, headers=None):
        url = self._build_url(url)
        
        try:
            r = requests.get(url, headers=headers)
            return r
        except:
            return None
        

    
    def PostRequest(self, url, data=None):
        url = self._build_url(url)

        if data:
            data = self._build_data(data)
        else:
            data = self._build_data()
        
        try:
            r = requests.post(url, data=data)
            return r
        except:
            return None
        
    def GetPHPSessionId(self):
        data = {
            'TITLE': "test"
        }

        r = self.PostRequest('crm/configs/import/lead.php', data)

        PHPSessionId = r.headers['Set-Cookie'].split(";")[0]

        return PHPSessionId
    
    def GetFile(self, url):
        PHPSessionId = self.GetPHPSessionId()

        headers = {
            "cookie": PHPSessionId
        }
        url = self._build_url(url)

        r = requests.get(url, headers=headers)
        f = r.content

        return f
    
    # def UploadImage(self, file):
    #     data = {
    #         'file': file
    #     }

    #     r = self.PostRequest('bitrix/components/bitrix/main.file.input/ajax.php?mfi_mode=upload&cid=67f538be0dcd0798c8924ca8e910bf48&sessid=7d22cf970f8ff1ebbed66135b3587dd2&s=cf521a32835f44716f1d198bddf4c16b5105aac26a0fb2615d96fbe0062a086a', data)

    #     print(r.content)



