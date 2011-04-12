#!/usr/bin/python

import web
import json

class Log:
  """
  This class provides a simple logging function
  """
  def __init__( self, module ):
    """
    Pass the name of the module to include in the log entry
    """
    self.module = module
    self.verbose = True

  def loggit( self, message ):
    """
    To suppress logging for this module, comment out the web.debug and put in a
    pass statement
    """
    if self.verbose:
      web.debug( "%s.%s" % ( self.module, message ) )

log = Log('wputil')


def must_match_username_or_admin( username, redirect='../' ):
  """
  Runs at the top of any page that requires a specific user or administrator role
  """
  log.loggit( 'must_match_username_or_admin()' )
  if not ( matches_username( username ) or is_admin() ):
    raise web.seeother( redirect )


def is_logged_in():
  """
  Test to see if the user is logged in.
  """
  log.loggit( 'is_logged_in()' )
  if web.ctx.session.has_key('username'):
    return True
  return False


def is_admin():
  """
  Test to see if the user is logged in as an administrator.
  """
  log.loggit( 'is_admin()' )
  if web.ctx.session.has_key('role') and web.ctx.session['role'] == 'administrator':
    return True
  return False


def matches_username( username ):
  """
  Test to see if the logged in username matches the supplied username
  """
  log.loggit( 'matches_username()' )
  if web.ctx.session.has_key('username') and web.ctx.session['username'] == username:
    return True
  return False
  

def clean_account( account ):
  """
  Common function to remove confidential fields from the account dict
  """
  log.loggit( 'clean_account()' )
  if not isinstance(account, dict):
    return account
  if account.has_key('password'):
    del account['password']
  if account.has_key('consumer_key'):
    del account['consumer_key']
  if account.has_key('consumer_secret'):
    del account['consumer_secret']
  return account


def fix_broken_browsers():
  """
  WebKit based browsers send the Accept header with a preference for XML over
  HTML for some stupid reason and as a result, we need to force html unless
  they change the 'format' parameter
  """
  if web.ctx.env['HTTP_USER_AGENT'].find('WebKit') > -1 and not web.input().has_key('format'):
    log.loggit( 'fix_broken_browsers() - Redirecting WebKit to force format' )
    raise web.seeother('?format=html')


class CustomEncoder(json.JSONEncoder):
  """
  This class allows us to filter our the non-JSON serializable types
  """
  def default(self, obj):
    if isinstance(obj, web.utils.Storage):
      return [ 'Unserializable web storage' ]
    if isinstance(obj, web.form.Form):
      return [ 'Unserializable web form' ]
    return json.JSONEncoder.default(self, obj)


class slashy:
  """
  This function sticks a slash character on the end of the URL
  """
  def GET(self):
    log.loggit( 'slashy.GET()' )
    raise web.seeother( '/' + web.ctx.query )

# End
