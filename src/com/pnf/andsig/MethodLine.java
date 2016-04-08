/*
 * JEB Copyright PNF Software, Inc.
 * 
 *     https://www.pnfsoftware.com
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.pnf.andsig;

import com.pnfsoftware.jeb.util.Conversion;

/**
 * 
 * 
 * @author Nicolas Falliere
 *
 */
public class MethodLine {
    String cname;
    String mname;
    String shorty;
    int opcount;
    String mhash;

    static MethodLine parse(String line) {
        String[] tokens = line.trim().split(",");
        if(tokens.length != 5) {
            return null;
        }

        MethodLine ml = new MethodLine();
        ml.cname = tokens[0];
        if(!ml.cname.startsWith("L") || !ml.cname.endsWith(";")) {
            return null;
        }

        ml.mname = tokens[1];
        if(ml.mname.isEmpty()) {
            return null;
        }

        ml.shorty = tokens[2];
        if(ml.shorty.isEmpty()) {
            return null;
        }

        ml.opcount = Conversion.stringToInt(tokens[3]);
        if(ml.opcount <= 0) {
            return null;
        }

        ml.mhash = tokens[4];
        if(ml.mhash.length() != 64) {
            return null;
        }

        return ml;
    }

    @Override
    public String toString() {
        return String.format("%s,%s,%s,%d,%s", cname, mname, shorty, opcount, mhash);
    }
}
