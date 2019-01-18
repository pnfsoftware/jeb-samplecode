package com.pnf.pdfscan;

import java.io.File;
import java.util.List;

import org.apache.commons.configuration2.PropertiesConfiguration;

import com.pnf.jebauto.AutoClient;
import com.pnf.jebauto.AutoUtil;
import com.pnfsoftware.jeb.core.Artifact;
import com.pnfsoftware.jeb.core.ICoreContext;
import com.pnfsoftware.jeb.core.IEnginesContext;
import com.pnfsoftware.jeb.core.ILiveArtifact;
import com.pnfsoftware.jeb.core.IRuntimeProject;
import com.pnfsoftware.jeb.core.JebCoreService;
import com.pnfsoftware.jeb.core.dao.IDataProvider;
import com.pnfsoftware.jeb.core.dao.IFileDatabase;
import com.pnfsoftware.jeb.core.dao.IFileStore;
import com.pnfsoftware.jeb.core.dao.impl.DataProvider;
import com.pnfsoftware.jeb.core.dao.impl.JEB2FileDatabase;
import com.pnfsoftware.jeb.core.dao.impl.SimpleFSFileStore;
import com.pnfsoftware.jeb.core.input.FileInput;
import com.pnfsoftware.jeb.core.output.text.ITextDocument;
import com.pnfsoftware.jeb.core.output.text.TextDocumentUtil;
import com.pnfsoftware.jeb.core.properties.IConfiguration;
import com.pnfsoftware.jeb.core.properties.impl.CommonsConfigurationWrapper;
import com.pnfsoftware.jeb.core.units.IUnit;
import com.pnfsoftware.jeb.core.units.IUnitNotification;
import com.pnfsoftware.jeb.core.units.UnitUtil;
import com.pnfsoftware.jeb.core.units.WellKnownUnitTypes;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * A PDF file scanner using the JEB2 PDF module.
 * <p>
 * This sample class shows the structure of a simple headless clients that scans PDF files, examines
 * the PDF units, assess the notifications reported by the PDF module, and makes a determination as
 * whether or not the PDF module is suspicious / potentially malicious. There is much more that
 * could be done, such as: complex heuristics (ex: corrupt records), examining sub-units (ex:
 * JavaScript doc) and determine their own suspicion level, etc. but it is beyond the scope of this
 * sample script.
 * <p>
 * Note: the heuristic used in this example is trivial: we are looking for X notifications having a
 * minimum suspicion level of Y. By default, (X, Y) is set to (2, 70).
 * 
 */
public class PDFScanner {
    static final ILogger logger = GlobalLog.getLogger(AutoClient.class);
    static {
        // disabled to avoid JEB log interferences
        // GlobalLog.addDestinationStream(System.out);
    }

    private static String jebEnginesCfg;
    private static String licenseKey;
    static {
        jebEnginesCfg = System.getProperty("jeb.engcfg");
        licenseKey = System.getProperty("jeb.lickey");
    }

    public static void main(String[] argv) throws Exception {
        if(jebEnginesCfg == null || licenseKey == null) {
            System.out.format("Please set the jeb.engcfg and jeb.lickey properties before executing this program.\n");
            System.exit(-1);
        }

        if(argv.length <= 0) {
            System.out.format("PDF scanner using JEB2 Business/Enterprise -- PNF Software (c) 2015\n");
            System.out.format("Usage:\n");
            System.out
                    .format("  [java] PDFScanner -Djeb.engcfg=<enginesCfgPath> -Djeb.lickey=<licenseKey> <location>\n");
            System.exit(-1);
        }

        System.out.format("Scanning files...\n");

        List<File> files = AutoUtil.retrieveFiles(argv[0]);
        long t0 = System.currentTimeMillis();

        // simple heuristic (see javadoc)
        PDFScanner scanner = new PDFScanner(2, 70);
        scanner.scanFiles(files);

        System.out.format("\nScanned %d files (%d suspicious) in %ds\n", scanner.getScannedCount(),
                scanner.getSuspiciousCount(), (System.currentTimeMillis() - t0) / 1000);
    }

    private int thDangerCount;
    private int thDangerLevel;

    private int cntScanned;
    private int cntSuspicious;

    private boolean dumpJS = false;

    public PDFScanner(int thDangerCount, int thDangerLevel) {
        this.thDangerCount = thDangerCount;
        this.thDangerLevel = thDangerLevel;
    }

    public void scanFiles(List<File> files) throws Exception {
        // create or retrieve a core context (engines container)
        ICoreContext core = JebCoreService.getInstance(licenseKey);

        // create an engines context (project container)
        String baseDir = System.getProperty("user.home");
        IFileDatabase projectdb = new JEB2FileDatabase(baseDir);
        IFileStore filestore = new SimpleFSFileStore(baseDir);
        IFileStore pluginstore = null;
        PropertiesConfiguration enginesConfig = AutoUtil.createPropertiesConfiguration(jebEnginesCfg);
        IConfiguration enginesConfigWrapper = new CommonsConfigurationWrapper(enginesConfig);
        Object o = enginesConfigWrapper.getProperty(".PluginsFolder");
        if(o == null) {
            System.out.format("Your JEB engines configuration must contain a \".PluginsFolder\""
                    + " property pointing to your JEB2 back-end plugins.\nTypically, "
                    + "this is the \"coreplugins/\" folder within your installation directory.\n");
            System.exit(-1);
        }

        IDataProvider dataProvider = new DataProvider(null, projectdb, filestore, pluginstore, null,
                enginesConfigWrapper);

        // engines context
        IEnginesContext engctx = core.createEnginesContext(dataProvider, null);

        for(File file: files) {
            System.out.format("\nFile %d/%d : %s ...\n", cntScanned + 1, files.size(), file.getName());

            // create or load a project (artifact container)
            IRuntimeProject prj = engctx.loadProject("ProjectTest" + cntScanned);

            // process the artifact, get units
            try {
                ILiveArtifact art = prj.processArtifact(new Artifact(file.getName(), new FileInput(file)));
                cntScanned++;

                // we check top-level units only (this is a demo file)
                // if the files were within a zip archive, JEB will process the archive, and PDF units should be at level 2
                List<IUnit> units = art.getUnits();
                for(IUnit unit: units) {
                    if(unit.getFormatType().equals(WellKnownUnitTypes.typePdf)) {
                        if(assessPdf(file, unit)) {
                            System.out.format("=> +++ SUSPICIOUS PDF FILE +++\n");
                            cntSuspicious++;
                        }
                    }

                    // ENABLE TO TRY: search and dump all extracted JS blobs
                    if(dumpJS) {
                        List<IUnit> jsUnits = UnitUtil.findDescendantsByFormatType(unit, "Javascript");
                        System.out.format("*** %s ***\n", jsUnits);
                        for(IUnit jsUnit: jsUnits) {
                            ITextDocument textDoc = (ITextDocument)jsUnit.getFormatter().getPresentation(0)
                                    .getDocument();
                            String js = TextDocumentUtil.buildText(textDoc).toString();
                            System.out.format("Javascript:\n %s \n", js);
                        }
                    }
                }

                engctx.unloadProject(prj.getKey());
            }
            catch(Exception e) {
                System.out.println();
            }
        }

        JebCoreService.getInstance().closeEnginesContext(engctx);
    }

    public int getScannedCount() {
        return cntScanned;
    }

    public int getSuspiciousCount() {
        return cntSuspicious;
    }

    private boolean assessPdf(File file, IUnit unit) {
        int dangerCount = 0;
        List<? extends IUnitNotification> notifications = unit.getNotificationManager().getNotifications();
        for(IUnitNotification n: notifications) {
            // suspicion level of a notification is in [0, 100]
            int level = n.getType().getLevel();
            System.out.format("- %d (%s): %s @ %s\n", level, n.getType().getDescription(), n.getDescription(),
                    n.getAddress());
            if(level >= thDangerLevel) {
                dangerCount++;
            }
        }
        return dangerCount >= thDangerCount;
    }
}
