import os
import sys

tplProject = '''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
	<name>%s</name>
	<comment></comment>
	<projects>
	</projects>
	<buildSpec>
		<buildCommand>
			<name>org.eclipse.jdt.core.javabuilder</name>
			<arguments>
			</arguments>
		</buildCommand>
	</buildSpec>
	<natures>
		<nature>org.eclipse.jdt.core.javanature</nature>
	</natures>
</projectDescription>
'''

tplClasspath = '''<?xml version="1.0" encoding="UTF-8"?>
<classpath>
	<classpathentry kind="src" path="src"/>
	<classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER"/>
  %s
	<classpathentry kind="output" path="bin"/>
</classpath>
'''

if __name__ == '__main__':
  prjname = os.path.split(os.path.abspath(os.path.dirname(sys.argv[0]) + '/..'))[-1]
  print('Project name: %s' % prjname)

  internal = len(sys.argv) > 1 and sys.argv[1] == '-i'

  if 'JEB_HOME' not in os.environ:
    print('Set an environment variable JEB_HOME pointing to your JEB folder')
    sys.exit(-1)

  jebhome = os.environ['JEB_HOME']
  jebcorepath = os.path.join(jebhome, 'bin/app/jeb.jar')
  if not os.path.isfile(jebcorepath):
    print('Based on your value of JEB_HOME, jeb.jar was expected at this location, but it was not found: %s' % jebcorepath)
    sys.exit(-1)
  jebdocpath = os.path.join(jebhome, 'doc/apidoc.zip')

  _Project = tplProject % prjname
  with open('.project', 'w') as f:
    f.write(_Project)
  print('Generated: Eclipse .project file')

  jeblibentry = '''<classpathentry kind="lib" path="%s">
    <attributes><attribute name="javadoc_location" value="jar:file:/%s!/reference"/></attributes>
  </classpathentry>''' % (jebcorepath, jebdocpath)
  if internal:
    # FOR INTERNAL USE
    jeblibentry = '<classpathentry combineaccessrules="false" kind="src" path="/jeb3.core"/>'
  _Classpath = tplClasspath % jeblibentry
  with open('.classpath', 'w') as f:
    f.write(_Classpath)
  print('Generated: Eclipse .classpath file')