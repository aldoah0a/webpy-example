#!/usr/bin/python

import os
import sys
import web
from credentials import Credentials

import wputil
log = wputil.Log('sessiondb')

SESSION_DB = 'sessions'

class SessionDB(object):
  """
  SessionDB() - abstracts the database access away for accounts
  """

  def __init__( self, app ):
    """
    The database credentials are stored in the Credentials class which is generated
    by the dbconfig-common package via debconf.
    """
    log.loggit( 'SessionDB()' )
    self.app = app
    self.db = web.database(
      dbn  = 'postgres',
      db   = Credentials.dbdefault,
      user = Credentials.dbuser,
      pw   = Credentials.dbpassword
    )
    self.store   = web.session.DBStore( self.db, SESSION_DB )
    self.session = web.session.Session( self.app, self.store )

  def get_session( self ):
    """
    @returns the session
    """
    log.loggit( 'SessionDB.get_session()' )
    return self.session

# End
