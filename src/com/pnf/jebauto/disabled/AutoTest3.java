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

package com.pnf.jebauto.disabled;

import java.io.File;
import java.util.List;

import org.apache.commons.configuration2.BaseConfiguration;

import com.pnf.jebauto.AutoUtil;
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
 * Batch processing. Method 3: all artifacts in a single project, single engines context
 * 
 * @author Nicolas Falliere
 */
public class AutoTest3 {
    static final ILogger logger = GlobalLog.getLogger(AutoTest3.class);
    static {
        GlobalLog.addDestinationStream(System.out);
    }

    // customize
    private static final String licenseKey = "3812237624091570049Z513924477";
    private static final String baseDir = "C:/Users/Nicolas/projects/jeb2/testbase";

    public static void main(String[] argv) throws Exception {
        long t0 = System.currentTimeMillis();
        String location = "C:/Users/Nicolas/projects/jeb2/testbase/test"; // argv[0]
        List<File> files = AutoUtil.retrieveFiles(location);
        test(files);
        logger.info("Done in %ds", (System.currentTimeMillis() - t0) / 1000);
    }

    /**
     * Initialize a core. Create a context within that core. Then, for each input artifact, a
     * project is created and the artifact is loaded within that project.
     * 
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
        // !!!!!!! CUSTOMIZE !!!!!!!!
        cfg.setProperty(".DevPluginClasspath", "...");
        cfg.setProperty(".DevPluginClassnames", "...");
        IConfiguration config = new CommonsConfigurationWrapper(cfg);
        IDataProvider dataProvider = new DataProvider(null, projectdb, filestore, null, null, config);
        IEnginesContext engctx = core.createEnginesContext(dataProvider, null);

        // create or load a project (artifact container)
        IRuntimeProject prj = engctx.loadProject("ProjectTest");

        int i = 0;
        for(File file: files) {
            i++;
            logger.info("Testing file %d/%d : %s ...", i, files.size(), file.getName());

            // process the artifact, get units
            ILiveArtifact art = prj.processArtifact(new Artifact(file.getName(), new FileInput(file)));

            // proceed with the units
            @SuppressWarnings("unused")
            List<IUnit> units = art.getUnits();
            //logger.info("  => %d unit(s)", units.size());

            // --- CUSTOMIZE HERE ---
            // example:
            // for(IUnit unit: units) {
            //     if(unit instanceof Xyz) {
            //         ... // more checks
            //     }
            // }
        }

        // close the engines
        engctx.getExecutorService().shutdown();  // FIXME: fixed in latest build
        JebCoreService.getInstance().closeEnginesContext(engctx);
    }
}