import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.DexDecEvaluationException;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDVisitor;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDArrayElt;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDExpression;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstruction;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDNewArrayInfo;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.IVisitResults;

/**
 * (NOTE: Sample IR optimizer plugin for JEB's dexdec. A variant of this plugin is shipping as a dexdec built-in.
 * As such, there is no need to enable this sample as it is. Its goal is to showcase parts of dexdec IR API for
 * learning and experimental purposes.)
 * <p>
 * Resolve direct array element access.
 * <p>
 * Example:
 * 
 * <pre>
 * a = new int[]{2, 3, 5, 7, 11}[1]
 * 
 * =>
 * 
 * a = 3
 * </pre>
 * 
 * @author Nicolas Falliere
 * 
 */
public class DOptArrayInitCleanup extends AbstractDOptimizer {
    private int totalcnt;

    @Override
    public int perform() {
        totalcnt = 0;

        // go through the instructions of the CFG sequentially
        for(IDInstruction insn: cfg.instructions()) {

            // pre-order visit of all the IR expressions making up the current instruction
            // important note: if the instruction is an ASSIGN, we skip processing the destination (left-side) expression
            insn.visitInstruction(new IDVisitor() {
                @Override
                public void process(IDExpression e, IDExpression parent, IVisitResults<IDExpression> results) {
                    if(e.isArrayElt()) {
                        IDArrayElt aelt = e.asArrayElt();

                        if(aelt.getIndex().isImm() && aelt.getArray().isNewArrayInfo()) {

                            int index;
                            try {
                                index = (int)aelt.getIndex().asImm().toLong();
                            }
                            catch(DexDecEvaluationException ex) {
                                return;
                            }

                            IDNewArrayInfo array = aelt.getArray().asNewArrayInfo();
                            if(index >= 0 && index < array.getCountOfInitialValues()) {

                                // if any of the array initial values have side-effects, we cannot safely discard them
                                // example: the expression "new int[] {10, 20, foo(), 40} [1]"
                                // cannot be replaced by "20" if foo() has or may have have side-effects
                                for(IDExpression val: array.getInitialValues()) {
                                    if(val.hasSideEffects(ctx, true)) {
                                        return;  // bail
                                    }
                                }

                                IDExpression repl = array.getInitialValue(index);
                                // note: repl should never be null, this is just a sanity check
                                if(repl != null && parent.replaceSubExpression(e, repl)) {
                                    results.setReplacedNode(repl);  // <-- in pre-order, we must report the replaced node
                                    totalcnt++;
                                }
                            }
                        }
                    }
                }
            }, true);
        }

        if(totalcnt > 0) {
            // dexdec IR CFG's share a single DFA object; if modifications of an optimizer changes
            // variable (identifier) arrangements in any way, the current DFA must be invalidated
            cfg.invalidateDataFlowAnalysis();
        }
        return totalcnt;
    }
}
