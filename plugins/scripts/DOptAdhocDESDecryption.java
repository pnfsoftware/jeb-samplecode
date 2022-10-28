import java.util.List;

import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.DESKeySpec;
import javax.crypto.spec.IvParameterSpec;

import com.pnfsoftware.jeb.core.units.code.android.ir.AbstractDOptimizer;
import com.pnfsoftware.jeb.core.units.code.android.ir.DOptimizerType;
import com.pnfsoftware.jeb.core.units.code.android.ir.DexDecEvaluationException;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDImm;
import com.pnfsoftware.jeb.core.units.code.android.ir.IDState;
import com.pnfsoftware.jeb.util.base.Wrapper;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Decryption helper for e4596c10ea8168ea00bf2f91398e441eb6f7090eab7e49913b175527726c2513
 *
 * @author Nicolas Falliere
 *
 */
public class DOptAdhocDESDecryption extends AbstractDOptimizer {

    public DOptAdhocDESDecryption() {
        super(DOptimizerType.UNSAFE);
        setPriority(10);  // run this early on
    }

    @Override
    public int perform() {
        String appsig = "Lllll/llll/llll/lllll;";
        if(dex.getClass(appsig) == null) {
            // not the app we are targetting
            return 0;
        }

        // refer to methods in Lllll/llll/llll/lllll;
        String key = "KbMMxfM,";
        String fsig_keySpec = "Lllll/llll/llll/lllll;->keySpec:Ljavax/crypto/spec/DESKeySpec;";
        String fsig_secretKey = "Lllll/llll/llll/lllll;->secretKey:Ljavax/crypto/SecretKey;";
        String fsig_iv = "Lllll/llll/llll/lllll;->iv:Ljavax/crypto/spec/IvParameterSpec;";

        IDState state = g.getEmulator();
        try {
            IDImm keySpec0 = state.getStaticField(fsig_keySpec);
            if(!keySpec0.isNullRef()) {
                // already initialized!
                return 0;
            }

            DESKeySpec keySpec;
            SecretKey secretKey;
            IvParameterSpec iv;
            try {
                keySpec = new DESKeySpec(key.getBytes("UTF-8"));
                secretKey = SecretKeyFactory.getInstance("DES").generateSecret(keySpec);
                iv = new IvParameterSpec(key.getBytes("UTF-8"));
            }
            catch(Exception ex) {
                return 0;
            }

            state.setStaticField(fsig_keySpec, state.registerObject(keySpec));
            state.setStaticField(fsig_secretKey, state.registerObject(secretKey));
            state.setStaticField(fsig_iv, state.registerObject(iv));
            logger.trace("Fields are patched");
        }
        catch(DexDecEvaluationException e) {
            //logger.catching(e);
        }

        // this optimizer is one-off; do not report on success, there is no point in running it more than once
        return 0;
    }
}
