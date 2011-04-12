#!/usr/bin/python

import os
import sys
import json
import time
import getopt
import oauth2
import random
import string
import urllib
import urllib2
import datetime
import cookielib
import MultipartPostHandler

REST_URL = 'http://localhost/webpy-example/account/rest'

KEY    = 'rGgkUYhqjNEtwZdhnnLZoBkXkdKCPJmI'
SECRET = 'OSdTYJAeQJLLOHlOdmatRvEdBcuxuKGD'

HEADERS = {
  'User-Agent' : 'Python-urllib/2.6 Tony Edition',
  'Accept' : 'application/json'
}

def generate_oauth_request( method, url, parameters={} ):

  # Generate our Consumer object
  consumer = oauth2.Consumer( key = KEY, secret = SECRET )

  # Add parameters required by OAuth
  parameters['oauth_version']      = "1.0"
  parameters['oauth_nonce']        = oauth2.generate_nonce()
  parameters['oauth_timestamp']    = int(time.time())
  parameters['oauth_consumer_key'] = consumer.key

  # Generate and sign the request
  req = oauth2.Request( method = method, url = url, parameters = parameters )
  signature_method = oauth2.SignatureMethod_HMAC_SHA1()
  req.sign_request( signature_method, consumer, None )

  return req

def create_account( account_info ):
  parameters = {
    "username"        : account_info['username'],
    "password"        : account_info['password'],
    "role"            : 'user',
    "last_ip"         : '',
    "last_login"      : '',
    "consumer_key"    : ''.join( random.choice(string.letters) for i in xrange(32) ),
    "consumer_secret" : ''.join( random.choice(string.letters) for i in xrange(32) ),
    "format"          : "json"
  }
  oauth = generate_oauth_request( 'POST', REST_URL, parameters )
  req = urllib2.Request( oauth.to_url(), oauth.to_postdata(), headers=HEADERS )
  result = urllib2.urlopen( req ).read()
  json_result = json.loads( result )
  return json_result

def review_account( username='' ):
  parameters = {
    "username" : username,
    "format"   : "json"
  }
  oauth = generate_oauth_request( 'GET', REST_URL, parameters )
  req = urllib2.Request( oauth.to_url(), headers=HEADERS )
  result = urllib2.urlopen( req ).read()
  json_result = json.loads( result )
  return json_result

def update_account( account_info ):
  parameters = {
    "id"        : account_info['id'],
    "username"  : account_info['username'],
    "password"  : account_info['password'],
    "password2" : account_info['password'],
    "role"       : 'user',
    "last_ip"    : '',
    "last_login" : '',
    "format"    : "json"
  }
  oauth = generate_oauth_request( 'PUT', REST_URL, parameters )
  req = urllib2.Request( oauth.to_url(), oauth.to_postdata(), headers=HEADERS )
  req.get_method = lambda: 'PUT'
  result = urllib2.urlopen( req ).read()
  json_result = json.loads( result )
  return json_result

def delete_account( account_info ):
  parameters = {
    "username" : account_info['username'],
    "format"   : "json"
  }
  oauth = generate_oauth_request( 'DELETE', REST_URL, parameters )
  req = urllib2.Request( oauth.to_url(), headers=HEADERS )
  req.get_method = lambda: 'DELETE'
  result = urllib2.urlopen( req ).read()
  json_result = json.loads( result )
  return json_result

# End
