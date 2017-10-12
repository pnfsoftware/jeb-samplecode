'''
Python API wrapper to query the "JEB Malware Sharing Network".
What is it? Go read https://www.pnfsoftware.com/blog/introducing-the-jeb-malware-sharing-network/

Operations supported: check a file hash, upload a file, download a file.
This file can be used as a library or as a stand-alone script. In the latter case,
make sure to update the APIKEY global variable or set up a JEBIO_AIKEY environment variable.

Dependency: requests ('pip install requests' if you don't have it)

Version 1 - Oct 12 2017 (Nicolas Falliere)
'''
import json
import os
import re
import requests
import sys

#------------------------------------------------------------------------------
#        1) update this global
#     or 2) set up a JEBIO_APIKEY environment variable
# and/or 3) use as a library and provide the `apikey` parameter
APIKEY = ''
#------------------------------------------------------------------------------

BASE = 'https://www.pnfsoftware.com/io/api'

def getApikey(apikey):
  if apikey:
    return apikey
  if 'JEBIO_APIKEY' in os.environ:
    return os.environ['JEBIO_APIKEY']
  if APIKEY:
    return APIKEY
  raise 'Your need a JEB.IO API key to execute this command.'

def check(h, apikey=''):
  url = '%s/file/check?apikey=%s&h=%s' % (BASE, getApikey(apikey), h)
  r = requests.get(url)  
  return r.json()

def download(h, outpath=None, apikey=''):
  url = '%s/file/download?apikey=%s&h=%s' % (BASE, getApikey(apikey), h)
  r = requests.get(url)
  if not r.ok:
    return None
  if not outpath:
    outpath = re.findall('filename=(\S+)', r.headers.get('content-disposition'))[0]
  with open(outpath, 'wb') as f:
    f.write(r.content)
  #if extract:  
  #  from zipfile import ZipFile
  #  zipfile = ZipFile(outputname)
  #  zipfile.extractall(pwd='infected')
  return outpath

def upload(filepath, apikey=''):  
  url = '%s/file/upload?apikey=%s' % (BASE, getApikey(apikey))
  files = {'ufile': open(filepath, 'rb')}
  r = requests.post(url, files=files)
  return r.json()

def usage():
  print('JEB.IO/"Malware Sharing Network" back-end API wrapper (c) PNF Software, 2017.')
  print('This file can be used as a library or as a stand-alone script to check file hashes as well as download and upload files.')
  print('Usage:')
  print('  %s [check|download|upload] <filehash|filepath>' % os.path.split(sys.argv[0])[-1])
  print('Example:')
  print('  %s check 42aaa93a894a69bfcbc21823b09e4ea9f723c428' % os.path.split(sys.argv[0])[-1])
  sys.exit(-1)

if __name__ == '__main__':
  if len(sys.argv) <= 1:
    usage()
    sys.exit()

  action = sys.argv[1].lower()
  if action == 'check':
    for h in sys.argv[2:]:
      try:
        print('%s: %s' % (h, json.dumps(check(h), indent=4, sort_keys=True)))
      except Exception as e:
        print('ERROR:', e)
  elif action == 'download':
    for h in sys.argv[2:]:
      try:
        outpath = download(h)
        print('%s: downloaded to %s (password: "infected")' % (h, outpath))
      except Exception as e:
        print('ERROR:', e)
  elif action == 'upload':
    for filepath in sys.argv[2:]:
      try:
        print('%s: %s' % (filepath, json.dumps(upload(filepath), indent=4, sort_keys=True)))
      except Exception as e:
        print('ERROR:', e)
  else:
    usage()
