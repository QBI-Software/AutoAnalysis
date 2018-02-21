import logging
import threading
from glob import iglob
from logging.handlers import RotatingFileHandler
from multiprocessing import freeze_support, Pool
from os import access, R_OK, mkdir
from os.path import join, dirname, exists, split, splitext, expanduser
from autoanalysis.db.dbquery import DBI
import matplotlib.pyplot as plt
import wx
import yaml
import importlib
from configobj import ConfigObj


# Required for dist
freeze_support()
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()
EVT_DATA_ID = wx.NewId()
#global logger
logger = logging.getLogger()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


def EVT_DATA(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_DATA_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class DataEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DATA_ID)
        self.data = data


def CheckFilenames(filenames, configfiles):
    """
    Check that filenames are appropriate for the script required
    :param filenames: list of full path filenames
    :param configfiles: matching filename for script as in config
    :return: filtered list
    """
    newfiles = []
    for conf in configfiles:
        for f in filenames:
            parts = split(f)
            if conf in parts[1]:
                newfiles.append(f)
            else:
                # extract directory and seek files
                newfiles = newfiles + [y for y in iglob(join(parts[0], '**', conf), recursive=True)]
    return newfiles


########################################################################

lock = threading.Lock()
event = threading.Event()
hevent = threading.Event()

class TestThread(threading.Thread):
    def __init__(self, controller, filenames, outputdir, output, processname, module,classname, config):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.controller = controller
        self.filenames = filenames
        self.output = output
        self.processname = processname
        self.module_name = module
        self.class_name = classname
        self.outputdir = outputdir
        self.config = config

    def run(self):
        i = 0
        try:
            event.set()
            lock.acquire(True)
            # Do work
            q = dict()
            files = self.filenames
            total_files = len(files)

            # Loop through each
            for i in range(total_files):
                count = ((i + 1) * 100) / total_files
                msg ="%s run: count=%d of %d (%d\%)" % (self.processname,i,total_files,count)
                print(msg)
                self.processData(files[i], q)

        except Exception as e:
            print(e)
        finally:
            print('Finished TestThread')
            # self.terminate()
            lock.release()
            event.clear()

    def processData(self, filename, q):
        """
        Activate filter process - multithreaded
        :param datafile:
        :param q:
        :return:
        """
        print("Process Data for file: ", filename)

        # create local subdir for output
        if self.output == 'local':
            outputdir = join(dirname(filename), 'processed')
            if not exists(outputdir):
                mkdir(outputdir)
        else:
            outputdir = self.outputdir
        # Instantiate module
        module = importlib.import_module(self.module_name)
        class_ = getattr(module, self.class_name)
        mod = class_(filename, outputdir, sheet=self.config['SHEET'],
                     skiprows=self.config['SKIPROWS'],
                     headers=self.config['HEADERS'])
        cfg = mod.getConfigurables()
        for c in cfg.keys():
            cfg[c] = self.controller.db.getConfigByName(self.controller.currentconfig, c)
            print("config set: ", cfg[c])
        mod.setConfigurables(cfg)
        if mod.data is not None:
            q[filename] = mod.run()
        else:
            q[filename] = None

####################################################################################################

class ProcessThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, filenames, filesin, type, row, processname, module):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.controller = controller
        self.wxObject = wxObject
        self.filenames = filenames
        self.filesIn = filesin
        self.row = row
        self.type = type
        self.processname = processname
        self.module = module
        logger = logging.getLogger(processname)
        # self.start()  # start the thread

    # ----------------------------------------------------------------------
    def run(self):
        i = 0
        try:
            event.set()
            lock.acquire(True)
            # Do work
            q = dict()
            if self.filesIn is not None:
                checkedfilenames = CheckFilenames(self.filenames, self.filesIn)
                files = [f for f in checkedfilenames if self.controller.datafile in f]
            else:
                files = self.filenames
            total_files = len(files)
            logger.info("Checked by type: (%s): \nFILES LOADED:%d\n%s", self.processname, total_files,
                        "\n\t".join(files))
            for i in range(total_files):
                count = ((i + 1) * 100) / total_files
                logger.info("FilterThread.run: count= %d", count)
                wx.PostEvent(self.wxObject, ResultEvent((count, self.row, i + 1, total_files, self.processname)))
                self.processFilter(files[i], q)

            wx.PostEvent(self.wxObject, ResultEvent((100, self.row, total_files, total_files, self.processname)))
        except Exception as e:
            wx.PostEvent(self.wxObject, ResultEvent((-1, self.row, i + 1, total_files, self.processname)))
            logging.error(e)
        except KeyboardInterrupt:
            logger.warning("Keyboard interrupt in FilterThread")
            self.terminate()
        finally:
            logger.info('Finished FilterThread')
            # self.terminate()
            lock.release()
            event.clear()

    # ----------------------------------------------------------------------
    def processFilter(self, filename, q):
        """
        Activate filter process - multithreaded
        :param datafile:
        :param q:
        :return:
        """
        logger.info("Process Filter with file: %s", filename)
        datafile_msd = filename.replace(self.controller.datafile, self.controller.msdfile)
        # Check datafile_msd is accessible - can use txt instead of xls
        if not access(datafile_msd, R_OK) and '.xls' in splitext(datafile_msd)[1]:
            f1 = datafile_msd.replace(splitext(datafile_msd)[1], '.txt')
            if access(f1, R_OK):
                datafile_msd = f1
        # create local subdir for output
        outputdir = join(dirname(filename), 'processed')
        if not exists(outputdir):
            mkdir(outputdir)
        fmsd = self.module(self.controller.configfile, filename, datafile_msd, outputdir)
        if fmsd.data is not None:
            q[filename] = fmsd.runFilter()
        else:
            q[filename] = None

    # ----------------------------------------------------------------------
    def terminate(self):
        logger.info("Terminating Filter Thread")
        self.terminate()



########################################################################

class Controller():
    def __init__(self, configfile, configID,processfile):
        self.logger = self.loadLogger()
        self.processfile = processfile
        self.cmodules = self.loadProcesses()
        # connect to db
        self.db = DBI(configfile)
        self.currentconfig = configID #multiple configs possible
        self.db.getconn()

    def loadProcesses(self):
        pf = None
        try:
            pf = open(self.processfile, 'rb')
            self.processes = yaml.load(pf)
            cmodules={}
            for p in self.processes:
                msg = "Controller:LoadProcessors: loading %s=%s" % (p, self.processes[p]['caption'])
                print(msg)
                logging.info(msg)
                module_name = self.processes[p]['modulename']
                class_name = self.processes[p]['classname']
                cmodules[p] =(module_name,class_name)
            return cmodules
        except Exception as e:
            raise e
        finally:
            if pf is not None:
                pf.close()

    def loadLogger(self,outputdir=None, expt=''):
        #### LoggingConfig
        logger.setLevel(logging.INFO)
        homedir = expanduser("~")
        if outputdir is not None and access(outputdir, R_OK):
            homedir = outputdir
        if len(expt) >0:
            expt = expt + "_"
        if not access(join(homedir, "logs"), R_OK):
            mkdir(join(homedir, "logs"))
        logfile = join(homedir, "logs", expt+'analysis.log')
        handler = RotatingFileHandler(filename=logfile, maxBytes=10000000, backupCount=10)
        formatter = logging.Formatter('[ %(asctime)s %(levelname)-4s ] (%(threadName)-9s) %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    # ----------------------------------------------------------------------
    # def loadConfig(self, config=None):
    #     """
    #     Load from config file or config object
    #     :param config:
    #     :return:
    #     """
    #     try:
    #         if config is not None and isinstance(config, ConfigObj):
    #             logger.info("Loading config obj:%s", config.filename)
    #         elif isinstance(config, str) and access(config, R_OK):
    #             logger.info("Loading config from file:%s", config)
    #             config = ConfigObj(config)
    #         else:
    #             logger.warning('No config file found')
    #             config = ConfigObj()
    #
    #     except IOError as e:
    #         logging.error(e)
    #     except ValueError as e:
    #         logging.error(e)
    #
    #     return config

    # ----------------------------------------------------------------------
    def RunCompare(self, wxGui, indirs, outputdir, prefixes, searchtext):
        """
        Comparison of groups
        :param wxGui:
        :param indirs:
        :param outputdir:
        :param prefixes:
        :param searchtext:
        :return:
        """
        pass


    # ----------------------------------------------------------------------
    def RunProcess(self, wxGui, process,outputdir,filenames, i,  expt, row, showplots=False):
        """
        Instantiate Thread with type for Process
        :param wxGui:
        :param filenames:
        :param type:
        :param row:
        :return:
        """
        type = self.processes[i]['href']
        processname = self.processes[i]['caption']
        filesIn = []
        for f in self.processes[i]['files'].split(", "):
            fin = self.db.getConfigByName(self.currentconfig,f)
            if fin is not None:
                filesIn.append(fin)
            else:
                filesIn.append(f)

        logger.info("Running Threads - start: %s (Expt prefix: %s) [row: %d]", type, expt, row)
        wx.PostEvent(wxGui, ResultEvent((0, row, 0, len(filenames), processname)))

        t = ProcessThread(self, wxGui, self.cmodules[i],outputdir, filenames, filesIn, type, row, processname, showplots )
        t.start()

        logger.info("Running Thread - loaded: %s", type)

    # ----------------------------------------------------------------------


    def shutdown(self):
        logger.info('Close extra thread')
        t = threading.current_thread()
        #print("Thread counter:", threading.main_thread())
        if t != threading.main_thread() and t.is_alive():
            logger.info('Shutdown: closing %s', t.getName())
            t.terminate()
