import os, argparse, tarfile, re, shutil, logging, random, time
import datetime as datetime

# Set date variables
date = datetime.datetime.utcnow().strftime("%mm_%dd_%Yy")
UTCtime = datetime.datetime.utcnow().strftime("%Hh_%Mm_%Ss")
localtime = time.localtime()
localtime_formatted = "{}h_{}m_{}s".format(
    localtime[3], localtime[4], localtime[5])

# Set up logging and specify level
logfilename="rmRegexMatches_{}_at_{}.log".format(
    date, localtime_formatted)
logging.basicConfig(filename=logfilename, level=logging.INFO)

# Opens a file using readlines() and returns a list
def tryOpenFileAsList(listfile):
    logging.debug("Loading filelist {}".format(listfile))
    try:
        with open(listfile, 'r') as filelist:
            logging.debug("Listfile {} opened successfully.".format(listfile))
            returnlist = filelist.readlines()
            return returnlist
    except Exception as e:
        logging.critical("Error opening filelist {}: {}".format(
            args['filelist'], e))
        print("Error opening filelist {}: {}".format(
            args['filelist'], e))


class clearRegex(object):
    """Clears regex matches from a file"""
    def __init__(self, args):
        super(clearRegex, self).__init__()
        self.args = args

    def clearMatch(self, infile, regex):
        logging.debug("Loading file {}.".format(infile))
        try:
            with open(infile, 'rw') as file:
                filecontents = file.read()
        except Exception as e:
            logging.critical(
                "Error loading file {}, exception: {}".format(infile, e))
            print("Error opening file {}: ".format(infile))
            print("Exception: {}".format(e))

        logging.debug("Compiling regex \"{}\".".format(regex))
        comp_regex = re.compile(regex, re.MULTILINE)
        regexmatch = comp_regex.search(filecontents)

        if regexmatch:
            logging.info("Regex match found")
            filestrip = filecontents.strip(regexmatch.group(0))
            if self.args['test']: 
                print("Regular expression matches: \n"+ regexmatch.group(0))
                print("File contents with regex match stripped: \n"
                    + filestrip)
            return filestrip
        else:
            logging.info("No matches found.")
            print("No matches found")

    def fileBackup(self, infile):
        logging.info("Creating file backup")
        outfile = "{}_OLD".format(infile)
        try:
            logging.info("Copying {} to {}.".format(infile, outfile))
            shutil.copyfile(infile, outfile)
            logging.debug("Creating {}.tar.gz".format(outfile))
            self.tarFile(outfile)

            os.remove(outfile)
            logging.debug("File {} removed.".format(outfile))
        except Exception as e:
            logging.critical("File backup failed: {}".format(e))
            print("File Backup failed: {}".format(e))

    def tarFile(self, infile):
        try:
            with tarfile.open("{}.tar.gz".format(infile), "w:gz") as tar:
                tar.add(infile)
            logging.info("Tar file {}.tar.gz created.".format(infile))
        except Exception as e:
            logging.critical("Tar file creation failed: {}".format(e))
            print("Tar file creation failed: {}".format(e))


    def stripFile(self, infile, filestrip):
        logging.info("Clearing regex pattern matches from file {}".format(
            infile))
        try:
            logging.debug("Opening file {}.".format(infile))
            with open(infile, 'w') as f:
                logging.debug("Writing file {}.".format(infile))
                f.write(filestrip)
                logging.info("File {} written.".format(infile))
                print("Regex pattern matches for {} cleared from file {}.".format(
                    regex, infile))
                logging.info("Successfully removed regex pattern matches for {} from {}".format(
                    regex, infile))
        except Exception as e:
            logging.critical("Critical ERROR writing file: {}".format(e))
            print("Critical Error writing file: {}".format(e))



if __name__ == '__main__':
    
    logging.info("Launching Regex Remover at: {}, {} local, {} UTC.".format(
        date, localtime_formatted, UTCtime)
        )
    logging.debug("Creating script parser")
    parser = argparse.ArgumentParser(
        description = "Clears files of imported regex pattern matches")

    parser.add_argument('filelist', 
        help="File of listed input filepaths/names")
    parser.add_argument('regexfilelist', 
        help="Regex file. Each Regex must be on a new line."  
        "DO NOT USE ESCAPE CHARS OR QUOTES!")
    parser.add_argument('-t', '--test', 
        help="Test regex match using random file from input filelist",
        action="store_true")
    # parser.add_argument('-v', "--verbose",
    #     help="Toggles verbose mode.",
    #     action="store_true")

    # Create args namespace, then convert to dictionary
    args=parser.parse_args()
    args=vars(args)
    if args['test']:
        print(args)

    # Init regex cleaner object
    regexclear = clearRegex(args)

    # Load regular expressions from regex file
    logging.info(
        "Loading regex's from regexfile {}.".format(args['regexfilelist']))
    regexlist = tryOpenFileAsList(args['regexfilelist'])


    logging.info(
        "Loading filelist {} for input file iteration.".format(args['filelist']))
    if args['test']:
        filelist = random.choice([tryOpenFileAsList(args['filelist'])])
        print(filelist)
    else:
        filelist = tryOpenFileAsList(args['filelist'])

    logging.debug("Begin regexclear.clearMatch loop over filelist files.")
    for infile in filelist:
        infile = infile.strip('\n')
        print("Input file: {}".format(infile))
        # Make a backup before running every regex pattern match
        regexclear.fileBackup(infile)
        for regex in regexlist:
            print("Regex: {}".format(regex))
            logging.info(
                "Running regexclear on file '{}' and regex pattern '{}'".format(
                    infile, regex))
            filestrip = regexclear.clearMatch(infile, regex)
            if filestrip and not args['test']:
                regexclear.stripFile(infile, filestrip)

    logging.debug("Creating log .tar.gz")
    regexclear.tarFile(logfilename)
    os.remove(logfilename)
    logging.info("Log file {}.tar.gz created.".format(logfilename))

