package com.pnf.plugintest;

import java.util.List;
import java.util.Map;

import com.pnfsoftware.jeb.core.IEnginesContext;
import com.pnfsoftware.jeb.core.IEnginesPlugin;
import com.pnfsoftware.jeb.core.IOptionDefinition;
import com.pnfsoftware.jeb.core.IPluginInformation;
import com.pnfsoftware.jeb.core.PluginInformation;
import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Sample plugin.
 * 
 * @author Nicolas Falliere
 */
public class SampleEnginesPlugin implements IEnginesPlugin {
    private static final ILogger logger = GlobalLog.getLogger(SampleEnginesPlugin.class);

    @Override
    public IPluginInformation getPluginInformation() {
        return new PluginInformation("Sample Plugin", "A sample JEB2 plugin", "PNF Software", Version.create(1, 0));
    }

    @Override
    public List<? extends IOptionDefinition> getExecutionOptionDefinitions() {
        return null;
    }

    @Override
    public void execute(IEnginesContext context) {
        execute(context, null);
    }

    @Override
    public void execute(IEnginesContext engctx, Map<String, String> executionOptions) {
        logger.info("Executing sample plugin");
    }

    @Override
    public void dispose() {
    }
}
