//?type=engines

import java.util.Map;

import com.pnfsoftware.jeb.core.AbstractEnginesPlugin;
import com.pnfsoftware.jeb.core.IEnginesContext;
import com.pnfsoftware.jeb.core.IOptionDefinition;
import com.pnfsoftware.jeb.core.IPluginInformation;
import com.pnfsoftware.jeb.core.PluginInformation;
import com.pnfsoftware.jeb.core.Version;

/**
 * Sample JEB Engines Plugin. It may be compiled and dropped in coreplugins/, or it may
 * be kept as a script plugin in coreplugins/scripts/.
 * <p>
 * Script plugins can be developed and modified while JEB is running.
 * Please refer to the javadoc of the IEnginesPlugin interface for additional information.
 *
 * @author Nicolas Falliere
 *
 */
public class EngSampleJava extends AbstractEnginesPlugin {

    @Override
    public IPluginInformation getPluginInformation() {
        return new PluginInformation("Sample engines plugin", "", "PNF Software", Version.create(0, 1));
    }

    @Override
    public void load(IEnginesContext context) {
        logger.debug("Sample engines plugin: load()");
    }

    @Override
    public void execute(IEnginesContext engctx, Map<String, String> executionOptions) {
        logger.debug("Sample engines plugin: execute()");
    }
}