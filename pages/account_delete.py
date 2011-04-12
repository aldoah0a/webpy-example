#!/usr/bin/python

import os
import sys
import web
import json

from mimerender import mimerender

import wputil
log = wputil.Log('account_delete')
import wpauth
import accountdb

#
# HTML Form definitions start here
#

delete_confirmation_form = web.form.Form(
  web.form.Hidden("username", description="Username"),
  web.form.Button("submit", type="submit", html="Confirm Deletion"),
  web.form.Button("cancel", type="cancel", html="Cancel"),
)

# These are the URLs we watch for. We don't see the prepended /account portion
# in this module because the index.py runs us as a subapplication.
urls = (
  '',      wputil.slashy,
  '/(.*)', 'delete'
)

htmlout = web.template.render( 'templates/', base='layout' )
render_html        = lambda **kwargs: htmlout.account_delete( kwargs )

class delete:
  """
  This class handles the GET and POST methods for the /account/delete URL.
  This class displays the form to confirm deleting and account (GET) and
  then deletes the account from the database (POST).
  """

  @wpauth.session_admin_protect
  @mimerender(
    default = 'html',
    override_input_key = 'format',
    html = render_html
  )
  def GET( self, get_string ):
    log.loggit( 'delete.GET()' )

    # Grab the username from the get string
    username = get_string.lstrip('/')

    if username == 'admin':
      return { 'status' : 'error',
               'message' : 'You cannot delete the administration account.' }

    # Try both account by id and by username
    adb = accountdb.AccountDB();
    account = adb.review_account( username )
    if not account:
      return { 'status' : 'error',
               'message' : 'No such account exists: %s' % ( username ) }

    # Instantiate a form and populate it with the data
    f = delete_confirmation_form()
    f.fill( account )
    return { 'status' : 'success',
             'message' : 'Are you sure you wish to delete the account: %s' % account['username'],
             'form' : f }

  @wpauth.session_admin_protect
  @mimerender(
    default = 'html',
    override_input_key = 'format',
    html = render_html
  )
  def POST( self, get_string ):
    log.loggit( 'delete.POST()' )

    # Catch the cancel button
    if  web.input().has_key('cancel'):
      raise web.seeother('../')

    # Validate the form
    f = delete_confirmation_form()
    if not f.validates():
      return { 'status' : 'error',
               'message' : 'Verify all information has been provided correctly.',
               'form' : f }

    if f.d['username'] == 'admin':
      return { 'status' : 'error',
               'message' : 'You cannot delete the administration account.' }

    # update the account in the database
    adb = accountdb.AccountDB();
    try:
      row = adb.delete_account( f.d['username'] )
    except:
      return { 'status' : 'error',
               'message' : 'An error occurred deleting the account.' }

    raise web.seeother('../')

app_account_delete = web.application( urls, locals() )

# End
