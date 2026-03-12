//?type=gendec-ir
import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.ir.opt.AbstractEOptimizer;

/**
 * A sample gendec IR optimizer plugin.
 * 
 * @author Nicolas Falliere
 *
 */
public class EOptSampleJava extends AbstractEOptimizer {

    public EOptSampleJava() {
        super();
    }

    @Override
    public int perform() {
        logger.debug("EOptSampleJava: the optimizer is running");
        return 0;
   }
}