import com.pnfsoftware.jeb.core.units.code.android.controlflow.BasicBlock;
import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDExpression;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDImm;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstruction;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDOperation;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDPredicate;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDVisitor;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.IVisitResults;

/**
 * (NOTE: Sample IR optimizer plugin for JEB's dexdec. A variant of this plugin is shipping as a dexdec built-in.
 * As such, there is no need to enable this sample as it is. Its goal is to showcase parts of dexdec IR API for
 * learning and experimental purposes.)
 * <p>
 * Simple expression evaluator and folder.
 * <p>
 * Example:
 * 
 * <pre>
 * 4 + 5 => 9
 * 1 & 6 => 0
 * ...
 * </pre>
 * 
 * <p>
 * Note: this source file is a sample IR optimizer for JEB's dexdec. A variant of this optimizer is
 * already shipping with dexdec as a built-in optimizer.
 * 
 * @author Nicolas Falliere
 *
 */
public class DOptEvalFolder extends AbstractDOptimizer {
    private int totalcnt = 0;

    @Override
    public int perform() {
        totalcnt = 0;

        for(BasicBlock<IDInstruction> b: cfg) {
            for(IDInstruction insn: b) {
                insn.visitInstruction(new IDVisitor() {
                    @Override
                    public void process(IDExpression e, IDExpression parent, IVisitResults<IDExpression> results) {
                        if(e instanceof IDOperation) {
                            IDExpression repl = null;
                            try {
                                IDImm cst = e.evaluate(ctx);
                                if(cst != null && !cst.isRef()) {
                                    // IDPredicate (type inhering IDOperation) need special handling to be replaced
                                    if(e instanceof IDPredicate) {
                                        repl = g.createPredicate(cst);
                                        // we may have created an IR identical to the source, watch for this
                                        if(repl.equalsEx(e, false)) {
                                            repl = null;
                                        }
                                    }
                                    else {
                                        repl = cst;
                                    }
                                    if(repl != null && parent.replaceSubExpression(e, repl)) {
                                        results.setReplacedNode(repl);
                                        totalcnt++;
                                    }
                                }
                            }
                            catch(Exception ex0) {
                                // neuter eval() exceptions
                            }
                        }
                    }
                }, true);
            }
        }

        if(totalcnt > 0) {
            // just in case, since some expressions containing variables may have been reduced, example: 0*x => 0 (-> x is no longer used)
            cfg.invalidateDataFlowAnalysis();
        }
        return totalcnt;
    }
}
