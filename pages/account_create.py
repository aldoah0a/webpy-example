#!/usr/bin/python

import os
import sys
import web
import json
import string
import random

from mimerender import mimerender

import wputil
log = wputil.Log('account_create')
import wpauth
import accountdb

#
# HTML Form definitions start here
#

vpass = web.form.regexp(r".{4,64}$", 'must be between 4 and 64 characters')
account_form = web.form.Form(
  web.form.Textbox('username', web.form.notnull, description='Username'),
  web.form.Password('password', web.form.notnull, vpass, description='Password'),
  web.form.Password('password2', web.form.notnull, description='Repeat password'),
  web.form.Dropdown('role', args=[('user', 'User'), ('administrator', 'Administrator')], value='user'),
  web.form.Button('submit', type='submit', html='Create'),
  web.form.Button('cancel', type='cancel', html='Cancel'),
  validators = [
    web.form.Validator("Passwords do not match.", lambda i: i.password == i.password2)
  ]
)

# These are the URLs we watch for. We don't see the prepended /account portion
# in this module because the index.py runs us as a subapplication.
urls = (
  '',      wputil.slashy,
  '/', 'create'
)

htmlout = web.template.render( 'templates/', base='layout' )
render_html = lambda **kwargs: htmlout.account_create( kwargs )

class create:
  """
  This class handles the GET and POST methods for the /account/create URL.
  This class displays the form for creating accounts (GET) and adds the
  new accounts to the database (POST).
  """

  @wpauth.session_admin_protect
  @mimerender(
    default = 'html',
    override_input_key = 'format',
    html = render_html
  )
  def GET( self ):
    log.loggit( 'create.GET()' )

    # Return the form
    f = account_form()
    return { 'status' : 'success',
             'message' : 'All fields are required - Note that password and password2 must match.',
             'form' : f }

  @wpauth.session_admin_protect
  @mimerender(
    default = 'html',
    override_input_key = 'format',
    html = render_html
  )
  def POST( self ):
    log.loggit( 'create.POST()' )

    # Check to see if we are canceling out
    if web.input().has_key('cancel'):
      raise web.seeother('../')

    # Validate the form and redirect user if needed
    f = account_form()
    if not f.validates():
      return { 'status' : 'error',
               'message' : 'Verify all information has been provided correctly.',
               'form' : f }

    # We can't add to or modify the f.d Storage, so create a new dict to pass
    # to create the account
    acct = {}
    acct['username'] = f.d['username']
    acct['password'] = f.d['password']
    acct['role']     = f.d['role']

    # Adding blank default fields
    acct['last_ip']    = '',
    acct['last_login'] = '',

    # Adding the consumer_key/consumer_secret to support oauth
    acct['consumer_key'] = ''.join( random.choice(string.letters) for i in xrange(32) )
    acct['consumer_secret'] = ''.join( random.choice(string.letters) for i in xrange(32) )

    # Try to write the data to the database
    adb = accountdb.AccountDB();
    try:
      account = adb.create_account( acct )
    except Exception, e:
      return { 'status' : 'error',
               'message' : 'An error occurred: %s' % e,
               'form' : f }

    raise web.seeother( '../review/%s' % (account['username']) )

app_account_create = web.application( urls, locals() )

# End
