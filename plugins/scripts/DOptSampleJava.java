import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;

/**
 * A sample IR optimizer.
 * 
 * @author Nicolas Falliere
 *
 */
public class DOptSampleJava extends AbstractDOptimizer {

    public DOptSampleJava() {
        super();
    }

    @Override
    public int perform() {
        logger.debug("The optimizer is running");
        return 0;
   }
}