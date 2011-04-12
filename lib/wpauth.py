#!/usr/bin/python

import re
import web
import base64
import oauth2
import urllib
import passlib
import accountdb

import wputil
log = wputil.Log('wpauth')

UNAUTHORIZED_MESSAGE = 'You are not authorized to access this content'
UNAUTHORIZED_HEADERS = { 'WWW-Authenticate' : 'Basic realm="Webpy Example"' }

"""
This module provides four different function dectorators to control access.

 o User must be logged in via application using web.py sessions
 o User must be logged and an administrator role in via application using
   web.py sessions
 o HTTP Basic authentication, which pops up a user login box in the browser
 o OAuth authentication (two leg option) using key/secret pairs

The Session logins are mostly for the web-based interface. The OAuth is mostly
for the REST API. HTTP Basic was implemented to restrict access during
development.

The decorators are applied to each GET/POST/PUT/DELETE function requiring
protection. Here is an example:

  import web
  import wpauth

  class protected:

    @wpauth.session_protect
    def GET(self, name=''):
      return '<html><body>You got in!</body></html>'

"""

def session_protect(target):
  """
  This is the decorator to validate a user is logged in
  """
  def decorated_function( *args, **kwargs ):
    log.loggit( 'session_protect.decorated_function()' )
    if not web.ctx.session.has_key('username'):
      raise web.seeother( '/login' + web.ctx.query, absolute=True )
    return target( *args, **kwargs )
  return decorated_function


def session_admin_protect(target):
  """
  This is the decorator to validate a user is an administrator
  """
  def decorated_function( *args, **kwargs ):
    log.loggit( 'session_admin_protect.decorated_function()' )
    if not web.ctx.session.has_key('role') or web.ctx.session['role'] != 'administrator':
      raise web.seeother( '/login' + web.ctx.query, absolute=True )
    return target( *args, **kwargs )
  return decorated_function


def validate_basic_auth():
  """
  Authenticates against the database user accounts using HTTP Basic authentication
  """
  log.loggit( 'validate_basic_auth()' )
  auth_header = web.ctx.env.get('HTTP_AUTHORIZATION')
  username = ""
  password = ""

  if auth_header is None:
    raise web.unauthorized( UNAUTHORIZED_MESSAGE, UNAUTHORIZED_HEADERS )

  elif not auth_header.startswith('Basic '):
    raise web.unauthorized( UNAUTHORIZED_MESSAGE, UNAUTHORIZED_HEADERS )

  else:
    auth = re.sub('^Basic ','',auth_header)
    username, password = base64.decodestring( auth ).split(':')

  adb = accountdb.AccountDB()
  account = adb.login( username, password )
  if account is None:
    raise web.unauthorized( UNAUTHORIZED_MESSAGE, UNAUTHORIZED_HEADERS )

  return True

def basic_protect(target):
  """
  This is the decorator to validate basic authentication
  """
  def decorated_function( *args, **kwargs ):
    log.loggit( 'basic_protect.decorated_function()' )
    validate_basic_auth()
    return target( *args, **kwargs )
  return decorated_function


def split_header( header ):
  """
  Turn Authorization: header into parameters.
  """
  log.loggit( 'split_header()' )
  params = {}
  parts = header.split(',')
  for param in parts:
    # Ignore realm parameter.
    if param.find('realm') > -1:
      continue
    param = param.strip()
    # Split key-value.
    param_parts = param.split('=', 1)
    # Remove quotes and unescape the value.
    params[param_parts[0]] = urllib.unquote(param_parts[1].strip('\"'))
  return params

def validate_two_leg_oauth():
  """
  Verify 2-legged oauth request using values in "Authorization" header.
  """
  log.loggit( 'validate_two_leg_oauth()' )
  parameters = web.input()
  if web.ctx.env.has_key('HTTP_AUTHORIZATION') and web.ctx.env['HTTP_AUTHORIZATION'].startswith('OAuth '):
    parameters.update( split_header( web.ctx.env['HTTP_AUTHORIZATION'] ) )

  # We have to reconstruct the original full URL used when signing
  # so if there are ever 401 errors verifying a request, look here first.
  req = oauth2.Request( web.ctx.env['REQUEST_METHOD'],
                        web.ctx['homedomain'] + web.ctx.env['REQUEST_URI'],
                        parameters = parameters )

  # Verify the account referenced in the request is valid
  adb = accountdb.AccountDB()
  account = adb.review_account_using_info( 'consumer_key', req['oauth_consumer_key'] )
  if not account:
    raise web.unauthorized( UNAUTHORIZED_MESSAGE )

  # Create an oauth2 Consumer with an account's consumer_key and consumer_secret
  # to be used to verify the request
  consumer = oauth2.Consumer( account['consumer_key'], account['consumer_secret'] )

  # Create our oauth2 Server and add hmac-sha1 signature method
  server = oauth2.Server()
  server.add_signature_method( oauth2.SignatureMethod_HMAC_SHA1() )

  # Attempt to verify the authorization request via oauth2
  try:
    server.verify_request( req, consumer, None )
  except oauth2.Error, e:
    log.loggit( 'validate_two_leg_oauth() - %s %s' % ( repr(e), str(e) ) )
    raise web.unauthorized( e )
  except KeyError, e:
    log.loggit( 'validate_two_leg_oauth() - %s %s' % ( repr(e), str(e) ) )
    raise web.unauthorized( "You failed to supply the necessary parameters (%s) to properly authenticate " % e )
  except Exception, e:
    log.loggit( 'validate_two_leg_oauth() - %s %s' % ( repr(e), str(e) ) )
    raise web.unauthorized( repr(e) + ' ' + str(e) )

  return True

def oauth_protect(target):
  """
  This is the decorator to validate oauth authentication
  """
  def decorated_function( *args, **kwargs ):
    log.loggit( 'oauth_protect.decorated_function()' )
    validate_two_leg_oauth()
    return target( *args, **kwargs )
  return decorated_function


# End
