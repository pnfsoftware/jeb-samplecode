import java.util.LinkedHashSet;
import java.util.Set;

import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.DOptimizerType;
import com.pnfsoftware.jeb.core.units.code.android.ir.DexDecEvaluationException;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDArrayElt;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDExpression;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDImm;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDInstruction;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDOperation;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDState;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDStaticField;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDVisitor;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.IVisitResults;
import com.pnfsoftware.jeb.core.units.code.java.JavaOperatorType;

/**
 * Custom IR optimizer plugin for dexdec. Attempt to clean obfuscated code making use of static
 * array values computed during class initialization. This plugin makes us of the emulator
 * (IDState).
 * <p>
 * 
 * <pre>
 *  static {
 *      SomeClass.abc = new int[16];
 *      int val = 0x11223344;
 *      for(int i = 0; i < 16; i++) {
 *          SomeClass.abc[i] = val;
 *          val = (val * 0x11111111 ^ 0x22222222) % 0x33333333;
 *      }
 *      ...
 *  }
 *  
 *  void someFunction() {
 *      ...
 *      int v = SomeClass.abc[3];  // ==> REPLACE BY THE ACTUAL VALUE
 *      ...
 *  }
 * </pre>
 * 
 * <p>
 * This optimizer is unsafe, it should not be globally enabled, as it is assumed that all
 * detected obfuscated arrays (such as `abc` above) are:<br>
 * - initialized in their containing class static initializer (&lt;clinit&gt;)<br>
 * - not updated after their initialization (i.e. they are 'effectively' final)<br>
 *
 * @author Nicolas Falliere
 *
 */
public class DOptUnsafeArrayAccessSubst extends AbstractDOptimizer {
    int replcnt;
    int triggercnt;
    Set<String> fieldCsigs = new LinkedHashSet<>();

    public DOptUnsafeArrayAccessSubst() {
        super(DOptimizerType.UNSAFE);
    }

    @Override
    public int perform() {
        replcnt = 0;
        triggercnt = 0;
        fieldCsigs.clear();

        // filter & collector: assume the array elements are used in arithmetic operations, e.g. "array[index] OPERATION constant"
        // here, we look for two instances of "SomeClass.someArrayField[imm1] ^ imm2"
        // the input method must have at least two of those elements
        for(IDInstruction insn: cfg.instructions()) {
            insn.visitInstruction(new IDVisitor() {
                @Override
                public void process(IDExpression e, IDExpression parent, IVisitResults<IDExpression> results) {
                    if(e.isOperation() && e.asOperation().getOperator().is(JavaOperatorType.XOR)) {
                        IDOperation op = e.asOperation();
                        IDExpression e1 = op.getLeft();
                        IDExpression e2 = op.getRight();
                        if(e2.isImm() && e1.isArrayElt()) {
                            IDArrayElt elt = e1.asArrayElt();
                            if(elt.getArray().isStaticField() && elt.getIndex().isImm()) {
                                String field_csig = elt.getArray().asStaticField().getClassSignature();
                                fieldCsigs.add(field_csig);  // collect the classes containing the "obfuscated arrays"
                                triggercnt++;
                                results.interrupt(true);  // done with this instruction
                            }
                        }
                    }
                }
            }, true);
        }
        if(triggercnt < 2) {
            return 0;
        }

        // retrieve the current emulator and use it to load the classes that contain the obfuscated arrays
        IDState state = g.getEmulator();
        if(!state.canRun()) {
            return 0;
        }
        for(String csig: fieldCsigs) {
            try {
                state.loadClass(csig);
            }
            catch(DexDecEvaluationException e) {
                logger.catching(e);
                return 0;
            }
        }

        // replace the array accesses by their actual value
        for(IDInstruction insn: cfg.instructions()) {
            insn.visitInstruction(new IDVisitor() {
                @Override
                public void process(IDExpression e, IDExpression parent, IVisitResults<IDExpression> results) {
                    if(e.isArrayElt()) {
                        IDArrayElt elt = e.asArrayElt();
                        if(elt.getArray().isStaticField() && elt.getIndex().isImm()) {
                            int index = (int)elt.getIndex().asImm().getRawValue();

                            IDStaticField fld = elt.getArray().asStaticField();
                            String fsig = fld.getNativeField(g).getSignature(false);

                            try {
                                IDImm _array = state.getStaticField(fsig);
                                IDImm repl = state.getArrayElement(_array, index);
                                if(!repl.isRef()) {
                                    if(parent.replaceSubExpression(e, repl)) {
                                        results.setReplacedNode(repl);
                                        replcnt++;
                                    }
                                }
                            }
                            catch(DexDecEvaluationException e1) {
                                results.interrupt(false);
                            }
                        }
                    }
                }
            }, true);
        }

        if(replcnt == 0) {
            return 0;
        }
        // note: no need for cfg.resetDFA(), no IDVar was touched

        return replcnt;
    }
}
