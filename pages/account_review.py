#!/usr/bin/python

import os
import sys
import web
import json

from mimerender import mimerender

import wputil
log = wputil.Log('account_review')

import accountdb
adb = accountdb.AccountDB()

# These are the URLs we watch for. We don't see the prepended /account portion
# in this module because the index.py runs us as a subapplication.
urls = (
  '',      wputil.slashy,
  '/(.*)', 'review'
)

htmlout = web.template.render( 'templates/', base='layout' )
render_html = lambda **kwargs: htmlout.account_review( kwargs )

class review:
  """
  This class handles the GET method for the /account/review URL.
  This class displays the individual record based upon the URL.
  For example:
    http://xx.xx.xx.xx/account/review/tom <-- look at record with username of tom
  """

  @mimerender(
    default = 'html',
    override_input_key = 'format',
    html = render_html
  )
  def GET( self, get_string ):
    log.loggit( 'review.GET()' )

    # Grab the account username from URL
    username = get_string.lstrip('/')

    # Must be a matching user or administrator to review accounts
    wputil.must_match_username_or_admin( username )

    # Check to see if it exists
    account = adb.review_account( username )
    if not account:
      return { 'status' : 'error',
               'message' : 'No such account exists: %s' % ( username ) }

    print account
    return { 'status' : 'success',
             'message' : 'Review the account information.',
             'account' : wputil.clean_account( account ) }


app_account_review = web.application( urls, locals() )

# End
