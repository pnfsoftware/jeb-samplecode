# -*- coding: utf-8 -*-

#?description=A sample script explictly specifying a UTF-8 encoding
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
"""
Sample script for JEB Decompiler..
"""
class SampleScript(IScript):
  def run(self, ctx):
    # For non-ASCII characters, remember to specify the encoding in the script header (here, UTF-8),
    # and do not forget to prefix all Unicode strings with "u", whether they're encoded (using \u or else) or not
    print('~~~\n' + u'Hello, 안녕하세요, 你好, こんにちは, Здравствуйте!\n' + 'This line was generated by a JEB Python script\n~~~')
