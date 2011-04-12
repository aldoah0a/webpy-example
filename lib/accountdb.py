#!/usr/bin/python

import os
import sys
import web

from credentials import Credentials

from passlib.apps import custom_app_context as pwd_context

import wputil

log = wputil.Log('accountdb')

INFO_BLACKLIST = [ 'username', 'password', 'password2', 'submit', 'cancel',
                   'oauth_body_hash', 'oauth_nonce', 'oauth_timestamp',
                   'oauth_consumer_key', 'oauth_signature_method', 'oauth_version',
                   'oauth_signature' ]

class AccountDB(object):
  """
  AccountDB() - abstracts the database access away for accounts
  """

  def __init__( self ):
    """
    The database credentials are stored in the Credentials class which is generated
    by the dbconfig-common package via debconf.
    """
    log.loggit( 'AccountDB()' )
    self.db = web.database(
      dbn  = 'postgres',
      db   = Credentials.dbdefault,
      user = Credentials.dbuser,
      pw   = Credentials.dbpassword
    )

  def _set_account_info( self, account, data ):
    """
    @param acct is a result from the database
    @returns a dict of the account with its associated info
    """
    log.loggit( 'AccountDB._set_account_info()' )
    for key,val in data.iteritems():
      if key not in INFO_BLACKLIST:
        account[key] = val
        info = { 'username': account['username'],
                 'key': key,
                 'value': val }
        tmp_id = self.db.insert( 'account_info', **info )
    return account

  def _get_account_info( self, account ):
    """
    @param acct is a result from the database
    @returns a dict of the account with its associated info
    """
    log.loggit( 'AccountDB._get_account_info()' )
    res = self.db.select(
      'account_info',
      where = 'username = $username',
      vars = dict( username = account['username'] )
    )
    for info in res:
      account[ info['key'] ] = info['value']
    return account

  def create_account( self, data ):
    """
    @param data is a Storage (or Dict)
    """
    log.loggit( 'AccountDB.create_account()' )
    account = {}
    account['username'] = data['username']
    account['password'] = pwd_context.encrypt( data['password'] )
    account['id'] = self.db.insert( 'accounts', **account )
    return self._set_account_info( account, data )

  def review_accounts( self ):
    """
    @returns a list of Storage elements from the database
    """
    log.loggit( 'AccountDB.review_accounts()' )
    res = self.db.select( 'accounts', order = 'id ASC' )
    accounts = []
    for a in res:
      accounts.append( self._get_account_info( a ) )
    return accounts

  def review_account( self, username ):
    """
    @param username is the username of the account
    @returns a single record from the database as a Storage object
    """
    log.loggit( 'AccountDB.review_account()' )
    res = self.db.select(
      'accounts',
      where = 'username = $username',
      limit = 1,
      vars = dict( username = username )
    )
    if not res:
      return False
    return self._get_account_info( res[0] )


  def review_account_using_info( self, key, value ):
    """
    @param key is the content in an account_info 'key' string
    @param value is the content in an account_info 'value' string
    @returns a single record from the database as a Storage object
    """
    res = self.db.select(
      'accounts',
      where = 'username = ( select username from account_info where key=$key and value=$value )',
      limit = 1,
      vars = dict( key = key, value = value )
    )
    if not res:
      return False
    return self._get_account_info( res[0] )


  def update_account( self, data ):
    """
    @param data is a Storage (or Dict)
    """
    log.loggit( 'AccountDB.set_account()' )
    account = {}
    account['id'] = data['id']
    account['username'] = data['username']
    # Leave password alone if it is not set from the form
    if data['password']:
      account['password'] = pwd_context.encrypt( data['password'] )
    result = self.db.update( 'accounts', where='id = $id', vars = dict( id = account['id'] ), **account )
    return self._set_account_info( account, data )

  
  def delete_account( self, username ):
    """
    @param account_id is the record id of the account to be deleted
    """
    log.loggit( 'AccountDB.delete_account()' )
    result = self.db.delete('account_info', where='username = $username', vars = dict( username = username ) )
    result = self.db.delete('accounts', where='username = $username', vars = dict( username = username ) )
    return True


  def login( self, username, password ):
    """
    @param username is the username of an account
    @param password is the password of an account
    @returns a single record from the database as a Storage object
    """
    log.loggit( 'AccountDB.login()' )
    acct = self.review_account( username )
    if not acct:
      return False
    if not pwd_context.verify( password, acct['password'] ):
      return False
    return acct

# End
