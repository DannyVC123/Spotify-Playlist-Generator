import json
import requests

import uuid
import pathlib
import logging
import sys
import os
import base64
import time

class WebService:
    @staticmethod
    def call(url, action, status_codes=None, headers=None, params=None, data=None):
        # https://developer.spotify.com/documentation/web-api/concepts/api-calls
        # if not status_codes:
            # status_codes = [200, 201, 202, 204, 304, 400, 401, 403, 404]
        # bad_stautus_codes = [429, 500, 502, 503]

        try:
            retries = 0
            
            while True:
                action_cf = action.casefold()
                if action_cf == 'get'.casefold():
                    response = requests.get(url, headers=headers, params=params, data=data)
                elif action_cf == 'put'.casefold():
                    response = requests.put(url, headers=headers, params=params, data=data)
                elif action_cf == 'post'.casefold():
                    response = requests.post(url, headers=headers, params=params, data=data)
                else:
                    raise Exception(f'web_service_{action} does not exist')
                    
                if response.status_code in status_codes:
                    break

                #
                # failed, try again?
                #
                retries = retries + 1
                if retries < 3:
                    # try at most 3 times
                    time.sleep(retries)
                    continue
                    
                #
                # if get here, we tried 3 times, we give up:
                #
                break

            return response

        except Exception as e:
            print('**ERROR**')
            logging.error(f'web_service_{action}() failed:')
            logging.error('url: ' + url)
            logging.error(e)
            return None