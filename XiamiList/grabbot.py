# python 3

import requests
import logging
from random import randint
from time import sleep
from functools import wraps

USER_AGENTS = ['Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
               'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)  \
               Chrome/50.0.2661.102 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
               ]

def retry(ExceptionToCheck, tries=3, delay=3, backoff=1):
    """Retry calling the decorated function using an exponential backoff.

    original from: http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "Retry (%s) in %d seconds. (ERROR: %s) " \
                          % (f.__name__.upper(), mdelay, str(e))
                    logging.warning(msg)

                    sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


class GrabBot(object):
    """ Simple bot to get web content """

    def __init__(self, proxy=None):
        self.proxies = {'http': proxy,
                        'https': proxy}

    @retry(requests.exceptions.RequestException, backoff=2)
    def _get(self, url, **kwargs):
        ua = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
        return requests.get(url, timeout=(10, 60), proxies=self.proxies,
                            headers={'User-Agent': ua}, **kwargs)

    @retry(requests.exceptions.RequestException, backoff=2)
    def _post(self, url, data):
        ua = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
        return requests.post(url, data=data, timeout=(10, 60),
                             proxies=self.proxies, headers={'User-Agent': ua})

    def get(self, url, **kwargs):
        r = None
        try:
            r = self._get(url, **kwargs)
        except requests.exceptions.RequestException as err:
            logging.warning('Failed to connect URL(%s), %s' % (url, err))
        return r

    def post(self, url, data):
        r = None
        try:
            r = self._post(url, data=data)
        except requests.exceptions.RequestException as err:
            logging.warning('Failed to post data to URL(%s), %s' % (url, err))
        return r
