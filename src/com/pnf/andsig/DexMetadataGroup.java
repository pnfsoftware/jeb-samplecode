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

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import com.pnfsoftware.jeb.core.units.MetadataGroup;
import com.pnfsoftware.jeb.core.units.MetadataGroupType;

/**
 * Metadata group with loose matching on Java FQ-name.
 * 
 * @author Nicolas Falliere
 *
 */
public class DexMetadataGroup extends MetadataGroup {
    private Map<String, Object> mmap = new HashMap<>();
    private Map<String, Object> cmap = new HashMap<>();

    public DexMetadataGroup(String name, MetadataGroupType type) {
        super(name, type);
    }

    @Override
    public Map<String, Object> getAllData() {
        return Collections.unmodifiableMap(mmap);
    }

    @Override
    public Object getData(String address) {
        int pos = address.indexOf("+");
        if(pos >= 0) {
            address = address.substring(0, pos);
        }

        Object data = mmap.get(address);
        if(data != null) {
            return data;
        }

        pos = address.indexOf("->");
        if(pos < 0) {
            return null;
        }

        String classAddress = address.substring(0, pos);
        return cmap.get(classAddress);
    }

    @Override
    public boolean setData(String methodAddress, Object data) {
        int pos = methodAddress.indexOf("->");
        if(pos < 0) {
            return false;
        }

        mmap.put(methodAddress, data);

        String classAddress = methodAddress.substring(0, pos);
        mmap.put(classAddress, data);

        return true;
    }
}
