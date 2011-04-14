#!/usr/bin/python

import os
import sys
import web
import json

from mimerender import mimerender

import wputil
log = wputil.Log('account_update')
import wpauth
import accountdb

#
# HTML Form definitions start here
#

vpass = web.form.regexp(r".{4,64}$", 'must be between 4 and 64 characters')
account_form = web.form.Form(
  web.form.Hidden('id', description='Id'),
  web.form.Textbox('username', web.form.notnull, description='Username'),
  web.form.Password('password', web.form.notnull, vpass, description='Password'),
  web.form.Password('password2', web.form.notnull, description='Repeat password'),
  web.form.Button('submit', type='submit', html='Update'),
  web.form.Button('cancel', type='cancel', html='Cancel'),
  validators = [
    web.form.Validator("Passwords do not match.", lambda i: i.password == i.password2)
  ]
)

admin_account_form = web.form.Form(
  web.form.Hidden('id', description='Id'),
  web.form.Textbox('username', web.form.notnull, description='Username'),
  web.form.Password('password', description='Password'),
  web.form.Password('password2', description='Repeat password'),
  web.form.Dropdown('role', args=[('user', 'User'), ('administrator', 'Administrator')], value='user'),
  web.form.Button('submit', type='submit', html='Update'),
  web.form.Button('cancel', type='cancel', html='Cancel'),
  validators = [
    web.form.Validator("Passwords do not match.", lambda i: i.password == i.password2)
  ]
)

# These are the URLs we watch for. We don't see the prepended /account portion
# in this module because the index.py runs us as a subapplication.
urls = (
  '',      wputil.slashy,
  '/(.*)', 'update'
)

htmlout = web.template.render( 'templates/', base='layout' )
render_html = lambda **kwargs: htmlout.account_update( kwargs )

class update:
  """
  This class handles the GET and POST methods for the /account/update URL.
  This class displays the form for updating accounts (GET) and updates the
  account to the database (POST).
  """

  @mimerender(
    default = 'html',
    override_input_key = 'format',
    html = render_html
  )
  def GET( self, get_string ):
    log.loggit( 'update.GET()' )

    # Grab the account id from the get string
    username = get_string.lstrip('/')
    if not username:
      raise web.seeother('../')

    # Must be a matching user or administrator to review accounts
    wputil.must_match_username_or_admin( username )

    # Verify account exists
    adb = accountdb.AccountDB()
    account = adb.review_account( username )
    if not account:
      return { 'status' : 'error',
               'message' : 'No such account exists: %s' % ( username ) }

    # Instantiate a form and populate it with the data
    if wputil.is_admin():
      f = admin_account_form()
    else:
      f = account_form()
    f.fill( wputil.clean_account( account ) )
    return { 'status' : 'success',
             'message' : 'Required fields include: id, username, password, password2 - Note that password and password2 must match.',
             'form' : f }

  @mimerender(
    default = 'html',
    override_input_key = 'format',
    html = render_html
  )
  def POST( self, get_string ):
    log.loggit( 'update.POST()' )

    # Must be a matching user or administrator to update
    wputil.must_match_username_or_admin( web.input()['username'] )

    # Catch the cancel button
    if  web.input().has_key('cancel'):
      if wputil.is_admin():
        raise web.seeother('../')
      else:
        raise web.seeother('../../')

    # Validate the form
    if wputil.is_admin():
      f = admin_account_form()
    else:
      f = account_form()
    if not f.validates():
      return { 'status' : 'error',
               'message' : 'Verify all information has been provided correctly.',
               'form' : f }

    # update the account in the database
    adb = accountdb.AccountDB()
    try:
      account = adb.update_account( f.d )
    except:
      return { 'status' : 'error',
               'message' : 'An error occurred updating the account.',
               'form' : f }

    raise web.seeother( '../review/%s' % (account['username']) )

app_account_update = web.application( urls, locals() )

# End
