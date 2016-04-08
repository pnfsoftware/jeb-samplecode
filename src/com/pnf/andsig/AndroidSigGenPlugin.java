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
import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

import com.pnfsoftware.jeb.client.Licensing;
import com.pnfsoftware.jeb.core.IEnginesContext;
import com.pnfsoftware.jeb.core.IEnginesPlugin;
import com.pnfsoftware.jeb.core.IOptionDefinition;
import com.pnfsoftware.jeb.core.IPluginInformation;
import com.pnfsoftware.jeb.core.IRuntimeProject;
import com.pnfsoftware.jeb.core.OptionDefinition;
import com.pnfsoftware.jeb.core.PluginInformation;
import com.pnfsoftware.jeb.core.RuntimeProjectUtil;
import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.core.units.code.ICodeUnit;
import com.pnfsoftware.jeb.core.units.code.android.IDexUnit;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDalvikInstruction;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDalvikInstructionParameter;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDexCodeItem;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDexMethod;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDexMethodData;
import com.pnfsoftware.jeb.core.units.code.android.dex.IDexPrototype;
import com.pnfsoftware.jeb.util.Formatter;
import com.pnfsoftware.jeb.util.IO;
import com.pnfsoftware.jeb.util.Strings;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Generate generic simple signatures for Android library methods. This plugin was ported from JEB1.
 * It is in no means intended to be used in professional systems: it is simply a POC show-casing how
 * easy it is to build a signing+matching system for DEX bytecode. It could easily be improved and extended
 * for all {@link ICodeUnit} in general, instead of being limited to {@link IDexUnit}.
 * <p>
 * This is the first part of a 2-part plugin. Second part: {@link AndroidSigApplyPlugin}.
 * <p>
 * How to use:
 * <ul>
 * <li>Load a DEX file (UI, headless client, other)</li>
 * <li>Execute the plugin, optionally providing a filter regex and library name</p>
 * <li>Signature file goes to <code>[JEB_PLUGINS]/android_sigs/[libname].sig</code></li>
 * <li>To apply sigs on unknown files, execute the {@link AndroidSigApplyPlugin} plugin</li>
 * </ul>
 * 
 * @author Nicolas Falliere
 * @see AndroidSigApplyPlugin
 */
public class AndroidSigGenPlugin implements IEnginesPlugin {
    private static final ILogger logger = GlobalLog.getLogger(AndroidSigGenPlugin.class);

    static final int androidSigFileVersion = 1;

    private static final boolean verbose = true;

    @Override
    public IPluginInformation getPluginInformation() {
        return new PluginInformation("Android Code Signature Generator",
                "Generate generic signatures to identify Android libraries (Ported from JEB1)", "PNF Software",
                Version.create(1, 0), Version.create(2, 2, 1), null);
    }

    @Override
    public List<? extends IOptionDefinition> getExecutionOptionDefinitions() {
        return Arrays.asList(new OptionDefinition("libname", "Library name"), new OptionDefinition("cpattern",
                "Class pattern regex"));
    }

    @Override
    public void dispose() {
    }

    @Override
    public void execute(IEnginesContext context) {
        execute(context, null);
    }

    private StringBuilder sb;
    private Pattern cpatternRE;
    private int methodCount;

    @Override
    public void execute(IEnginesContext engctx, Map<String, String> executionOptions) {
        IRuntimeProject prj = engctx.getProject(0);
        if(prj == null) {
            return;
        }

        // reset attributes
        sb = new StringBuilder();
        cpatternRE = null;
        methodCount = 0;

        String libname = executionOptions.get("libname");
        if(Strings.isBlank(libname)) {
            libname = prj.getName();
        }

        String cpattern = executionOptions.get("cpattern");
        if(!Strings.isBlank(cpattern)) {
            try {
                cpatternRE = Pattern.compile(cpattern);
            }
            catch(PatternSyntaxException e) {
                logger.error("Invalid regex for cpattern: %s", e.getDescription());
            }
        }

        record(";comment=JEB signature file");
        record(";author=" + Licensing.user_name);
        record(";version=" + androidSigFileVersion);
        record(";libname=" + libname);

        List<IDexUnit> dexlist = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit.class, false);
        for(IDexUnit dex: dexlist) {
            processDex(dex);
        }

        if(methodCount >= 1) {
            File sigFolder = getSignaturesFolder(engctx);
            
            File f = new File(sigFolder, sanitizeFilename(libname) + ".sig");
            logger.info("Saving signatures to file: %s", f);
            try {
                byte[] data = sb.toString().getBytes("UTF-8");
                if(!IO.writeFileSafe(f, data, true)) {
                    logger.error("Could not write signature file!");
                }
            }
            catch(UnsupportedEncodingException e) {
                logger.catching(e);
            }
        }
    }

    static File getSignaturesFolder(IEnginesContext engctx) {
        String pluginFolderPath = engctx.getDataProvider().getPluginStore().getStoreLocation();
        return new File(pluginFolderPath, "android_sigs");
    }

    void record(String s) {
        sb.append(s);
        sb.append('\n');

        if(verbose) {
            logger.info(s);
        }
    }

    String sanitizeFilename(String s) {
        String s2 = "";
        for(int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            s2 += c == '-' || Character.isJavaIdentifierPart(c) ? c: '_';
        }
        return s2;
    }

    boolean processDex(IDexUnit dex) {
        if(!dex.isProcessed()) {
            if(!dex.process()) {
                return false;
            }
        }

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

            String msig = m.getSignature(true);
            if(cpatternRE != null && !cpatternRE.matcher(msig).matches()) {
                continue;
            }

            String mhash = hashDexMethod(ci);
            if(mhash == null) {
                continue;
            }

            String classfullname = dex.getTypes().get(m.getClassTypeIndex()).getSignature(true);
            String methodname = m.getName(true);
            IDexPrototype proto = dex.getPrototypes().get(m.getPrototypeIndex());
            String shorty = dex.getStrings().get(proto.getShortyIndex()).getValue();
            int opcount = ci.getInstructions().size();
            String s = String.format("%s,%s,%s,%d,%s", classfullname, methodname, shorty, opcount, mhash);
            record(s);
            methodCount++;
        }

        return true;
    }

    static String hashDexMethod(IDexCodeItem ci) {
        String sig = "";
        for(IDalvikInstruction insn: ci.getInstructions()) {
            String token = insn.getMnemonic() + ":";
            // note: array- and switch-data are disregarded
            for(IDalvikInstructionParameter param: insn.getParameters()) {
                int pt = param.getType();
                token += String.format("%d,", pt);
                if(pt == IDalvikInstruction.TYPE_IDX) {
                    token += "x,";  // disregard pool indexes;
                }
                else {
                    token += String.format("%d,", param.getValue());
                }
            }
            token += " ";
            sig += token;
        }
        //logger.info("-> %s", sig);

        byte[] h;
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            h = md.digest(sig.getBytes());
        }
        catch(NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }

        return Formatter.byteArrayToHexString(h).toLowerCase();
    }
}
