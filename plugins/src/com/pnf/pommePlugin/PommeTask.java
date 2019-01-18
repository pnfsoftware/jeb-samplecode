package com.pnf.pommePlugin;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.stream.JsonReader;
import com.pnf.pommePlugin.MetaUnit;
import com.pnfsoftware.jeb.core.events.J;
import com.pnfsoftware.jeb.core.events.JebEvent;
import com.pnfsoftware.jeb.core.output.IUnitDocumentPresentation;
import com.pnfsoftware.jeb.core.output.UnitRepresentationAdapter;
import com.pnfsoftware.jeb.core.output.tree.ITreeDocument;
import com.pnfsoftware.jeb.core.output.tree.impl.Node;
import com.pnfsoftware.jeb.core.output.tree.impl.StaticTreeDocument;
import com.pnfsoftware.jeb.core.units.INativeCodeUnit;
import com.pnfsoftware.jeb.core.units.IUnit;
import com.pnfsoftware.jeb.core.units.code.ICodeUnit;
import com.pnfsoftware.jeb.core.units.code.IInstruction;
import com.pnfsoftware.jeb.core.units.code.asm.analyzer.ICallGraphManager;
import com.pnfsoftware.jeb.core.units.code.asm.analyzer.INativeCodeAnalyzer;
import com.pnfsoftware.jeb.core.units.code.asm.analyzer.INativeCodeModel;
import com.pnfsoftware.jeb.core.units.code.asm.analyzer.IReference;
import com.pnfsoftware.jeb.core.units.code.asm.analyzer.IReferenceManager;
import com.pnfsoftware.jeb.core.units.code.asm.decompiler.INativeDecompilerUnit;
import com.pnfsoftware.jeb.core.units.code.asm.items.INativeMethodItem;
import com.pnfsoftware.jeb.core.util.DecompilerHelper;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

public class PommeTask {

	// Needed to print to JEB's console.
	private static final ILogger logger = GlobalLog.getLogger(PommeTask.class);
	// 
	private Map<String, Map<String, List<String>>> artifactsMap = new HashMap<>();
	
	private String artifactName = new String();
	
	private IUnit artifact;
	
	// Thread started by the plugin.
	PommeTask(List<ICodeUnit> codeUnits) {

		try {		

			for(int i = 0; i < codeUnits.size(); i++){

				logger.info("Creating CVEs");
				INativeCodeUnit<IInstruction> codeUnit = (INativeCodeUnit<IInstruction>) codeUnits.get(i);

				artifact = (IUnit)codeUnit.getParent();

				artifactName = artifact.getName();

				logger.info("Artifact name: %s", artifactName);

				// TODO: Make the function list config file customizable. Config file our prompt? Prompt if no config?
				String filename = "./functionList.json";

				// Importing user-configured function list.
				String[] functionList = getFunctionList(filename);

				Map<String, List<String>> functionMap = new HashMap<>();

				INativeDecompilerUnit<?> decomp = (INativeDecompilerUnit<?>) DecompilerHelper.getDecompiler(
						codeUnit);

				if (decomp == null) {

					logger.info("There is no decompiler available for code unit %s", codeUnit.toString());
					return;

				}

				// Getting functions (including imports)
				List<INativeMethodItem> methods = (List<INativeMethodItem>) codeUnit.getMethods();

				logger.info("Number of functions: %d", methods.size());

				// Getting the analyzer to get xrefs.
				INativeCodeAnalyzer<IInstruction> analyzer = codeUnit.getCodeAnalyzer();
				
				
				INativeCodeModel<IInstruction> codeModel = analyzer.getModel();
				ICallGraphManager cfgManager = codeModel.getCallGraphManager();

				IReferenceManager refManager = codeModel.getReferenceManager();
				
				
				// Finding interesting functions.
				for(int j = 0; j < methods.size(); j++){

					INativeMethodItem method = methods.get(j);

					// Checking if its one that we want to look at.
					String name = method.getName(true);
					Boolean functionFound = false;

					for (String function: functionList) {

						if (name.indexOf(function) != -1){
							functionFound = true;

						}
					}

					if (!functionFound){

						// Continue to the next function
						continue;

					}

					logger.info("Fct name is:  %s", name);

					// Converting the function's address to use it with the ref manager
					String rawAddr = method.getAddress();

					if (rawAddr == null) {

						logger.info("Function's address is null for %s", name);
						continue;

					}

					rawAddr =  rawAddr.substring(0, rawAddr.length() - 1);
					
					logger.info("rawAddr : %s", rawAddr);
					
					Long addr = Long.getLong(rawAddr, 16);
					
					Set<IReference> refs = (Set<IReference>) refManager.getReferencesToTarget(addr);
					
					logger.info("Number of refs: %d", refs.size());
					
					Set<Long> callers = cfgManager.getRoutineCallers(method);

					logger.info("Number of callers: %d for function %s", callers.size(), name);

					List<String> callersList = new ArrayList<String>();

					// Iterating though each caller of this function.
					for (Long caller: callers) {

						// Getting caller's name.
						INativeMethodItem callerFunction = codeUnit.getInternalMethod(caller, false);

						if (callerFunction == null) {
							logger.info("Function %d not found", caller);
							// Skip this function
							continue;

						}

						String functionName = callerFunction.getName(true);

						// Building signature with variable names.
						List<String> parametersNames = callerFunction.getParameterNames();

						String functionSignature = functionName + "(";

						for (String parameter: parametersNames) {

							functionSignature += parameter + ",";

						}
						if (parametersNames.size() > 0) {
							functionSignature = functionSignature.substring(0, functionSignature.length() - 1);
						}
						functionSignature += ")";

						callersList.add(functionSignature);

					}

					functionMap.put(name, callersList);
					logger.info("Adding list of function %s to the map", name);

				}
				logger.info("Adding artifact %s to the map", artifactName);
				artifactsMap.put(artifactName, functionMap);


			}
		}
		catch (NullPointerException e) {

			// FIXME: prints only the real terminal and not to JEB's console.
			e.printStackTrace();

		}
		// Adding the Map as a TableDocument to the unit.
		ITreeDocument treeDocument = createCallerTree();
		IUnitDocumentPresentation callerPresentation =  new UnitRepresentationAdapter(
				200,
				"API Use",
				false,
				treeDocument
				);

		for (int i = 0; i< codeUnits.size(); i++) {

			INativeCodeUnit<IInstruction> codeUnit = (INativeCodeUnit<IInstruction>) codeUnits.get(i);
			
			IUnit parentUnit = (IUnit)codeUnit.getParent();

			MetaUnit metaUnit = new MetaUnit("Pomme", "API Usage", callerPresentation, codeUnit);

			logger.info("Name: %s", parentUnit.getName());

			metaUnit.setParent(parentUnit);

			parentUnit.addChild(metaUnit);

			// Refreshes the unit with the new presentation
			codeUnit.notifyListeners(new JebEvent(J.UnitChange));
		}
	}

	
	/*
	 * Creates a TableDocument containing every callers of a certain function
	 * and the number of occurrences of calls in the same caller.
	 * 
	 * @param tableMap Map of the callers and its number of call occurrences.
	 * @return TableDocument that will be added as a new presentation. 
	 * */
    private ITreeDocument createCallerTree() {
    	
        List<Node> root = new ArrayList<>(); 				// Each caller has a row
        Set<String> artifactSet = artifactsMap.keySet();		// Set of each caller's name.
        Object[] artifactNames = artifactSet.toArray();	// Set to Array.
        
        
        // Create a row for each caller of the selected function.
        for (int i =0; i < artifactsMap.size(); i++) {
        	//String callerRefCount = tableMap.get(keys[i].toString()).toString();
        	
        	String artifactName = artifactNames[i].toString();
        	Node artifact = new Node(artifactName);
        	logger.info("Creating node for %s", artifact);
        	
        	Map<String, List<String>> functionsMap = artifactsMap.get(artifactName);
        	
        	Set<String> functionSet = functionsMap.keySet();	// Set of each caller's name.
            Object[] functionNames = functionSet.toArray();		// Set to Array.

        	for (int j = 0; j < functionsMap.size(); j++) {
        	
        		String functionName = functionNames[j].toString();
        		Node callers = new Node(functionName);
        		logger.info("Creating node for %s", functionName);
        		List<String> callersList = functionsMap.get(functionName);
        		
        		for (int k=0; k < callersList.size(); k++){
        			
        			String callerName = callersList.get(k);
        			callers.addChild(new Node(callerName));
        			logger.info("Creating node for %s", callerName);
        			
        		}
        		
        		artifact.addChild(callers);
        		
        	}
        	root.add(artifact);
        	
        }
        return new StaticTreeDocument(root);
        
    }
	
	
	/* Loads the config file and reads the user-defined function names.
	 * 
	 * @param filename Config file name that contains a list of the functions.
	 * @return String Array of the functions names.
	 * */
	private String[] getFunctionList(String filename) {

		try {

			// Creates a String[] from the file.
			JsonReader reader = new JsonReader(new FileReader(filename));
			Gson gson = new GsonBuilder().create();
			String[] functionList = gson.fromJson(reader, String[].class);

			for (String function: functionList) {

				logger.info("Added %s to interesting functions.", function);

			}

			return functionList;

		} catch (FileNotFoundException e) {
			
			logger.info("Config file \"%s\" not found", filename);
			e.printStackTrace();
			return null;
			
		}
	}
}