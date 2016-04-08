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

package com.pnf.andsig;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
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
import com.pnfsoftware.jeb.core.output.ItemClassIdentifiers;
import com.pnfsoftware.jeb.core.units.IMetadataGroup;
import com.pnfsoftware.jeb.core.units.MetadataGroupType;
import com.pnfsoftware.jeb.core.units.code.ICodeUnit;
import com.pnfsoftware.jeb.core.units.code.android.IDexUnit;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDexClass;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDexCodeItem;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDexMethod;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDexMethodData;
import com.pnfsoftware.jeb.util.CollectionUtil;
import com.pnfsoftware.jeb.util.Conversion;
import com.pnfsoftware.jeb.util.IO;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Sign and apply signatures to find Android library methods. This plugin was ported from JEB1.
 * Currently a partial port. Refer to {@link AndroidSigGenPlugin} for additional documentation and
 * how-to use.
 * <p>
 * This is the second part of a 2-part plugin. First part: {@link AndroidSigGenPlugin}.
 * <p>
 * TODO: rename methods and refactor+rename flattened packages if need be
 * 
 * @author Nicolas Falliere
 * @see AndroidSigGenPlugin
 */
public class AndroidSigApplyPlugin implements IEnginesPlugin {
    private static final ILogger logger = GlobalLog.getLogger(AndroidSigApplyPlugin.class);

    @Override
    public IPluginInformation getPluginInformation() {
        return new PluginInformation("Android Code Recognition",
                "Apply code signatures to identify Android libraries (Ported from JEB1)", "PNF Software",
                Version.create(1, 0), Version.create(2, 2, 1), null);
    }

    @Override
    public List<? extends IOptionDefinition> getExecutionOptionDefinitions() {
        return null;
    }

    @Override
    public void dispose() {
    }

    @Override
    public void execute(IEnginesContext context) {
        execute(context, null);
    }

    /** do not match small routines or small classes */
    static final int MIN_OPCODE_LENGTH = 8;

    /** dictionary of class: { chash -> list of (libname, cname) } */
    Map<Long, List<String[]>> allc;
    /** dictionary of methods: {mhash -> list of (...) } */
    Map<String, List<String[]>> allm;
    /** number of new methods matched */
    int matchcount_total;
    /** number of new methods matched */
    int matchcount_new;
    /** library name -> number of methods matched within that library */
    Map<String, Integer> matchcount_per_lib;

    @Override
    public void execute(IEnginesContext engctx, Map<String, String> executionOptions) {
        IRuntimeProject prj = engctx.getProject(0);
        if(prj == null) {
            return;
        }

        allc = new HashMap<>();
        allm = new HashMap<>();
        matchcount_total = 0;
        matchcount_new = 0;
        matchcount_per_lib = new HashMap<>();

        File sigFolder = AndroidSigGenPlugin.getSignaturesFolder(engctx);
        loadAllSignatures(sigFolder);

        List<IDexUnit> dexlist = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit.class, false);
        for(IDexUnit dex: dexlist) {
            applySignatures(dex);
        }
    }

    void loadAllSignatures(File sigFolder) {
        for(File f: sigFolder.listFiles()) {
            if(f.isFile() && f.getName().endsWith(".sig")) {
                if(!loadSignatures(f)) {
                    logger.error("Cannot load signatures files: %s", f);
                }
            }
        }
    }

    String checkMarker(String line, String marker) {
        if(line.startsWith(marker + "=")) {
            return line.substring(marker.length() + 1).trim();
        }
        return null;
    }

    boolean loadSignatures(File sigFile) {
        int version = 0;
        String libname = "Unknown library code";

        List<String> lines;
        try {
            lines = IO.readLines(new FileInputStream(sigFile), Charset.forName("UTF-8"));
        }
        catch(IOException e) {
            logger.catching(e);
            return false;
        }

        List<MethodLine> mllist = new ArrayList<MethodLine>();
        for(String line: lines) {
            line = line.trim();
            if(line.isEmpty()) {
                continue;
            }

            if(line.startsWith(";")) {
                line = line.substring(1);

                String value = checkMarker(line, "version");
                if(value != null) {
                    version = Conversion.stringToInt(value);
                }

                value = checkMarker(line, "libname");
                if(value != null) {
                    libname = value;
                }

                continue;
            }

            if(version != AndroidSigGenPlugin.androidSigFileVersion) {
                logger.error("Unsupported version: %d", version);
                return false;
            }

            MethodLine ml = MethodLine.parse(line);
            if(ml == null) {
                logger.warn("Invalid signature line: %s", line);
                continue;
            }

            mllist.add(ml);
        }

        // sort method lines by ascending class FQ-name
        Collections.sort(mllist, new Comparator<MethodLine>() {
            @Override
            public int compare(MethodLine o1, MethodLine o2) {
                return o1.cname.compareTo(o2.cname);
            }
        });
        // build class signatures, derived from method signatures
        long chash = 1;
        String cname0 = null;
        for(MethodLine ml: mllist) {
            // works because we sorted mllist
            if(ml.cname != cname0) {
                storeClassHash(chash, cname0, libname);
                chash = 1L;
                cname0 = ml.cname;
            }
            chash *= Long.parseLong(ml.mhash.substring(0, 8), 16);
        }
        storeClassHash(chash, cname0, libname);

        // store method signatures
        for(MethodLine ml: mllist) {
            storeMethodHash(ml.mhash, ml.cname, ml.mname, libname);
        }

        // note: recommended libname format is: 'name-version'
        // sort by descending library name: more recent libraries will be picked first
        // TODO: ...

        return true;
    }

    void storeClassHash(long chash, String cname, String libname) {
        if(chash != 1L) {
            if(!allc.containsKey(chash)) {
                allc.put(chash, new ArrayList<String[]>());
            }
            allc.get(chash).add(new String[]{libname, cname});
        }
    }

    void storeMethodHash(String mhash, String cname, String mname, String libname) {
        if(!allm.containsKey(mhash)) {
            allm.put(mhash, new ArrayList<String[]>());
        }
        allm.get(mhash).add(new String[]{libname, cname, mname});
    }

    void applySignatures(IDexUnit dex) {
        // class hashes for the current file, built on the fly
        // maps a type index to a tuple (class hash, total number of opcodes)
        //        Map<String, ...> chashes = new HashMap<>();

        // method matching
        for(IDexMethod m: dex.getMethods()) {
            if(!m.isInternal()) {
                continue;
            }

            IDexMethodData md = m.getData();
            if(md == null) {
                continue;
            }

            IDexCodeItem ci = md.getCodeItem();
            if(ci == null) {
                continue;
            }

            String mhash = AndroidSigGenPlugin.hashDexMethod(ci);
            if(mhash == null) {
                continue;
            }

            // update associated class signature
            // ...

            // do not attempt method matching if the method is too small
            if(ci.getInstructions().size() >= MIN_OPCODE_LENGTH) {
                List<String[]> elts = allm.get(mhash);
                String[] e = CollectionUtil.getFirst(elts);
                if(e != null) {
                    // process the first match (do not check "shorty", a perfect hash match is enough)
                    matchcount_total++;

                    //...

                    getCodeGroup(dex).setData(m.getSignature(false), ItemClassIdentifiers.CODE_LIBRARY.getId());
                }
            }
        }

        // class matching, not as accurate, but useful for classes having
        // lots of small methods (therefore, unmatched methods)
        for(@SuppressWarnings("unused")
        IDexClass c: dex.getClasses()) {
            ;
        }
    }

    IMetadataGroup getCodeGroup(ICodeUnit unit) {
        IMetadataGroup grp = unit.getMetadataManager().getGroupByName("codeAnalysis");
        if(grp == null) {
            grp = new DexMetadataGroup("codeAnalysis", MetadataGroupType.CLASSID);
            unit.getMetadataManager().addGroup(grp);
        }
        return grp;
    }
}
