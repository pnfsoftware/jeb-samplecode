
/*
 * JEB Copyright PNF Software, Inc.
 * 
 *     https://www.pnfsoftware.com
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import java.io.File;
import java.util.List;

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
import com.pnfsoftware.jeb.core.dao.impl.JDB2Manager;
import com.pnfsoftware.jeb.core.dao.impl.SimpleFSFileStore;
import com.pnfsoftware.jeb.core.input.FileInput;
import com.pnfsoftware.jeb.core.properties.IConfiguration;
import com.pnfsoftware.jeb.core.units.IUnit;
import com.pnfsoftware.jeb.util.base.Env;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Skeleton for a JEB simple client that takes a list of files and processes them. This class can be
 * extended to write some automation code for bulk processing.
 * <p>
 * The sole dependency is {@code jeb.jar}. If you have JEB installed on your machine pointed to by
 * {@code $JEB_HOME}, this code will try to pull information (such as license key or engines
 * configuration) from that installation, unless specified otherwise.
 * <p>
 * API reference: https://www.pnfsoftware.com/jeb/apidoc/
 * 
 * @author Nicolas Falliere
 * 
 */
public class JebClient {
    static final ILogger logger = GlobalLog.getLogger(JebClient.class);
    static {
        GlobalLog.addDestinationStream(System.out);
    }

    // NOTE: you may set the two fields below, else the main() will try to auto-determine them if your JEB was installed
    // and properly configured
    //
    /**
     * base directory that will contain the plugins and other JEB extensions; typically, this should
     * point to your JEB folder. Will be auto-determined if left null.
     */
    static String baseDir;
    /**
     * a Valid JEB license key. Will be auto-determined if left null.
     */
    static String licenseKey;

    public static void main(String[] argv) throws Exception {
        if(argv.length <= 0) {
            return;
        }

        // retrieve the JEB folder if none was specified
        if(baseDir == null) {
            baseDir = Env.get("JEB_HOME");
            if(baseDir == null) {
                throw new RuntimeException("Set the JEB_HOME environment variable to point to your JEB folder");
            }
        }
        // attempt to retrieve a valid license key if one had been generated
        if(licenseKey == null) {
            IConfiguration cfg = JebUtil.getConfiguration(new File(baseDir, "bin/jeb-client.cfg"));
            licenseKey = (String)cfg.getProperty(".LicenseKey");
            if(licenseKey == null) {
                throw new RuntimeException("Set a JEB license key");
            }
        }

        long t0 = System.currentTimeMillis();
        String location = argv[0];
        List<File> files = JebUtil.retrieveFiles(location);
        processFiles(files);
        logger.info("Done in %ds", (System.currentTimeMillis() - t0) / 1000);
        
        System.exit(0);  // ensure an exit, if some plugins misbehave 
    }

    /**
     * Initialize a core. Create a context within that core. Then, for each input artifact, a
     * project is created and the artifact is loaded within that project.
     */
    public static void processFiles(List<File> files) throws Exception {
        // create or retrieve a core context (engines container)
        ICoreContext core = JebCoreService.getInstance(licenseKey);

        // create an engines context (project container)
        IFileDatabase projectdb = new JDB2Manager(baseDir);
        IFileStore filestore = new SimpleFSFileStore(baseDir);
        IFileStore pluginstore = new SimpleFSFileStore(baseDir + File.separator + "coreplugins");

        // the code below reuses the engines configuration from your JEB install
        // if you'd rather have an empty config (or a different one), you could do:
        //   IConfiguration engconfig = new CommonsConfigurationWrapper(new BaseConfiguration());
        IConfiguration engconfig = JebUtil.getConfiguration(new File(baseDir, "bin/jeb-engines.cfg"));

        IDataProvider dataProvider = new DataProvider(null, projectdb, filestore, pluginstore, null, engconfig);
        IEnginesContext engctx = core.createEnginesContext(dataProvider, null);

        int i = 0;
        for(File file: files) {
            i++;
            logger.info("Processing file %d/%d : %s ...", i, files.size(), file.getName());

            // create or load a project (artifact container)
            IRuntimeProject prj = engctx.loadProject("ProjectTest" + i);

            // process the artifact, get units
            ILiveArtifact art = prj.processArtifact(new Artifact(file.getName(), new FileInput(file)));

            // proceed with the units
            List<IUnit> units = art.getUnits();

            // work with the units
            for(IUnit unit: units) {
                logger.info("Unit: %s", unit);
                // ... <do some work>
            }

            engctx.unloadProject(prj.getKey());
        }

        // close the engines
        JebCoreService.getInstance().closeEnginesContext(engctx);
    }
}