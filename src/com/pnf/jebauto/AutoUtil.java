package com.pnf.jebauto;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * Utility methods.
 */
public class AutoUtil {

    /**
     * List all files recursively.
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
