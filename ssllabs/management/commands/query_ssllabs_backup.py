#!/usr/bin/env python

import time
import json
from urllib import parse
import random
import logging

import requests

from requests.exceptions import Timeout

from django.core.management.base import BaseCommand, CommandError
from ssllabs.models import Host

dev_mode = True
max_retries = 5
max_wait_duration = 600  # 10 minutes

logging.basicConfig(level=logging.INFO)

# Disable warning about unconfigured logger, only needed if used as a library
# try:
#     from logging import NullHandler
# except ImportError:
#     class NullHandler(logging.Handler):
#         def emit(self, record):
#             pass
# logging.getLogger(__name__).addHandler(NullHandler())

log = logging.getLogger(__name__)


class SSLLabsBadResponseException(Exception):
    pass


class SSLLabsBadParametersException(Exception):
    pass


def _sleep_jitter(interval, jitter):
    '''Sleep for a base interval with a random jitter. Arguments are in seconds.
    '''
    time.sleep(float(interval) + (random.random() * float(jitter)))


def _ssllabs_request(endpoint, params, attempts=0):
    api_url = 'https://api.ssllabs.com/api/v2/'
    if dev_mode:
        api_url = 'https://api.dev.ssllabs.com/api/v2/'

    retry = 0

    try:
        response = requests.get(urlparse.urljoin(api_url, endpoint), params=params, timeout=5)
    except Timeout as e:
        if attempts < max_retries:
            log.warning(e)
            retry = 30
        else:
            log.fatal(e)
    except Exception as e:
        log.fatal(e)

    if retry:
        _sleep_jitter(retry, 5)
        return _ssllabs_request(endpoint, params, attempts + 1)

    code = response.status_code

    if code == 200:
        return response.json()
    elif attempts >= max_retries:
        log.fatal('Giving up')
        raise SSLLabsBadResponseException('Bad response from server HTTP%d - %s' % (code, response.text))
    elif code == 400:
        raise SSLLabsBadParametersException('Bad parameters for "%s" endpoint:%s' % (endpoint, params))
    elif code == 429:
        # Rate too high
        retry = 10
    elif code == 503:
        # Unavailable
        retry = 30
    elif code == 529:
        # Overloaded
        retry = 120
    elif code != 200:
        raise SSLLabsBadResponseException('Bad response from server HTTP%d - %s' % (code, response.text))

    if retry:
        _sleep_jitter(retry, 10)
        log.debug('Retrying...')
        return _ssllabs_request(endpoint, params, attempts + 1)


def analyze_host(host, maxage=1, use_cache=True):
    log.info('Starting Analyze of host: %s' % host)

    params = {
        'host': host,
        'publish': 'off',
        'maxAge': maxage,
        'all': 'done',
        'ignoreMismatch': 'on',
    }

    try:
        init_params = params.copy()
        if not use_cache:
            init_params.update({'startNew': 'on'})
        else:
            init_params.update({'fromCache': 'on'})
        response = _ssllabs_request('analyze', init_params)
    except Exception as e:
        log.error('Analyze Error: %s' % e)
        return None

    if response.get('status') == 'READY':
        return response

    logging.info('%s - %s' % (response.get('status'), host))

    _sleep_jitter(5, 2)  # Initial wait before polling

    params = {
        'host': host,
        'all': 'done',
    }

    start_time = time.time()

    while True:
        try:
            response = _ssllabs_request('analyze', params)
            if response.get('status') == 'READY':
                return response

            logging.info('%s - %s' % (response.get('status'), host))
        except Exception as e:
            log.error('Analyze Error while waiting: %s' % e)
            break

        if time.time() - start_time >= max_wait_duration:
            log.fatal('Waited too long for results')
            break

        _sleep_jitter(10, 5)

    return None


def run_mp(hosts, use_cache=True, show_cn=False, dump_json=False):
    from multiprocessing import Pool

    # Number of processes should match the number of CPUs you have.
    # Assignment will be processes/n_processors.  Or whatever, I don't care.
    pool = Pool(processes=4)
    results = [pool.apply_async(analyze_host, args=(h, 1, use_cache)) for h in hosts]

    finished = []
    for p in results:
        data = p.get()
        if data:
            finished.append(data)

    for data in finished:
        for ep in data.get('endpoints'):
            # Find the endpoint that has a server name
            if 'serverName' in ep and ep.get('progress') == 100:
                print('Host: %s' % data.get('host'))
                print('  IP: %s' % ep.get('ipAddress'))
                print('  Server Name: %s' % ep.get('serverName'))

                details = ep.get('details', {})

                if show_cn:
                    cert = details.get('cert', {})

                    for name in cert.get('commonNames', []):
                        print('  Common Name: %s' % name)

                    for name in cert.get('altNames', []):
                        print('  Alt Name: %s' % name)

                print('  HeartBleed: %s' % details.get('heartbleed', False))
                print('  POODLE: %s' % details.get('poodle', False))

                print('  Status: %s' % ep.get('statusMessage'))
                print('  Grade: %s' % ep.get('grade'))
                print('  Grade*: %s' % ep.get('gradeTrustIgnored'))

        if dump_json:
            with open('%s.json' % data.get('host'), 'wb') as fp:
                json.dump(data, fp, indent=2, sort_keys=True)


class Command(BaseCommand):
    help = 'Queries the SSL labs API, using database records that are queued'

    def add_arguments(self, parser):
        #parser.add_argument('host', nargs='+')
        parser.add_argument('--no-cache', required=False, action='store_true', dest='no-cache', help='Bypass cache and force re-scan of hostname')
        parser.add_argument('--show-cn', required=False, action='store_true', dest='show-cn')
        parser.add_argument('--dump-json', required=False, action='store_true', dest='dump-json')

    def handle(self, *args, **options):
        target_hosts = Host.objects.filter(status="QUEUED")
        #for h in target_hosts:
        #if options['no-cache']:
        #    self.stdout.write('hi')
        #self.stdout.write(options['no-cache'])
        run_mp(target_hosts, not options['no-cache'], options['show-cn'], options['dump-json'])
        

