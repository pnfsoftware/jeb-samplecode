package com.pnf.pommePlugin;

import java.util.List;
import java.util.Map;

import com.pnfsoftware.jeb.core.IEnginesContext;
import com.pnfsoftware.jeb.core.IEnginesPlugin;
import com.pnfsoftware.jeb.core.IOptionDefinition;
import com.pnfsoftware.jeb.core.IPluginInformation;
import com.pnfsoftware.jeb.core.IRuntimeProject;
import com.pnfsoftware.jeb.core.PluginInformation;
import com.pnfsoftware.jeb.core.RuntimeProjectUtil;
import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.core.units.INativeCodeUnit;
import com.pnfsoftware.jeb.core.units.code.ICodeUnit;
import com.pnfsoftware.jeb.core.units.code.IInstruction;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;


public class PommePlugin implements IEnginesPlugin {

	private static final ILogger logger = GlobalLog.getLogger(PommePlugin.class);

    @Override
    public IPluginInformation getPluginInformation() {
    	
        return new PluginInformation("Pomme Plugin", "Finds API usage in multiple files.", "PNF Software", Version.create(0, 1));
    }

	@Override
	public void dispose() {
        logger.info("Dispose");
	}

	@Override
	public void execute(IEnginesContext engctx) {

        execute(engctx, null);

	}

	public void execute(IEnginesContext engctx, Map<String, String> arg1) {

        List<IRuntimeProject> projects = engctx.getProjects();
        if (projects == null){
            logger.info("There is no opened project");
            return;

        }
        IRuntimeProject prj = projects.get(0);
        logger.info("Decompiling code units of %s", prj.toString());

        List<ICodeUnit> codeUnits = RuntimeProjectUtil.findUnitsByType(prj, ICodeUnit.class, false);

        if (codeUnits == null) {

            logger.warn("No code units found.");

        }
        
        new PommeTask(codeUnits);

        logger.info("Done.");

    }

	public List<? extends IOptionDefinition> getExecutionOptionDefinitions() {
		return null;
	}
}