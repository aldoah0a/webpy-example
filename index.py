#!/usr/bin/python

import os
import sys
import web

# force stdout to stderr
sys.stdout = sys.stderr

# Add local directories to the system path
include_dirs = [ 'lib', 'pages' ]
for dirname in include_dirs:
  sys.path.append( os.path.dirname(__file__) + '/' + dirname )

# Change to the directory this file is located in
os.chdir( os.path.dirname(__file__) )

# Turn on/off debugging
web.config.debug = False

# Import our libraries
import sessiondb
import wputil
import wpauth

log = wputil.Log('index')

# Import our html pages
import account
import login

urls = (
  '',          wputil.slashy,
  '/account', account.app_account,
  '/login',   login.app_login,
  '/logout',  'logout',
  '/',        'index'
)

# Create application
app = web.application(urls, locals())

# Start the session and stick it in a database
sdb = sessiondb.SessionDB( app )

# This is required for the sub-apps and templates to access to the shared
# session data
def session_hook():
  web.ctx.session = sdb.get_session()
  web.template.Template.globals['session'] = sdb.get_session()

# This adds the session data as an app processor
app.add_processor( web.loadhook( session_hook ) )

# Set up the templator
htmlout = web.template.render( 'templates/', base='layout' )

# Logs out the user by killing their session
class logout:
  def GET(self, get_string = ''):
    log.loggit( 'logout.GET()' )
    web.ctx.session.kill()
    raise web.seeother('/')

# Delivers the index page
class index:
  def GET(self, get_string = ''):
    log.loggit( 'index.GET()' )
    return htmlout.main()

# Configure HTTP error pages
def unauthorized( message='This page requires proper authorization to view.' ):
  result = { 'title':'401 Authorization Required', 'message':message }
  return web.unauthorized( htmlout.error( result ) )
app.unauthorized = unauthorized

def forbidden( message='Access is forbidden to the requested page.' ):
  result = { 'title':'403 Forbidden', 'message':message }
  return web.forbidden( htmlout.error( result ) )
app.forbidden = forbidden

def notfound( message='The server cannot find the requested page.' ):
  result = { 'title':'404 Not Found', 'message':message }
  return web.notfound( htmlout.error( result ) )
app.notfound = notfound

# This is only needed in the index script
application = app.wsgifunc()

# End
