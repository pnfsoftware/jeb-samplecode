//?type=gendec-ast
import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ast.opt.AbstractCOptimizer;

/**
 * A sample gendec AST optimizer plugin.
 * 
 * @author Nicolas Falliere
 *
 */
public class COptSampleJava extends AbstractCOptimizer {

    public COptSampleJava() {
        super();
    }

    @Override
    public int perform() {
        logger.debug("COptSampleJava: the optimizer is running");
        return 0;
   }
}