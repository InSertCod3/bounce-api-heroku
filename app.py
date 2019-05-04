import os
import time
import logging
import datetime

import requests
import atoma
from flask import Flask, request
from flask_restful import Resource, Api

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


app = Flask(__name__)
api = Api(app)
cache = {}

class Service(Resource):
    def get(self, code_id):
        """
        Bounces the information from 9gag rss api to our own,
        with caching.

        Example :: http://127.0.0.1:5000/9GAGComic
        
        Arguments:
            code_id {str} -- Name of the channel
        
        Returns:
            [requests.text] -- Information aqquired from 9gag rss api feed.
        """
        cache_timer = 20 # 20 secs
        # TODO #Feature, Remove the oldest item in cache
        if len(cache.keys()) >= 1:  # do we have anything stored
            if (int(time.time()) - max(cache.keys()) < cache_timer): # (OLD TIME - CACHED TIME) < TIME GAP
                logger.debug('Using Cached Version.')
                return cache[max(cache.keys())]
        params = {'code': code_id, 'format': '1'}
        logger.debug('Getting Fresh Copy.')
        resp = requests.get('https://9gag-rss.com/api/rss/get', params=params)
        feed = atoma.parse_atom_bytes(resp.content)
        cache[int(time.time())] = resp.text
        return resp.text

    def put(self):
        return

api.add_resource(Service, '/<string:code_id>')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))