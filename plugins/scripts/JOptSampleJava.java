//?type=dexdec-ast
import com.pnfsoftware.jeb.core.Version;
import com.pnfsoftware.jeb.core.units.code.java.AbstractJOptimizer;

/**
 * A sample dexdec AST optimizer plugin. Requires JEB 4.23+.
 * 
 * @author Nicolas Falliere
 *
 */
public class JOptSampleJava extends AbstractJOptimizer {

    public JOptSampleJava() {
        super();
    }

    @Override
    public int perform() {
        //logger.debug("The Java AST optimizer is running");
        return 0;
   }
}