package com.pnf.andhook;

import java.util.Map;

import javax.crypto.Cipher;

import com.pnfsoftware.jeb.core.AbstractEnginesPlugin;
import com.pnfsoftware.jeb.core.IEnginesContext;
import com.pnfsoftware.jeb.core.IPluginInformation;
import com.pnfsoftware.jeb.core.IRuntimeProject;
import com.pnfsoftware.jeb.core.PluginInformation;
import com.pnfsoftware.jeb.core.RuntimeProjectUtil;
import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.core.units.code.android.IDexUnit;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerUnit;
import com.pnfsoftware.jeb.core.util.DebuggerHelper;
import com.pnfsoftware.jeb.util.CollectionUtil;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * This plugin uses the JEB debugger API to monitor the use of cryptographic primitives in a running
 * Android application, specifically the methods in the {@link Cipher} abstract class. This plugin
 * is intended as proof-of-concept code show-casing what can be done with the {@link IDebuggerUnit}
 * et al. set of interfaces.
 * <p>
 * Note that this plugin can be used with any client, such as the official UI RCP client, or a
 * headless client.
 * <p>
 * How to use as a stand-alone Jar plugin:
 * <ul>
 * <li>Navigate to the build/ folder</li>
 * <li>Build the plugin using Ant:
 * <code>ant -file build-andhook.xml -Dversion=1.0.0 clean build package</code></li>
 * <li>Copy to your JEB coreplugins/ folder and start JEB</li>
 * </ul>
 * <p>
 * How to use in a development environment, via the RCP desktop client:
 * <ul>
 * <li>Set the plugin's *.class files folder and class name in the Development tab of the Options
 * dialog</li>
 * <li>(Instructions here: <a
 * href="https://www.pnfsoftware.com/viewdoc?doc=jeb2-tutorial-plugin-1">JEB Dev Tutorial Part 1)</a>
 * </li>
 * <li>Restart JEB</a>
 * </ul>
 * <p>
 * Then: open an APK; start a debugging session; run the plugin (eg, in UI: File, Engines menu.)
 * 
 * @author Nicolas Falliere
 *
 */
public class AndroidCryptoHookPlugin extends AbstractEnginesPlugin {
    private static final ILogger logger = GlobalLog.getLogger(AndroidCryptoHookPlugin.class);

    @Override
    public IPluginInformation getPluginInformation() {
        return new PluginInformation("Android Crypto-Hook Plugin",
                "Hook cryptographic primitives during an Android app debugging sesssion", "PNF Software",
                Version.create(1, 0));
    }

    private AndroidCryptoHook manager;

    @Override
    public void execute(IEnginesContext engctx, Map<String, String> executionOptions) {
        IRuntimeProject prj = engctx.getProject(0);
        if(prj == null) {
            logger.warn("No project found");
            return;
        }

        IDexUnit dex = CollectionUtil.getFirst(RuntimeProjectUtil.findUnitsByType(prj, IDexUnit.class, false));
        if(dex == null) {
            logger.warn("No DEX unit found");
            return;
        }

        IDebuggerUnit dbg = DebuggerHelper.getDebuggerForUnit(prj, dex);
        if(dbg == null) {
            logger.warn("No debugger found for DEX file");
            return;
        }

        if(!dbg.isAttached()) {
            logger.warn("The debugger is not attached");
            return;
        }

        if(manager == null) {
            logger.info("Hooking cryptographic primitives...");
            manager = new AndroidCryptoHook(dex, dbg);
            manager.start();
        }
        else {
            logger.info("Un-hooking cryptographic primitives...");
            manager.stop();
        }
    }
}
