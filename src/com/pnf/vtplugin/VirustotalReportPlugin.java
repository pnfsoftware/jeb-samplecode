package com.pnf.vtplugin;

import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import com.pnfsoftware.jeb.core.AbstractEnginesPlugin;
import com.pnfsoftware.jeb.core.IArtifact;
import com.pnfsoftware.jeb.core.IEnginesContext;
import com.pnfsoftware.jeb.core.ILiveArtifact;
import com.pnfsoftware.jeb.core.IOptionDefinition;
import com.pnfsoftware.jeb.core.IPluginInformation;
import com.pnfsoftware.jeb.core.IRuntimeProject;
import com.pnfsoftware.jeb.core.OptionDefinition;
import com.pnfsoftware.jeb.core.PluginInformation;
import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.core.events.J;
import com.pnfsoftware.jeb.core.units.IBinaryUnit;
import com.pnfsoftware.jeb.core.units.IUnit;
import com.pnfsoftware.jeb.core.units.UnitUtil;
import com.pnfsoftware.jeb.util.encoding.Hash;
import com.pnfsoftware.jeb.util.events.IEvent;
import com.pnfsoftware.jeb.util.events.IEventListener;
import com.pnfsoftware.jeb.util.format.Formatter;
import com.pnfsoftware.jeb.util.format.Strings;
import com.pnfsoftware.jeb.util.io.IO;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * VirusTotal Scan Report Plugin. This <em>JEB engines plugin</em> is loaded automatically. Every
 * time an artifact is loaded into a project, the top-level binary units it produces will be checked
 * for existing scan reports on VirusTotal. The report result will be summarized and displayed in
 * the console, and an INFO notification will be added to the list of notifications. You may also
 * call execute the plugin manually (via the File, Plugins menu), for instance to request a most
 * current report if there is one.
 * 
 * @author PNF Software
 *
 */
public class VirustotalReportPlugin extends AbstractEnginesPlugin {
    private static final ILogger logger = GlobalLog.getLogger(VirustotalReportPlugin.class);

    private IEnginesContext engctx;
    private IEventListener listener;
    private String apikey;

    @Override
    public IPluginInformation getPluginInformation() {
        return new PluginInformation("VT Report Plugin",
                "Display and record VirusTotal reports for top-level binary units processed in JEB", "PNF Software",
                Version.create(1, 0, 0));
    }

    @Override
    public void load(IEnginesContext engctx) {
        this.engctx = engctx;
        apikey = getApiKey(engctx);
        listener = new IEventListener() {
            @Override
            public void onEvent(IEvent e) {
                // add contributions to newly-created units
                if(e.getType() == J.UnitCreated && e.getData() instanceof IBinaryUnit) {
                    IBinaryUnit unit = (IBinaryUnit)e.getData();
                    if(unit.getParent() instanceof IArtifact) {
                        logger.debug("Top-level binary unit was created: %s", unit);
                        try {
                            checkVT(unit);
                        }
                        catch(Exception ex) {
                            logger.catching(ex);
                        }
                    }
                }
            }
        };
        engctx.addListener(listener);
    }

    @Override
    public void dispose() {
        if(listener != null) {
            engctx.removeListener(listener);
            listener = null;
        }
    }

    @Override
    public List<? extends IOptionDefinition> getExecutionOptionDefinitions() {
        return Arrays.asList(new OptionDefinition(null, "Specify or update your VirusTotal API key:"),
                new OptionDefinition("apikey", apikey, "VirusTotal API Key"));
    }

    @Override
    public void execute(IEnginesContext engctx, Map<String, String> executionOptions) {
        if(executionOptions != null) {
            apikey = executionOptions.get("apikey");
            if(apikey != null) {
                setApiKey(engctx, apikey);
            }
        }
        if(apikey == null) {
            logger.error("In order to use the VirusTotal Scan Report plugin, set up your VT API key first!");
            return;
        }
        processAll(engctx);
    }

    private String getApiKey(IEnginesContext engctx) {
        try {
            return engctx.getPropertyManager().getString(".VirusTotalApiKey");
        }
        catch(Exception e) {
            return null;
        }
    }

    private boolean setApiKey(IEnginesContext engctx, String key) {
        try {
            engctx.getPropertyManager().setString(".VirusTotalApiKey", key);
            return true;
        }
        catch(Exception e) {
            return false;
        }
    }

    /**
     * Trigger manual processing of all top-level binary units.
     * 
     * @param engctx
     */
    private void processAll(IEnginesContext engctx) {
        for(IRuntimeProject prj: engctx.getProjects()) {
            for(ILiveArtifact art: prj.getLiveArtifacts()) {
                for(IUnit unit: art.getUnits()) {
                    if(unit instanceof IBinaryUnit) {
                        try {
                            checkVT((IBinaryUnit)unit);
                        }
                        catch(Exception ex) {
                            logger.catching(ex);
                        }
                    }
                }
            }
        }
    }

    @SuppressWarnings("rawtypes")
    private boolean checkVT(IBinaryUnit unit) throws IOException, ParseException {
        // do not check for a specific format (eg, 64 hexnums chars) because VT could change or may have changed that
        if(Strings.isBlank(apikey)) {
            return false;
        }

        String h;
        try(InputStream in = unit.getInput().getStream()) {
            byte[] data = IO.readInputStream(in);
            h = Formatter.byteArrayToHexString(Hash.calculateSHA256(data)).toLowerCase();
        }

        logger.debug("Verifying SHA-256 hash on VirustTotal: %s", h);
        String url = String.format("https://www.virustotal.com/vtapi/v2/file/report?apikey=%s&resource=%s", apikey, h);
        String jsonResponse;

        jsonResponse = engctx.getNetworkUtility().query(url);
        logger.debug(jsonResponse);

        Map o = (Map)(new JSONParser().parse(jsonResponse));

        // "response_code" and "verbose_msg" are the only keys guaranteed to be present
        // ref: https://www.virustotal.com/en/documentation/public-api/
        if(!o.containsKey("response_code")) {
            logger.debug("Invalid VT answer: %s", url);
            return false;
        }

        Long responseCode = (Long)o.get("response_code");
        if(responseCode == 0L) {
            UnitUtil.logInfo(unit, null, true, logger, "VT: unknown file");
        }
        else if(responseCode == 1L) {
            long positives = (Long)o.get("positives");
            long total = (Long)o.get("total");
            String scanDate = (String)o.get("scan_date");
            UnitUtil.logInfo(unit, null, true, logger, "VT Report: %d/%d (%s)", positives, total, scanDate);
        }
        else if(responseCode == 2L) {
            // do not record
            UnitUtil.logInfo(unit, null, false, logger, "VT: analysis in progress");
        }
        else {
            // do not record
            UnitUtil.logInfo(unit, null, false, logger, "VT: error - unknown response_code");
        }
        return true;
    }
}