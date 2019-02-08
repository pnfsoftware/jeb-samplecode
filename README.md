# Sample extensions (Python scripts & Java plugins) for [JEB Decompiler](https://www.pnfsoftware.com).

## JEB Script Development Recommendations

JEB Client extensions (*scripts*) should be written in Python. (We may add support for scripts written in Java in the future.)

If you are using Sublime Text 3, we published a ST3 extension to make JEB script writing easier.
Install the `jeb_scriptdev_helper` package using PackageControl or by cloning [that repository](https://github.com/pnfsoftware/jeb_scriptdev_helper) into your Sublime's 'Packages' folder:

- OS X: ~/Library/Application Support/Sublime Text 3/Packages/
- Windows: %APPDATA%/Roaming/Sublime Text 3/Packages/
- Linux: ~/.config/sublime-text-3/Packages/

## Plugin Development Recommendations

JEB Back-end extensions (*plugins*) should be written in Java. (Some classes of back-end plugins may be written in Python.)

We recommend using Eclipse IDE, although you may use any code editor. If you are using Eclipse, clone [that repository](https://github.com/pnfsoftware/jeb-template-plugin) and follow the README instructions to create an empty plugin skeleton with tester code as well as the accompanying project (to be imported in Eclipse) with integrated JEB API documentation.

## Resources

- [Developer Portal](https://www.pnfsoftware.com/jeb/devportal)
- [API Reference](https://www.pnfsoftware.com/jeb/apidoc)
