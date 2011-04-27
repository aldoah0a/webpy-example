#!/usr/bin/python

import os
import sys
import web

from mimerender import mimerender

import wputil
log = wputil.Log('account')
import wpauth
import accountdb

import account_rest
import account_create
import account_review
import account_update
import account_delete

# These are the URLs we watch for. We don't see the prepended /account portion
# in this module because the index.py runs us as a subapplication.
urls = (
  '',          wputil.slashy,
  '/rest',     account_rest.app_account_rest,
  '/create',   account_create.app_account_create,
  '/review',   account_review.app_account_review,
  '/update',   account_update.app_account_update,
  '/delete',   account_delete.app_account_delete,
  '/',         'default'
)

htmlout = web.template.render( 'templates/', base='layout' )
render_html = lambda **kwargs: htmlout.account( kwargs )

class default:
  """
  This class handles the GET method for the /account/ URL and returns the
  listing of accounts.
  """

  @wpauth.session_admin_protect
  @mimerender(
    default = 'html',
    override_input_key = 'format',
    html = render_html
  )
  def GET( self, get_string='' ):
    log.loggit( 'default.GET()' )

    # Get the accounds and delete the password field
    adb = accountdb.AccountDB()
    accounts = adb.review_accounts()
    for account in accounts:
      account = wputil.clean_account( account )
    return { 'status' : 'success',
             'message' : 'Select the user account to review, update or delete. Click the Add Account link to create a new account.',
             'accounts' : accounts }

app_account = web.application( urls, locals() )

# End
