//?type=gendec-ir
import com.pnfsoftware.jeb.core.units.code.asm.cfg.BasicBlock;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.IEAssign;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.IEGeneric;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.IEImm;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.IEMem;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.IEOperation;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.IEStatement;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.IEVar;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.OperationType;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.opt.AbstractEOptimizer;
import com.pnfsoftware.jeb.core.units.code.asm.items.INativeContinuousItem;

/**
 * This file is an IR optimizer plugin for JEB's gendec.
 * Drop this file in your JEB's coreplugins/scripts/ folder.
 * <p>
 * This optimizer is a garbage array assigment cleaner.
 * Any statement writing an immediate value to a global array
 * whose name starts with 'garbage' will be discarded.<br>
 */
public class GarbageCleaner extends AbstractEOptimizer {

	@Override
	public int perform() {
		int cnt = 0;

		for (BasicBlock<IEStatement> b : cfg) {
			for (int i = 0; i < b.size(); i++) {
				IEStatement stm = b.get(i);
				if (stm instanceof IEAssign && stm.asAssign().getDstOperand() instanceof IEMem
						&& stm.asAssign().getSrcOperand() instanceof IEImm) {
					IEMem dst = stm.asAssign().getDstOperand().asMem();
					IEGeneric e = dst.getReference();
					// [xxx + offset] = immediate
					if (e.isOperation(OperationType.ADD)) {
						IEOperation op = e.asOperation();
						if (op.getOperand1().isVar() && op.getOperand2().isImm()) {
							IEVar v = op.getOperand1().asVar();
							IEImm off = op.getOperand2().asImm();
							if (v.isGlobalReference()) {
								long addr = v.getAddress();
								INativeContinuousItem item = ectx.getNativeContext().getNativeItemAt(addr);
								// logger.info("FOUND ITEM %s", item.getName());
								if (item != null && item.getName().startsWith("garbage")) {
									long itemsize = item.getMemorySize();
									if (off.canReadAsLong() && off.getValueAsLong() + dst.getBitsize() / 8 < itemsize) {
										logger.info("FOUND GARBAGE CODE");
										b.set(i, ectx.createNop(stm));
										cnt++;
									}
								}
							}
						}
					}
				}
			}
		}

		if (cnt > 0) {
			cfg.invalidateDataFlowAnalysis();
		}
		return cnt;
	}

}
