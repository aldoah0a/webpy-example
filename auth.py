#!/usr/bin/python

# Note: This is *NOT* a part of the web.py infrastructure. It supports
# an implementation of HTTP Auth that the mod_wsgi provides support for.
#
# See the configuration file for apache in postinstall/webpy-config for
# more information on how this might be used

from hashlib import md5

def check_password( environ, user, password ):
  """
  check_password() is called by Apache when it needs to validate a
  user account during an HTTP Basic authentication process

  Requires the following line in the Apache site configurtation:

  WSGIAuthUserScript /path/to/auth.py

  """
  if user == 'user':
    if password == 'user':
      return True
    return False
  return None

def get_realm_hash( environ, user, realm ):
  """
  get_realm_hash() is called by Apache when it needs to generate a
  a password during an HTTP Digest authentication process

  Requires the following line in the Apache site configurtation:

  WSGIAuthUserScript /path/to/auth.py

  """
  if user == 'user':
    value = md5.new()
    # user:realm:password
    value.update( 's:%s:%s' % ( user, realm, 'user' ) )
    hash = value.hexdigest()
    return hash
  return None

def groups_for_user( environ, user ):
  """
  groups_for_user() is called by Apache to verify if a given user is a
  member of a paricular group during an HTTP authentication process

  Requires the following line in the Apache site configurtation:

  WSGIAuthUserScript /path/to/auth.py

  """
  if user == 'user':
    return ['mygroup']
  return ['']

def allow_access( environ, host ):
  """
  allow_access() is called by Apache when evaluating if a host should be
  allowed access. The IP address should be present in the list to allow
  access.

  Requires the following line in the Apache site configurtation:

  WSGIAccessScript /path/to/auth.py

  """
  return host in [ '127.0.0.1', '::1', '66.192.110.63' ]

# End
