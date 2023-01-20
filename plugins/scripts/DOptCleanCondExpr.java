import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDVisitor;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDExpression;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstruction;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDOperation;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.IVisitResults;

/**
 * (NOTE: Sample IR optimizer plugin for JEB's dexdec. A variant of this plugin is shipping as a dexdec built-in.
 * As such, there is no need to enable this sample as it is. Its goal is to showcase parts of dexdec IR API for
 * learning and experimental purposes.)
 * <p>
 * Simplify conditional expressions where both alternatives are the same.
 * <p>
 * Example:
 * 
 * <pre>
 * COND ? X: X     // COND has no side-effect
 * 
 * =>
 * 
 * X
 * </pre>
 * 
 * NOTE: gendec: see EOptUselessCondRem
 * 
 * @author Nicolas Falliere
 *
 */
public class DOptCleanCondExpr extends AbstractDOptimizer {
    private int totalcnt;

    @Override
    public int perform() {
        totalcnt = 0;

        for(IDInstruction insn: cfg.instructions()) {
            insn.visitInstructionPostOrder(new IDVisitor() {
                @Override
                public void process(IDExpression e, IDExpression parent, IVisitResults<IDExpression> results) {
                    if(e instanceof IDOperation && ((IDOperation)e).isConditional()) {
                        IDExpression eP = ((IDOperation)e).getCondPredicate();
                        IDExpression eT = ((IDOperation)e).getCondTrueExpression();
                        IDExpression eR = ((IDOperation)e).getCondFalseExpression();
                        if(eT.equalsEx(eR, false) && !eP.hasSideEffects(ctx, true)) {
                            if(parent.replaceSubExpression(e, eT)) {
                                totalcnt++;
                            }
                        }
                    }
                }
            }, true);
        }

        if(totalcnt > 0) {
            cfg.invalidateDataFlowAnalysis();
        }
        return totalcnt;
    }
}
