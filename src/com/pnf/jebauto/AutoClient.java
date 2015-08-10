package com.pnf.jebauto;

import java.io.File;
import java.util.List;

import org.apache.commons.configuration2.BaseConfiguration;

import com.pnfsoftware.jeb.core.Artifact;
import com.pnfsoftware.jeb.core.ICoreContext;
import com.pnfsoftware.jeb.core.IEnginesContext;
import com.pnfsoftware.jeb.core.ILiveArtifact;
import com.pnfsoftware.jeb.core.IRuntimeProject;
import com.pnfsoftware.jeb.core.JebCoreService;
import com.pnfsoftware.jeb.core.dao.IDataProvider;
import com.pnfsoftware.jeb.core.dao.IFileDatabase;
import com.pnfsoftware.jeb.core.dao.IFileStore;
import com.pnfsoftware.jeb.core.dao.impl.DataProvider;
import com.pnfsoftware.jeb.core.dao.impl.SimpleFSFileDatabase;
import com.pnfsoftware.jeb.core.dao.impl.SimpleFSFileStore;
import com.pnfsoftware.jeb.core.input.FileInput;
import com.pnfsoftware.jeb.core.properties.IConfiguration;
import com.pnfsoftware.jeb.core.properties.impl.CommonsConfigurationWrapper;
import com.pnfsoftware.jeb.core.units.IUnit;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Skeleton for a JEB2 headless client (eg, for automation/bulk processing)
 * !! IMPORTANT !! The areas marked "TODO: customize" must be edited prior to executing this code
 */
public class AutoClient {
    static final ILogger logger = GlobalLog.getLogger(AutoClient.class);
    static {
        GlobalLog.addDestinationStream(System.out);
    }
    
    // TODO: customize (should be replaced by the LicenseKey entry in your bin/jeb-client.cfg file)
    private static final String licenseKey = "...";
    
    // TODO: customize
    private static final String baseDir = "...";
    
    public static void main(String[] argv) throws Exception {
        if(argv.length <= 0) {
            return;
        }
        
        long t0 = System.currentTimeMillis();
        String location = argv[0];
        List<File> files = AutoUtil.retrieveFiles(location);
        test(files);
        logger.info("Done in %ds", (System.currentTimeMillis()-t0)/1000);
    }
    
    /**
     * Initialize a core. Create a context within that core. Then, for each input artifact,
     * a project is created and the artifact is loaded within that project.
     * @param files
     * @throws Exception
     */
    public static void test(List<File> files) throws Exception {
        // create or retrieve a core context (engines container)
        ICoreContext core = JebCoreService.getInstance(licenseKey);
        
        // create an engines context (project container)
        IFileDatabase projectdb = new SimpleFSFileDatabase(baseDir);
        IFileStore filestore = new SimpleFSFileStore(baseDir);
        BaseConfiguration cfg = new BaseConfiguration();
        
        // TODO: customize (alternative is to read your configuration from .cfg file)
        cfg.setProperty(".DevPluginClasspath", "...");
        
        // TODO: customize
        cfg.setProperty(".DevPluginClassnames", "...");
        
        IConfiguration config = new CommonsConfigurationWrapper(cfg);
        IDataProvider dataProvider = new DataProvider(null, projectdb, filestore, null, null, config);
        IEnginesContext engctx = core.createEnginesContext(dataProvider, null);
        
        int i = 0;
        for(File file: files) {
            i++;
            logger.info("Testing file %d/%d : %s ...", i, files.size(), file.getName());

            // create or load a project (artifact container)
            IRuntimeProject prj = engctx.loadProject("ProjectTest"+i);
        
            // process the artifact, get units
            ILiveArtifact art = prj.processArtifact(new Artifact(file.getName(), new FileInput(file)));
            
            // proceed with the units
            @SuppressWarnings("unused")
            List<IUnit> units = art.getUnits();
            
            // TODO: CUSTOMIZE -- this is the important part
            // Basic tests go here
            // example:
            for(IUnit unit: units) {
            //     if(unit instanceof Xyz) {
            //         // ...
            //         // ...
            //     }
            }
            
            engctx.unloadProject(prj.getKey());
        }
        
        // close the engines
        JebCoreService.getInstance().closeEnginesContext(engctx);
    }
}