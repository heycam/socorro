#!/usr/bin/python

#
# A mod_python environment for the crash report collector
#

import collect
import config
import sys

if __name__ != "__main__":
  from mod_python import apache
  from mod_python import util
else:
  # this is a test being run from the command line
  # these objects are to provide a fake environment for testing
  from modpython_testhelper import apache
  from modpython_testhelper import util

def handler(req):
  if req.method == "POST":
    try:
      theform = util.FieldStorage(req)
      dump = theform[config.dumpField]
      if not dump.file:
        return apache.HTTP_BAD_REQUEST

      jsonData = collect.createJSON(theform)
      if collect.throttle(jsonData):
        storageRoot = config.deferredStorageRoot
        useIndexSubdirectories = True
      else:
        storageRoot = config.storageRoot
        useIndexSubdirectories = False

      (dumpID, dumpPath, dateString) = collect.storeDump(dump.file, storageRoot)
      collect.storeJSON(dumpID, dumpPath, jsonData, storageRoot, useIndexSubdirectories)
      req.content_type = "text/plain"
      req.write(collect.makeResponseForClient(dumpID, dateString))
    except:
      print >>sys.stderr, "Exception: %s" % sys.exc_info()[0]
      print >>sys.stderr, sys.exc_info()[1]
      print >>sys.stderr
      sys.stderr.flush()
      return apache.HTTP_INTERNAL_SERVER_ERROR
    return apache.OK
  else:
    return apache.HTTP_METHOD_NOT_ALLOWED


if __name__ == "__main__":
  from modpython_testhelper import *

  req = FakeReq()
  req.method = "POST"
  req.fields = {
    "StartupTime": "1206120381",
    "Vendor": "Mozilla",
    "InstallTime": "1204828702",
    "timestamp": "1206206829.56",
    "Add-ons": "{19503e42-ca3c-4c27-b1e2-9cdb2170ee34}:0.8.3,inspector@mozilla.org:1.9b4pre,{972ce4c6-7e08-4474-a285-3208198ce6fd}:2.0",
    "BuildID": "2008022517",
    "SecondsSinceLastCrash": "63935",
    "UserID": "d6d2b6b0-c9e0-4646-8627-0b1bdd4a92bb",
    "ProductName": "Firefox",
    "URL": "http:\/\/www.google.com.ar\/search?hl=es&defl=es&q=define:ARN&sa=X&oi=glossary_definition&ct=title",
    "Theme": "classic\/1.0",
    "Version": "3.0b4pre",
    "CrashTime": "1206120413",
    "upload_file_minidump":FakeDump(FakeFile("this is a dump"))
  }

  print handler(req)
