
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

import com.pnfsoftware.jeb.core.JebCoreService;
import com.pnfsoftware.jeb.core.units.IUnit;
import com.pnfsoftware.jeb.util.base.Env;
import com.pnfsoftware.jeb.util.io.IO;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Skeleton file for a custom JEB client. Requires JEB Pro version 5.37 or above.
 * <p>
 * This simple client that takes a list of files and processes them. It can be extended to write
 * some automation code for bulk processing.
 * <p>
 * The sole dependency is {@code jeb.jar}. If you have JEB installed on your machine pointed to by
 * {@code $JEB_HOME}, this code will try to pull information (such as license key and engines
 * configuration) from that installation.
 * <p>
 * API reference: https://www.pnfsoftware.com/jeb/apidoc/
 * 
 */
public class JebClient {
    static final ILogger logger = GlobalLog.getLogger(JebClient.class);
    static {
        GlobalLog.addDestinationStream(System.out);
    }

    // provide a folder with files as the command-line argument
    public static void main(String[] args) throws Exception {
        if(args.length == 0) {
            throw new RuntimeException("Provide a directory for scanning as the first command-line argument");
        }

        var jebHome = Env.get("JEB_HOME");
        if(jebHome == null) {
            throw new RuntimeException("Set the JEB_HOME environment variable to point to your JEB folder");
        }

        // instantiate the JEB core service
        var jeb = JebCoreService.getInstance(new File(jebHome));

        // create an engines context (a container of JEB projects)
        var engctx = jeb.createEnginesContext();

        // scan some files
        var files = IO.listFiles(args[0]);
        int i = 0;
        for(var file: files) {
            i++;
            logger.info("Processing file %d/%d : %s ...", i, files.size(), file.getName());

            // create or load a project (artifact container)
            var prj = engctx.createProject("ProjectTest" + i);

            // process the artifact, get units
            var art = prj.processArtifact(file);

            // proceed with the units
            var units = art.getUnits();

            // work with the units
            for(IUnit unit: units) {
                logger.info("Unit: %s", unit);
                //
                // ... do some work
                //
            }

            engctx.unloadProject(prj.getKey());
        }

        // close our engines context
        jeb.closeEnginesContext(engctx);

        // close JEB
        jeb.close();
    }
}