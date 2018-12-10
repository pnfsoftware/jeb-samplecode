#!/usr/bin/env python3

'''
Python API wrapper to query the "JEB Malware Sharing Network".
What is it? Go read https://www.pnfsoftware.com/blog/introducing-the-jeb-malware-sharing-network/

Operations supported: check a file hash, upload a file, download a file.
This file can be used as a library or as a stand-alone script. In the latter case,
make sure to update the APIKEY global variable or set up a JEBIO_APIKEY environment variable.

Dependency: requests ('pip install requests' if you don't have it)

Version 1 - Oct 12 2017 (Nicolas Falliere)
'''
import getopt
import json
import os
import re
import requests
import sys
import traceback

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

def download(h, outpath=None, apikey='', extract=False):
  if not h:
    raise 'A hash must be provided'
  url = '%s/file/download?apikey=%s&h=%s' % (BASE, getApikey(apikey), h)
  r = requests.get(url)
  if not r or not r.ok or not r.content:
    return None
  if not outpath:
    try:
      outpath = re.findall('filename=(\S+)', r.headers.get('content-disposition'))[0]
    except Exception as e:
      pass
  if not outpath:
    outpath = h + '.zip'
  with open(outpath, 'wb') as f:
    f.write(r.content)
  if extract:
    from zipfile import ZipFile
    with ZipFile(outpath) as zipfile:
      zipfile.extractall(pwd=b'infected')
      outpath2 = zipfile.namelist()[0]
    os.unlink(outpath)
    outpath = outpath2
  return outpath

def upload(filepath, apikey=''):  
  url = '%s/file/upload?apikey=%s' % (BASE, getApikey(apikey))
  files = {'ufile': open(filepath, 'rb')}
  r = requests.post(url, files=files)
  return r.json()

def usage():
  p = os.path.split(sys.argv[0])[-1]
  print('JEB.IO/"Malware Sharing Network" back-end API wrapper (c) PNF Software, 2017-2018.')
  print('This file can be used as a library or as a stand-alone script to check file hashes as well as download and upload files.')
  print('Usage:')
  print('  %s mode options' % p)
  print('  where mode is one of \'check\', \'download\', or \'upload\'')
  print('Details:')
  print('  %s (check|download|upload) [-d] <filehash|filepath>' % p)
  print('  %s (check|download) [-d] -f <file.txt>' % p)
  print('Options:')
  print('  -v  : extra verbose')
  print('  -x  : extract downloaded files (only in \'download\' mode')
  print('Example:')
  print('  %s check 42aaa93a894a69bfcbc21823b09e4ea9f723c428' % p)
  sys.exit(-1)

if __name__ == '__main__':
  if len(sys.argv) <= 1:
    usage()
    sys.exit()

  # retrieve the mode
  action = sys.argv[1].lower()

  try:
    opts, args = getopt.getopt(sys.argv[2:], 'vxf:')
  except getopt.GetoptError as err:
    usage()

  verbose = False
  extract = False
  hlist = []
  for o, a in opts:
    if o == '-v':
      verbose = True
    elif o == '-x':
      extract = True
    elif o == '-f':
      with open(a) as f:
        for line in f.readlines():
          line = line.strip()
          if line and not line.startswith('#'):
            hlist.append(line)
    else:
      usage()

  hlist.extend(args)
  hlist = list(set(hlist))

  if verbose:
    print('Mode: %s' % action)
    print('  (extract=%s)' % extract)
    print('Processing %d entries' % len(hlist))

  if action == 'check':
    for h in hlist:
      try:
        print('%s: %s' % (h, json.dumps(check(h), indent=4, sort_keys=True)))
      except Exception as e:
        traceback.print_exc()
  elif action == 'download':
    for h in hlist:
      try:
        outpath = download(h, extract=extract)
        if outpath:
          if extract:
            print('%s: downloaded to %s' % (h, outpath))
          else:
            print('%s: downloaded to %s (password: "infected")' % (h, outpath))
        else:
          print('%s: NOT found' % h)
      except Exception as e:
        traceback.print_exc()
  elif action == 'upload':
    for filepath in hlist:
      try:
        print('%s: %s' % (filepath, json.dumps(upload(filepath), indent=4, sort_keys=True)))
      except Exception as e:
        traceback.print_exc()
  else:
    usage()
