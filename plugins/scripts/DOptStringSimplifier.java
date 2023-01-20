import com.pnfsoftware.jeb.core.units.code.android.controlflow.BasicBlock;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDVisitor;
import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDCallInfo;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDExpression;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDImm;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstruction;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDOperation;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.IVisitResults;
import com.pnfsoftware.jeb.core.units.code.java.JavaOperatorType;

/**
 * (NOTE: Sample IR optimizer plugin for JEB's dexdec. A variant of this plugin is shipping as a dexdec built-in.
 * As such, there is no need to enable this sample as it is. Its goal is to showcase parts of dexdec IR API for
 * learning and experimental purposes.)
 * <p>
 * Simplify useless calls to {@code String.valueOf}.
 * 
 * <pre>
 * String.valueOf(some_string)
 * 
 * => (simplified to)
 *  
 * some_string
 * </pre>
 *
 * @author Nicolas Falliere
 *
 */
public class DOptStringSimplifier extends AbstractDOptimizer {
    private static final String msig0 = "Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;";

    private int totalcnt;

    @Override
    public int perform() {
        totalcnt = 0;

        for(int iblk = 0; iblk < cfg.size(); iblk++) {
            BasicBlock<IDInstruction> b = cfg.get(iblk);

            for(int i = 0; i < b.size(); i++) {
                IDInstruction insn = b.get(i);

                insn.visitDepthPost(new IDVisitor() {
                    @Override
                    public void process(IDExpression e, IDExpression parent, IVisitResults<IDExpression> results) {
                        if(e instanceof IDCallInfo && msig0.equals(((IDCallInfo)e).getMethodSignature())) {
                            IDExpression arg0 = ((IDCallInfo)e).getArgument(0);
                            boolean proceed = false;
                            if(arg0 instanceof IDImm && ((IDImm)arg0).isString()) {
                                proceed = true;
                            }
                            else if(arg0 instanceof IDOperation
                                    && ((IDOperation)arg0).getOperator().is(JavaOperatorType.CONCAT)) {
                                proceed = true;
                            }
                            if(arg0 instanceof IDCallInfo
                                    && ((IDCallInfo)arg0).getMethodSignature().endsWith(")Ljava/lang/String;")) {
                                proceed = true;
                            }
                            if(proceed) {
                                if(parent.replaceSubExpression(e, arg0)) {
                                    totalcnt++;
                                }
                            }
                        }
                    }
                });
            }
        }

        return totalcnt;
    }
}