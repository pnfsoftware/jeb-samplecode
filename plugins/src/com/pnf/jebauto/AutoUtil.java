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

package com.pnf.jebauto;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.configuration2.PropertiesConfiguration;
import org.apache.commons.configuration2.builder.FileBasedConfigurationBuilder;
import org.apache.commons.configuration2.builder.fluent.Parameters;
import org.apache.commons.configuration2.ex.ConfigurationException;

/**
 * Utility methods for headless JEB2 clients.
 * 
 * @author Nicolas Falliere
 * 
 */
public class AutoUtil {

    /**
     * List all files recursively.
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

    /**
     * Create an Apache properties object out of a JEB2 configuration file.
     * 
     * @param path path to a JEB2 configuration file, such as jeb-client.cfg or jeb-engines.cfg
     * @return
     */
    public static PropertiesConfiguration createPropertiesConfiguration(String path) {
        File configfile = new File(path);

        if(!configfile.isFile()) {
            try {
                configfile.createNewFile();
            }
            catch(IOException e) {
                throw new RuntimeException(e);
            }
        }

        Parameters params = new Parameters();
        FileBasedConfigurationBuilder<PropertiesConfiguration> builder = new FileBasedConfigurationBuilder<>(
                PropertiesConfiguration.class).configure(params.properties().setFileName(path));
        builder.setAutoSave(true);

        try {
            return builder.getConfiguration();
        }
        catch(ConfigurationException e) {
            throw new RuntimeException(e);
        }
    }
}
