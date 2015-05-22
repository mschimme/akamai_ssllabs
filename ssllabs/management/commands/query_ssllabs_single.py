#!/usr/bin/env python

import time
import json
from urllib import parse
import random
import logging

import requests

from requests.exceptions import Timeout

from django.conf import settings

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
        response = requests.get(parse.urljoin(api_url, endpoint), params=params, timeout=5)
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

    #Mark this host as running
    #thishost = Host.objects.get(host=host)
    #thishost.status="RUNNING"
    #thishost.save()

    try:
        init_params = params.copy()
        if not use_cache:
            init_params.update({'startNew': 'on'})
        else:
            init_params.update({'fromCache': 'on'})
        response = _ssllabs_request('analyze', init_params)
    except Exception as e:
        log.error('Analyze Error: %s' % e)
        host.status='ERROR'
        host.statusMessage = e
        host.save()
        return None

    if response.get('status') == 'READY' or response.get('status') == 'ERROR':
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
            if response.get('status') == 'READY' or response.get('status') == 'ERROR':
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


def run_mp(hosts, use_cache=True, dump_json=False):
    #from multiprocessing import Pool

    # Number of processes should match the number of CPUs you have.
    # Assignment will be processes/n_processors.  Or whatever, I don't care.
    #pool = Pool(settings.PROCESSES)
    #results = [pool.apply_async(analyze_host, args=(h, 1, use_cache)) for h in hosts]

    #finished = []

    #for h in hosts:
    #    thisdata = analyze_host(h)
    #    finished.append(thisdata)

    #for p in results:
    #    data = p.get()
    #    if data:
    #        finished.append(data)

    for h in hosts:
        data = analyze_host(h)

        if (data.get('status') == 'ERROR'):
            print ('Error with %s: %s' % (data.get('host'), data.get('statusMessage')))
            h = Host.objects.get(host=data.get('host'))
            h.status = data.get('status')
            h.statusMessage = data.get('statusMessage')
            h.grade = 'ERR'
            h.gradeTrustIgnored = 'ERR'
            h.supportsRC4 = None
            h.signatureAlg = None
            h.startTime = None
            h.endTime = None
            h.save()
            continue

        for ep in data.get('endpoints'):
            # Find the endpoint that has a server name
            if ep.get('statusMessage').upper() == 'READY' and ep.get('progress') == 100:
                thishost = data.get('host')
                startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get('startTime') / 1000))
                endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get('testTime') / 1000))
                #print('TZ: %s' % dtz_string)

                #startTime = 
                #endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get('testTime') / 1000))

                print('Host: %s' % data.get('host'))
                print('  IP: %s' % ep.get('ipAddress'))
                print('  Server Name: %s' % ep.get('serverName'))

                details = ep.get('details', {})

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
                print('  Signature Algorithm: %s' % cert.get('sigAlg'))
                print('  Supports RC4: %s' % details.get('supportsRc4'))
                print('  Start Time: %s' % startTime)
                print('  End Time: %s' % endTime)
                print('  Not Before: %s' % cert.get('notBefore'))
                print('  Not After: %s' % cert.get('notAfter'))

                # Update the database!
                h = Host.objects.get(host=thishost)

                h.grade = ep.get('grade')
                h.gradeTrustIgnored = ep.get('getTrustIgnored')
                h.ipAddress = ep.get('ipAddress')
                h.supportsRC4 = details.get('supportsRc4')
                h.signatureAlg = cert.get('sigAlg')
                h.startTime = startTime
                h.endTime = endTime
                h.notBefore = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cert.get('notBefore') / 1000))
                h.notAfter = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cert.get('notAfter') / 1000))
                h.status = data.get('status')
                h.statusMessage = data.get('statusMessage')
                h.save()
                print ('Saving Qualys data for '+h.host+' to database')

                if dump_json:
                    with open('%s.json' % data.get('host'), 'wb') as fp:
                        json.dump(data, fp, indent=2, sort_keys=True)


class Command(BaseCommand):
    help = 'Queries the SSL labs API, using database records that are queued'

    def add_arguments(self, parser):
        #parser.add_argument('host', nargs='+')
        parser.add_argument('--no-cache', required=False, action='store_true', dest='no-cache', help='Bypass cache and force re-scan of hostname')
        #parser.add_argument('--show-cn', required=False, action='store_true', dest='show-cn')
        parser.add_argument('--dump-json', required=False, action='store_true', dest='dump-json')

    def handle(self, *args, **options):
        target_hosts = Host.objects.filter(status="QUEUED")

        if not target_hosts:
            print ('Nothing in the queue, exiting')
            return 0

        #Update status of these records to RUNNING to prevent other jobs from picking it up
        
        target_hosts.update(status="RUNNING")

        #Re-grab hosts
        running_hosts = Host.objects.filter(status="RUNNING")
        
        run_mp(running_hosts, not options['no-cache'], options['dump-json'])
        #run_mp(target_hosts, not options['no-cache'], options['dump-json'])
        

