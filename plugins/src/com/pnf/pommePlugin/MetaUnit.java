package com.pnf.pommePlugin;

import java.util.List;

import com.pnfsoftware.jeb.core.output.AbstractUnitRepresentation;
import com.pnfsoftware.jeb.core.output.IGenericDocument;
import com.pnfsoftware.jeb.core.output.IUnitDocumentPresentation;
import com.pnfsoftware.jeb.core.output.IUnitFormatter;
import com.pnfsoftware.jeb.core.output.UnitFormatterAdapter;
import com.pnfsoftware.jeb.core.units.AbstractUnit;
import com.pnfsoftware.jeb.core.units.code.ICodeUnit;

/*
 * 
 * */
public class MetaUnit extends AbstractUnit{

	
	private IUnitDocumentPresentation presentation_;
	
	public MetaUnit(String name, String description, IUnitDocumentPresentation presentation, ICodeUnit codeUnit) {
        super(name, description, codeUnit);
		presentation_ = presentation;
		
	}

	@Override
	public boolean process() {
		setProcessed(true);
		return true;
	}
	
	@Override
	public IUnitFormatter getFormatter() {
		UnitFormatterAdapter adapter = new UnitFormatterAdapter(new AbstractUnitRepresentation("API Use", true) {
            public IGenericDocument getDocument() {
                return presentation_.getDocument();
            }
        });
		return adapter;
	}

}
