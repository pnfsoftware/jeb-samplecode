import com.pnfsoftware.jeb.core.units.code.android.controlflow.BasicBlock;
import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.DOpcodeType;
import com.pnfsoftware.jeb.core.units.code.android.ir.DUtil;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstruction;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDSwitchData;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDTarget;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDTryData;

/**
 * (NOTE: Sample IR optimizer plugin for JEB's dexdec. A variant of this plugin is shipping as a dexdec built-in.
 * As such, there is no need to enable this sample as it is. Its goal is to showcase parts of dexdec IR API for
 * learning and experimental purposes.)
 * <p>
 * Remove NOP assignments. Blocks made entirely of nops are removed as well.
 * <p>
 * Note: this source file is a sample IR optimizer for JEB's dexdec. A variant of this optimizer is
 * already shipping with dexdec as a built-in optimizer.
 *
 * @author Nicolas Falliere
 *
 */
public class DOptRemoveNops extends AbstractDOptimizer {

    @Override
    public int perform() {
        IDTryData exdata = ctx.getExceptionData();
        int cnt = 0;

        // nop removal in multi-instruction blocks, never end-up with empty blocks (no block deletion)
        // (i.e., at most, reduce the entire block to a single nop)
        if(true) {
            for(BasicBlock<IDInstruction> b: cfg) {
                int i = 0;
                while(i < b.size()) {
                    if(b.size() >= 2 && b.get(i).getOpcode() == DOpcodeType.IR_NOP) {
                        cnt++;
                        if(DUtil.removeInstruction(b, i)) {
                            continue;
                        }
                    }
                    i++;
                }
            }
        }

        // nop block removal: since it takes place after the above, those blocks would have been reduced to a single-instruction NOP
        // caveat: to keep things simple, we bail if the fall-through block is a handler
        int i = 0;
        while(i < cfg.size()) {
            BasicBlock<IDInstruction> b = cfg.get(i);
            if(b.size() != 1) {
                i++;
                continue;
            }

            // single-instruction NOP block
            IDInstruction insn = b.getLast();
            if(insn.getOpcode() != DOpcodeType.IR_NOP) {
                i++;
                continue;
            }

            // we will remove the block if the fall-through block is not a handler
            BasicBlock<IDInstruction> b1 = b.getOutputBlock(0);
            if(b1.irrinsize() > 0) {
                i++;
                continue;
            }

            cfg.deleteIrregularOutEdges(b);
            if(exdata != null) {
                exdata.unprotectBlock((int)b.getAddress());
            }

            cfg.deleteEdge(b, b1);

            IDInstruction newFirstInsn = b1.get(0);
            int oldOffset = (int)newFirstInsn.getOffset();
            int newOffset = (int)insn.getOffset();
            for(BasicBlock<IDInstruction> src: b1.getInputBlocks()) {
                updateTargets(src.getLast(), oldOffset, newOffset);
            }

            for(BasicBlock<IDInstruction> src: b.getInputBlocks()) {
                cfg.reconnectEdges(src, b, b1);
                cfg.removeDuplicateEdges(src, b1);
            }

            for(BasicBlock<IDInstruction> src: b.getIrregularInputBlocks()) {
                cfg.reconnectIrregularEdges(src, b, b1);
            }
            if(exdata != null) {
                exdata.moveProtectedBlock((int)b1.getAddress(), (int)b.getAddress());
            }

            newFirstInsn.setOffset(insn.getOffset());
            newFirstInsn.adjustSize(insn.getSize());

            cfg.removeBlock(b);

            cnt++;
        }

        if(cnt > 0) {
            cleanGraph();
            cfg.invalidateDataFlowAnalysis();
        }
        return cnt;
    }

    private void updateTargets(IDInstruction insn, int oldOffset, int newOffset) {
        if(insn.isJump() || insn.isJcond()) {
            int offset = insn.getBranchTarget();
            if(offset == oldOffset) {
                insn.setBranchTarget(newOffset);
            }
        }
        else if(insn.isSwitch()) {
            IDSwitchData data = insn.getSwitchData();
            for(IDTarget target: data.getTargets(false)) {
                if(target.getOffset() == oldOffset) {
                    target.setOffset(newOffset);
                }
            }
        }
    }
}
