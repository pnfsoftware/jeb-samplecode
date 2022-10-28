import java.util.WeakHashMap;

import com.pnfsoftware.jeb.core.units.code.android.ApkManifestHelper;
import com.pnfsoftware.jeb.core.units.code.android.ApkStringResHelper;
import com.pnfsoftware.jeb.core.units.code.android.IApkUnit;
import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.DOptimizerType;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDCallInfo;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDExpression;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDImm;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstanceField;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstruction;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDVisitor;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.IVisitResults;
import com.pnfsoftware.jeb.util.encoding.Conversion;
import com.pnfsoftware.jeb.util.format.Strings;

/**
 * Custom IR optimizer plugin for dexdec.<br>
 * - Replace APK string resource access by the actual (default) string value.<br>
 * - Replace app info (application properties) by their actual value.<br>
 * <p>
 * This optimizer is aggressive (the scenarios for which those replacements are to be made are not
 * common) and potentially unsafe regarding string resource replacement. See details below.
 *
 * @author Nicolas Falliere
 *
 */
public class DOptUnsafeApkSpecificSubst extends AbstractDOptimizer {
    private int cnt;

    public DOptUnsafeApkSpecificSubst() {
        super(DOptimizerType.UNSAFE);
    }

    @Override
    public int perform() {
        // we need a parent APK to perform those optimizations
        if(!(dex.getParent() instanceof IApkUnit)) {
            return 0;
        }
        IApkUnit apk = (IApkUnit)dex.getParent();

        cnt = 0;

        for(IDInstruction insn: cfg.instructions()) {

            insn.visitInstruction(new IDVisitor() {

                @Override
                public void process(IDExpression e, IDExpression parent, IVisitResults<IDExpression> results) {
                    IDImm repl = null;

                    if(e.isCallInfo()) {
                        IDCallInfo ci = e.asCallInfo();
                        String msig = ci.getMethodSignature();
                        if(msig.equals("Landroid/content/res/Resources;->getString(I)Ljava/lang/String;")
                                || msig.equals("Landroid/content/Context;->getString(I)Ljava/lang/String;")) {
                            // e.g. someActivity.getString(RESID) or someActivity().getResources().getString(RESID)
                            if(ci.getArgument(1).isImm()) {
                                int rid = (int)ci.getArgument(1).asImm().getRawValue();
                                if(apk != null) {
                                    ApkStringResHelper helper = getStringResHelper(apk);
                                    if(helper != null) {
                                        String str = helper.getDefaultString(rid);
                                        if(str != null) {
                                            // UNSAFE since those methods can be overridden by activities
                                            repl = g.createString(str);
                                        }
                                    }
                                }
                            }
                        }
                        else if(msig.equals("Landroid/content/Context;->getPackageName()Ljava/lang/String;")) {
                            // fetch the actual value from the Manifest (the value is cached in the APK unit)
                            String str = apk.getPackageName();
                            if(str != null) {
                                repl = g.createString(str);
                            }
                        }
                    }
                    else if(e.isInstanceField()) {
                        IDInstanceField f = e.asInstanceField();
                        if(!f.isArrayLength()) {
                            String fsig = f.getNativeField(g).getSignature(false);
                            if(fsig.equals("Landroid/content/pm/ApplicationInfo;->targetSdkVersion:I")) {
                                // fetch the actual value from the Manifest
                                ApkManifestHelper mh = getManifestHelper(apk);
                                if(mh != null) {
                                    String attrval = mh.readAttribute("uses-sdk", "targetSdkVersion");
                                    if(!Strings.isBlank(attrval)) {
                                        int targetSdkVersion = Conversion.stringToInt(attrval);
                                        if(targetSdkVersion != 0) {
                                            repl = g.createInt(targetSdkVersion);
                                        }
                                    }
                                }
                            }
                        }
                    }
                    // TODO: add more, as necessary

                    if(repl != null && parent.replaceSubExpression(e, repl)) {
                        results.setReplacedNode(repl);
                    }
                }
            }, true);
        }

        if(cnt > 0) {
            cfg.resetDataFlowAnalysis();
        }
        return cnt;
    }

    private static WeakHashMap<IApkUnit, ApkStringResHelper> apkStringResHelperMap = new WeakHashMap<>();

    private static ApkStringResHelper getStringResHelper(IApkUnit apk) {
        if(apk == null) {
            return null;
        }
        ApkStringResHelper helper = apkStringResHelperMap.get(apk);
        if(helper == null) {
            if(apkStringResHelperMap.containsKey(apk)) {
                return null;
            }
            synchronized(apkStringResHelperMap) {
                helper = apkStringResHelperMap.get(apk);
                if(helper == null) {
                    try {
                        helper = new ApkStringResHelper(apk);
                    }
                    catch(Exception ex) {
                        // neuter
                    }
                    apkStringResHelperMap.put(apk, helper);
                }
            }
        }
        return helper;
    }

    private static WeakHashMap<IApkUnit, ApkManifestHelper> apkManifestHelperMap = new WeakHashMap<>();

    private static ApkManifestHelper getManifestHelper(IApkUnit apk) {
        if(apk == null) {
            return null;
        }
        ApkManifestHelper helper = apkManifestHelperMap.get(apk);
        if(helper == null) {
            if(apkManifestHelperMap.containsKey(apk)) {
                return null;
            }
            synchronized(apkManifestHelperMap) {
                helper = apkManifestHelperMap.get(apk);
                if(helper == null) {
                    try {
                        helper = new ApkManifestHelper(apk);
                    }
                    catch(Exception ex) {
                        // neuter
                    }
                    apkManifestHelperMap.put(apk, helper);
                }
            }
        }
        return helper;
    }
}
