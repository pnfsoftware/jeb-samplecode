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
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.configuration2.PropertiesConfiguration;
import org.apache.commons.configuration2.builder.FileBasedConfigurationBuilder;
import org.apache.commons.configuration2.builder.fluent.Parameters;
import org.apache.commons.configuration2.ex.ConfigurationException;

import com.pnfsoftware.jeb.core.properties.IConfiguration;
import com.pnfsoftware.jeb.core.properties.impl.CommonsConfigurationWrapper;

/**
 * Some utility code used by {@link JebClient}.
 *
 * @author Nicolas Falliere
 *
 */
public class JebUtil {

    /**
     * Create a configuration object for a JEB configuration file, such as {@code jeb-engines.cfg}.
     * 
     * @param file
     * @return
     */
    public static IConfiguration getConfiguration(File file) {
        if(!file.isFile()) {
            try {
                file.createNewFile();
            }
            catch(IOException e) {
                throw new RuntimeException(e);
            }
        }
        Parameters params = new Parameters();
        FileBasedConfigurationBuilder<PropertiesConfiguration> builder = new FileBasedConfigurationBuilder<>(
                PropertiesConfiguration.class).configure(params.properties().setFile(file));
        builder.setAutoSave(true);
        try {
            return new CommonsConfigurationWrapper(builder.getConfiguration());
        }
        catch(ConfigurationException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * List files recursively.
     * 
     * @param location root directory
     * @return a list of files
     */
    public static List<File> retrieveFiles(String location) {
        List<File> results = new ArrayList<>();
        retrieveFilesRecurse(new File(location), results);
        return results;
    }

    private static void retrieveFilesRecurse(File f, List<File> results) {
        if(f.isFile()) {
            results.add(f);
        }
        else {
            for(String name: f.list()) {
                File f1 = new File(f, name);
                retrieveFilesRecurse(f1, results);
            }
        }
    }
}
