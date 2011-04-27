#!/usr/bin/python

import os
import sys
import web
import json

from mimerender import mimerender

import wputil
log = wputil.Log('account_rest')
import wpauth
import accountdb

# These are the URLs we watch for. We don't see the prepended /account portion
# in this module because the index.py runs us as a subapplication.
urls = (
  '(.*)',     'default'
)

render_json = lambda **kwargs: json.dumps( kwargs, cls=wputil.CustomEncoder )

class default:
  """
  The REST functions for managing accounts
  """

  @wpauth.oauth_protect
  @mimerender(
    default = 'json',
    override_input_key = 'format',
    json = render_json
  )
  def GET( self, get_string='' ):
    log.loggit( 'default.GET()' )

    # Try to detemine the username from the query
    username = ''
    if web.input().has_key('username'):
      username = web.input()['username']

    adb = accountdb.AccountDB()
    if username:
      account = adb.review_account( username )
      if account:
        return { 'status' : 'success', 'account' : wputil.clean_account( account ) }
      else:
        return { 'status' : 'failure', 'message' : 'No account: %s' % ( username ) }
    else:
      accounts = adb.review_accounts()
      for account in accounts:
        account = wputil.clean_account( account )
      return { 'status' : 'success', 'accounts' : accounts }


  @wpauth.oauth_protect
  @mimerender(
    default = 'json',
    override_input_key = 'format',
    json = render_json
  )
  def POST( self, get_string='' ):
    log.loggit( 'default.POST()' )
    adb = accountdb.AccountDB()
    try:
      account = adb.create_account( web.input() )
    except Exception, e:
      return { 'status' : 'failure', 'message' : '%s %s' % ( repr(e), str(e) ) }
    return { 'status' : 'success', 'account': wputil.clean_account( account ) }


  @wpauth.oauth_protect
  @mimerender(
    default = 'json',
    override_input_key = 'format',
    json = render_json
  )
  def PUT( self, get_string='' ):
    log.loggit( 'default.PUT()' )
    adb = accountdb.AccountDB()
    try:
      account = adb.update_account( web.input() )
    except Exception, e:
      return { 'status' : 'failure', 'message' : '%s %s' % ( repr(e), str(e) ) }
    return { 'status' : 'success', 'account': wputil.clean_account( account ) }


  @wpauth.oauth_protect
  @mimerender(
    default = 'json',
    override_input_key = 'format',
    json = render_json
  )
  def DELETE( self, get_string='' ):
    log.loggit( 'default.DELETE()' )
    if web.input()['username'] == 'admin':
      return { 'status' : 'failure', 'message' : 'Cannot delete the admin account.' }
    adb = accountdb.AccountDB()
    try:
      result = adb.delete_account( web.input()['username'] )
    except Exception, e:
      return { 'status' : 'failure', 'message' : '%s %s' % ( repr(e), str(e) ) }
    return { 'status' : 'success' }


app_account_rest = web.application( urls, locals() )

# End
