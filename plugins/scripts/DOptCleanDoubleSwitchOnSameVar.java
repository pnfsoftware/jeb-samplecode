import com.pnfsoftware.jeb.core.units.code.android.controlflow.BasicBlock;
import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDExpression;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstruction;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDSwitchData;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDTarget;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDTryData;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDVar;

/**
 * (NOTE: Sample IR optimizer plugin for JEB's dexdec. A variant of this plugin is shipping as a dexdec built-in.
 * As such, there is no need to enable this sample as it is. Its goal is to showcase parts of dexdec IR API for
 * learning and experimental purposes.)
 * <p>
 * Coalesce two switches, executed back-to-back on the same variable.
 * <p>
 * Example:
 * 
 * <pre>
 * ...
 * switch(var) {
 * case 1: ...
 * case 2: ...
 * }
 * switch(var) {
 * case 3: ...
 * case 4: ...
 * }
 * //
 * 
 * =>
 * 
 * ...
 * switch(var) {
 * case 1: ...
 * case 2: ...
 * case 3: ...
 * case 4: ...
 * }
 * </pre>
 * 
 * @author Nicolas Falliere
 *
 */
public class DOptCleanDoubleSwitchOnSameVar extends AbstractDOptimizer {

    @Override
    public int perform() {
        int totalcnt = 0;

        analyzeChains();

        for(int i = 1; i < cfg.size(); i++) {
            BasicBlock<IDInstruction> b = cfg.get(i);

            // second switch; block has only that instruction
            if(!(b.size() == 1 && b.insize() == 1 && b.get(0).isSwitch())) {
                continue;
            }

            // first switch; block ends up with the switch but may have more instructions
            BasicBlock<IDInstruction> p = cfg.get(i - 1);
            if(!p.getLast().isSwitch()) {
                continue;
            }

            IDInstruction sw0 = p.getLast();
            IDInstruction sw1 = b.getLast();

            if(!sw0.getSwitchData().isRegularSwitch() || !sw1.getSwitchData().isRegularSwitch()) {
                continue;
            }

            IDExpression e0 = sw0.getSwitchExpression();
            if(!(e0 instanceof IDVar) || !e0.equals(sw1.getSwitchExpression())) {
                continue;
            }

            IDTryData ex = ctx.getExceptionData();
            if(ex != null) {
                if(!ex.sameExceptionHandlers((int)p.getAddress(), (int)b.getAddress())) {
                    continue;
                }
            }

            // default block of the second switch, i.e. the subsequent block
            BasicBlock<IDInstruction> n = b.getOutputBlock(0);

            // upgrade the second switch (i.e. integrate the first switch info into it)
            IDSwitchData data0 = sw0.getSwitchData();
            IDSwitchData data1 = sw1.getSwitchData();
            for(Integer val: data0.getCasesAsInt()) {
                IDTarget t0 = data0.getTargetForCase(val);
                BasicBlock<IDInstruction> x0 = cfg.getBlockAt(t0.getOffset());
                if(x0 == n) {
                    data1.deleteCase(val);
                }
                else {
                    data1.addCase(val, t0, true);
                }
            }

            // edges for the upgraded switch (2nd)
            cfg.deleteOutEdges(b);
            cfg.addEdge(b, n);
            for(IDTarget t: data1.getTargets(true)) {
                cfg.addEdge(b, cfg.getBlockAt(t.getOffset()));
            }

            // neuter the first switch
            cfg.deleteOutEdges(p);
            cfg.addEdge(p, b);
            // replace it with a nop
            IDInstruction repl = ctx.createNop();
            repl.setOffset(sw0.getOffset());
            repl.setSize(sw0.getSize());
            p.set(p.size() - 1, repl);
            totalcnt++;
        }

        if(totalcnt > 0) {
            cleanGraph();
            cfg.invalidateDataFlowAnalysis();
        }
        return totalcnt;
    }
}
