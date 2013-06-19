import os
import tempfile
import twill.commands as tc


class ExposureDownloadError(Exception):
    pass


class ExposureDownloader(object):
    def __init__(self, host):
        self.host = host
        self._login = host + '/accounts/login/'
        self._page = host + '/exposure/export_population'

    def login(self, username, password):
        tc.go(self._login)
        tc.formvalue(2, 'username', username)
        tc.formvalue(2, 'password', password)
        tc.submit()

    def download(self, lat1, lng1, lat2, lng2):
        """Download the data in CSV format and return the filename"""
        tc.go(self._page + '?outputType=csv&lat1=%s&lng1=%s&lat2=%s&lng2=%s'
              % (lat1, lng1, lat2, lng2))
        http_code = tc.browser.result.get_http_code()
        result = tc.browser.get_html()
        if not result:
            raise RuntimeError('No data found for region (%s %s)-(%s %s)',
                               lat1, lng1, lat2, lng2)
        if http_code == 200:
            # save csv on a temporary file
            fd, fname = tempfile.mkstemp(suffix='.csv')
            os.close(fd)
            with open(fname, 'w') as csv:
                csv.write(result)
            return fname
        else:
            raise ExposureDownloadError(result)
