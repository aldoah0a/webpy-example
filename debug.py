#!/usr/bin/python

# Note! This file can be run in place of the index.py to review the
# HTTP headers and content being sent from a web client. Very useful
# for debugging android phone issues.

import os
import sys
import cStringIO

def application(environ, start_response):
  headers = []
  headers.append(('Content-Type', 'text/plain'))
  write = start_response('200 OK', headers)

  input = environ['wsgi.input']
  output = cStringIO.StringIO()

  print >> output, "PID: %s" % os.getpid()
  print >> output, "UID: %s" % os.getuid()
  print >> output, "GID: %s" % os.getgid()
  print >> output

  keys = environ.keys()
  keys.sort()
  for key in keys:
      print >> output, '%s: %s' % (key, repr(environ[key]))
  print >> output

  output.write(input.read(int(environ.get('CONTENT_LENGTH', '0'))))

  fh = open( '/tmp/wsgi.debug', 'a' )
  fh.write( 'XXX\n%s\n\n' % output.getvalue() )
  fh.close()

  #return [output.getvalue()]
  return '{ "status": "success", "message": "Running in debug mode" }'

