#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Processes a Sentinel-2 time series for a tile using MAJA processor for atmospheric correction and cloud screening.

MAJA was developped by CS-SI, under a CNES contract, using a multi-temporal method developped at CESBIO, for the MACCS processor and including methods developped by DLR for ATCOR.

This tool, developped by O.Hagolle (CNES:CESBIO) is a very basic one to show how to use MAJA to process a time series. If anything does not go as anticipated, the tool will probably crash 
"""

import glob
import tempfile
import optparse
import os
import os.path
import shutil
import sys

from convert_to_exo import exocam_creation

import logging
logger = logging.getLogger('Start-Maja')
#logger.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#logger.addHandler(ch)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
START_MAJA_VERSION = 3.1

# #########################################################################
class OptionParser(optparse.OptionParser):

    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)


# #################################### Lecture de fichier de parametres "Key=Value"
def read_folders(fic_txt):

    repCode = repWork = repL1= repL2 = repMaja = repCAMS = repCAMS_raw = None

    with file(fic_txt, 'r') as f:
        for ligne in f.readlines():
            if ligne.find('repCode') == 0:
                repCode = (ligne.split('=')[1]).strip()
            if ligne.find('repWork') == 0:
                repWork = (ligne.split('=')[1]).strip()
            if ligne.find('repL1') == 0:
                repL1 = (ligne.split('=')[1]).strip()
            if ligne.find('repL2') == 0:
                repL2 = (ligne.split('=')[1]).strip()
            if ligne.find('repMaja') == 0:
                repMaja = (ligne.split('=')[1]).strip()
            if ligne.find('repCAMS') == 0:
                repCAMS = (ligne.split('=')[1]).strip()
            if ligne.find('repCAMS_raw') == 0:
                repCAMS_raw = (ligne.split('=')[1]).strip()

    missing = False

    if repCode is None:
        logger.error("repCode is missing from configuration file. Needed : repCode, repWork, repL1, repL2, repMaja")
        missing = True
    if repWork is None:
        logger.error("repWork is missing from configuration file. Needed : repCode, repWork, repL1, repL2, repMaja")
        missing = True
    if repL1 is None:
        logger.error("repL1 is missing from configuration file. Needed : repCode, repWork, repL1, repL2, repMaja")
        missing = True
    if repL2 is None:
        logger.error("repL2 is missing from configuration file. Needed : repCode, repWork, repL1, repL2, repMaja")
        missing = True
    if repMaja is None:
        logger.error("repCode is missing from configuration file. Needed : repCode, repWork, repL1, repL2, repMaja")
        missing = True
    if repCAMS is None:
        logger.debug("repCAMS is missing from configuration file. Needed : repCode, repWork, repL1, repL2, repMaja")
    if repCAMS_raw is None:
        logger.debug("repCAMS_raw is missing from configuration file. Needed : repCode, repWork, repL1, repL2, repMaja")

    if missing:
        raise Exception("Configuration file is not complete. See log file for more information.")

    directory_missing = False

    if not os.path.isdir(repCode):
        logger.error("repCode %s is missing", repCode)
        directory_missing = True
    if not os.path.isdir(repWork):
        logger.error("repWork %s is missing", repWork)
        directory_missing = True
    if not os.path.isdir(repL1):
        logger.error("repL1 %s is missing", repL1)
        directory_missing = True
    if not os.path.isdir(repL2):
        logger.error("repL2 %s is missing", repL2)
        directory_missing = True
    if not os.path.isfile(repMaja):
        logger.error("repMaja %s is missing", repMaja)
        directory_missing = True
    if repCAMS is not None and not os.path.isdir(repCAMS):
        logger.error("repCAMS %s is missing", repCAMS)
    if repCAMS_raw is not None and not os.path.isdir(repCAMS_raw):
        logger.error("repCAMS %s is missing", repCAMS_raw)

    if directory_missing:
        raise Exception("One or more directories are missing. See log file for more information.")

    return repCode, repWork, repL1, repL2, repMaja, repCAMS, repCAMS_raw


# =============== Module to copy and link files

# replace tile name in example files
def replace_tile_name(fic_in, fic_out, tile_in, tile_out):
    with file(fic_in) as f_in:
        with file(fic_out, "w") as f_out:
            lignes = f_in.readlines()
            for l in lignes:
                if l.find(tile_in) > 0:
                    l = l.replace(tile_in, tile_out)
                f_out.write(l)


def add_parameter_files(repGipp, repWorkIn, tile, repCams):

    for fic in glob.glob(repGipp + "/*"):

        base = os.path.basename(fic)
        if fic.find("36JTT") > 0:
            replace_tile_name(fic, repWorkIn + '/' + base.replace("36JTT", tile), "36JTT", tile)
        else:
            logger.debug("Linking %s to %s", fic, repWorkIn + '/' + base)
            os.symlink(fic, repWorkIn + '/' + base)

    # links for CAMS files
    if repCams is not None:
        for fic in glob.glob(os.path.join(repCams, "*")):
            base = os.path.basename(fic)
            logger.debug("Linking %s in %s", fic, repWorkIn)
            os.symlink(fic, os.path.join(repWorkIn, base))


def add_DEM(repDEM, repWorkIn, tile):
    logger.debug("%s/*%s*/*", repDEM, tile)
    for fic in glob.glob(repDEM + "/S2_*%s*/*" % tile):
        base = os.path.basename(fic)
        os.symlink(fic, repWorkIn + base)


def add_config_files(repConf, repWorkConf):
    os.symlink(repConf, repWorkConf)

def manage_rep_cams(repCams, repCamsRaw, working_dir):
    if repCamsRaw is not None:
        #convert nc to exocams
        if repCams is not None:
            logger.warning("Exo cams dir and exo cams dir all ")
        working_directory = tempfile.mkdtemp(suffix="ConvertToExo_temp", dir=working_dir)
        repCams_out = tempfile.mkdtemp(suffix="ConvertToExo_out", dir=working_dir)
        exocam_creation(repCamsRaw, out_dir=repCams_out, working_dir=working_directory)
        return repCams_out

    return repCams


def start_maja(folder_file, context, site, tile, orbit, nb_backward):
    # =================directories
    (repCode, repWork, repL1, repL2, maja, repCams, repCamsRaw) = read_folders(folder_file)

    repCams = manage_rep_cams(repCams, repCamsRaw, repWork)

    repConf = repCode + "/userconf"
    repDtm = repCode + "/DTM"
    repGipp = repCode + "/GIPP_%s" % context

    repWork = "%s/%s/%s/%s/" % (repWork, site, tile, context)
    if not (os.path.exists(repWork)):
        try:
            os.makedirs(repWork)
        except:
            logger.error("something wrong when creating %s", repWork)
            sys.exit(1)
    repL1 = "%s/%s/" % (repL1, site)
    repL2 = "%s/%s/%s/%s/" % (repL2, site, tile, context)

    # check existence of folders
    for fic in repL1, repCode, repWork, maja:
        if not (os.path.exists(fic)):
            logger.error("ERROR : %s does not exist", fic)
            sys.exit(-1)

    if not os.path.exists(repL2):
        os.makedirs(repL2)

    if orbit != None:
        listeProd = glob.glob(repL1 + "/S2?_OPER_PRD_MSIL1C*%s_*.SAFE/GRANULE/*%s*" % (orbit, tile))
        listeProd = listeProd + glob.glob(repL1 + "/S2?_MSIL1C*%s_*.SAFE/GRANULE/*%s*" % (orbit, tile))
    else:
        listeProd = glob.glob(repL1 + "/S2?_OPER_PRD_MSIL1C*.SAFE/GRANULE/*%s*" % (tile))
        listeProd = listeProd + glob.glob(repL1 + "/S2?_MSIL1C*.SAFE/GRANULE/*%s*" % (tile))

    logger.debug("Liste prod %s", listeProd)
    # list of images to process
    dateProd = []
    dateImg = []
    listeProdFiltree = []

    if len(listeProd) == 0:
        if orbit != None:
            logger.error("No L1C product found in %s or %s",
                         repL1 + "/S2?_OPER_PRD_MSIL1C*%s_*.SAFE/GRANULE/*%s*" % (orbit, tile),
                         repL1 + "/S2?_MSIL1C*%s_*.SAFE/GRANULE/*%s*" % (orbit, tile))
        else:
            logger.error("No L1C product found in %s or %s",
                         repL1 + "/S2?_OPER_PRD_MSIL1C*.SAFE/GRANULE/*%s*" % (tile),
                         repL1 + "/S2?_MSIL1C*.SAFE/GRANULE/*%s*" % (tile))
        sys.exit(-3)


    for elem in listeProd:
        rac = elem.split("/")[-3]
        elem = '/'.join(elem.split("/")[0:-2])
        logger.debug("elem: %s", elem)
        rac = os.path.basename(elem)
        logger.debug("rac: %s", rac)

        if rac.startswith("S2A_OPER_PRD_MSIL1C") or rac.startswith("S2B_OPER_PRD_MSIL1C"):
            date_asc = rac.split('_')[7][1:9]
        else:
            date_asc = rac.split('_')[6][0:8]
        logger.debug("date_asc %s %s %s/%s", date_asc, date_asc >= options.startDate, date_asc, options.startDate)
        if date_asc >= options.startDate:
            dateImg.append(date_asc)
            if rac.startswith("S2A_OPER_PRD_MSIL1C") or rac.startswith("S2B_OPER_PRD_MSIL1C"):
                dateProd.append(rac.split('_')[5])
            else:
                dateProd.append(rac.split('_')[2])
            listeProdFiltree.append(elem)

    # removing multiple images with same date and tile
    logger.debug("date img %s", dateImg)
    logger.debug("set %s", set(dateImg))

    dates_diff = list(set(dateImg))
    dates_diff.sort()

    prod_par_dateImg = {}
    nomL2_par_dateImg_Natif = {}
    nomL2_par_dateImg_MUSCATE = {}
    for d in dates_diff:
        nb = dateImg.count(d)

        dpmax = ""
        ind = -1
        # search the most recent production date
        for i in range(0, nb):
            ind = dateImg.index(d, ind + 1)
            dp = dateProd[ind]
            if dp > dpmax:
                dpmax = dp

        # keep only the products with the most recent date
        ind = dateProd.index(dpmax)
        logger.debug("date prod max %s index in list %s", dpmax, ind)
        prod_par_dateImg[d] = listeProdFiltree[ind]
        nomL2_par_dateImg_Natif[d] = "S2?_OPER_SSC_L2VALD_%s____%s.DBL.DIR" % (tile, d)
        nomL2_par_dateImg_MUSCATE[d] = "SENTINEL2?_%s-*_T%s_C_V*" % (d,tile)
        logger.debug("d %s, prod_par_dateImg[d] %s", d, prod_par_dateImg[d])

    print
    # find the first image to process

    logger.debug("dates_diff %s", dates_diff)

    derniereDate = ""
    for d in dates_diff:
        logger.debug("d %s", d)
        logger.debug("%s/%s", repL2, nomL2_par_dateImg_Natif[d])
        logger.debug("%s/%s", repL2, nomL2_par_dateImg_MUSCATE[d])
        logger.debug("glob %s", glob.glob("%s/%s" % (repL2, nomL2_par_dateImg_Natif[d])))
        logger.debug("glob %s", glob.glob("%s/%s" % (repL2, nomL2_par_dateImg_MUSCATE[d])))
        
        
        #test existence of a L2 with MAJA name convention
        nomL2init = glob.glob("%s/%s" % (repL2, nomL2_par_dateImg_Natif[d]))
        if len(nomL2init)>0:
            derniereDate = d
            L2type="Natif"
            logger.debug("Most recent processed date : %s", derniereDate)
        else:
            nomL2init = glob.glob("%s/%s" % (repL2, nomL2_par_dateImg_MUSCATE[d]))
            if len(nomL2init)>0:
                L2type="MUSCATE"
                derniereDate = d
                logger.debug("Most recent processed date : %s", derniereDate)

    

    # ############## For each product
    nb_dates = len(dates_diff)

    logger.debug("nb dates %s", nb_dates)

    if not (os.path.exists(repWork)):
        os.makedirs(repWork)
    if not (os.path.exists(repWork + "userconf")):
        logger.debug("create %s userconf %s", repWork)
        add_config_files(repConf, repWork + "userconf")

    logger.debug("derniereDate %s", derniereDate)
    for i in range(nb_dates):
        d = dates_diff[i]
        logger.debug("d %s, %s", d, d > derniereDate)
        if d > derniereDate:
            if os.path.exists(repWork + "/in"):
                shutil.rmtree(repWork + "/in")
            os.makedirs(repWork + "/in")
            # Mode Backward
            if i == 0:
                nb_prod_backward = min(len(dates_diff), nb_backward)
                for date_backward in dates_diff[0:nb_prod_backward]:
                    logger.debug("dates to process %s", date_backward)
                    logger.debug(prod_par_dateImg[date_backward])
                    os.symlink(prod_par_dateImg[date_backward],
                               repWork + "/in/" + os.path.basename(prod_par_dateImg[date_backward]))
                add_parameter_files(repGipp, repWork + "/in/", tile, repCams)
                add_DEM(repDtm, repWork + "/in/", tile)

                Maja_logfile="%s/%s.log"%(repL2,os.path.basename(prod_par_dateImg[d]))
                logger.debug(os.listdir(os.path.join(repWork, "in")))
                commande = "%s -i %s -o %s -m L2BACKWARD -ucs %s --TileId %s &> %s"% (
                    maja, repWork + "/in", repL2, repWork + "/userconf", tile,Maja_logfile)
                logger.debug("#################################")
                logger.debug("#################################")
                logger.debug(commande)
                logger.debug("#################################")
                logger.debug("Initialisation mode with backward is longer")
                logger.debug("MAJA logfile: %s", Maja_logfile)
                logger.debug("#################################")
                os.system(commande)
            # else mode nominal
            else:
                nomL2 = ""
                # Search for previous L2 product
                for PreviousDate in dates_diff[0:i]:
                    if L2type=="Natif":
                        nom_courant = "%s/%s" % (repL2, nomL2_par_dateImg_Natif[PreviousDate])
                    elif L2type=="MUSCATE":
                         nom_courant = "%s/%s" % (repL2, nomL2_par_dateImg_MUSCATE[PreviousDate])
                    try:
                        logger.debug(nom_courant)
                        nomL2 = glob.glob(nom_courant)[0]
                        logger.debug("Previous L2 names, per increasing date : %s", nomL2)
                    except:
                        logger.debug("pas de L2 pour : %s", nom_courant)
                        pass
                        logger.debug("previous L2 : %s", nomL2)
                os.symlink(prod_par_dateImg[PreviousDate],
                           repWork + "/in/" + os.path.basename(prod_par_dateImg[d]))

                if L2type=="Natif":
                    os.symlink(nomL2, repWork + "/in/" + os.path.basename(nomL2))
                    os.symlink(nomL2.replace("DBL.DIR", "HDR"),
                           repWork + "/in/" + os.path.basename(nomL2).replace("DBL.DIR", "HDR"))
                    os.symlink(nomL2.replace("DIR", ""), repWork + "/in/" + os.path.basename(nomL2).replace("DIR", ""))
                elif L2type=="MUSCATE":
                    os.symlink(nomL2, repWork + "/in/" + os.path.basename(nomL2))
                    
                Maja_logfile="%s/%s.log"%(repL2,os.path.basename(prod_par_dateImg[d]))

                add_parameter_files(repGipp, repWork + "/in/", tile, repCams)
                add_DEM(repDtm, repWork + "/in/", tile)

                logger.debug(os.listdir(os.path.join(repWork, "in")))

                commande = "%s -i %s -o %s -m L2NOMINAL -ucs %s --TileId %s &> %s" % (
                    maja, repWork + "/in", repL2, repWork + "/userconf", tile, Maja_logfile)
                logger.debug("#################################")
                logger.debug("#################################")
                logger.debug(commande)
                logger.debug("#################################")
                logger.debug("MAJA logfile: %s", Maja_logfile)
                logger.debug("#################################")
                os.system(commande)
        #check for errors in MAJA executions
        Error=False
        with open(Maja_logfile, "r") as logfile:
            for line in logfile:
                if line.find("[E]")>0:
                    print line
                    Error=True
        if Error:
            print "#######################################"
            print "Error detected, see: %s"%Maja_logfile
            print "#######################################"
            sys.exit(-1)



if __name__ == '__main__':
    # ========== command line
    if len(sys.argv) == 1:
        prog = os.path.basename(sys.argv[0])
        print '      ' + sys.argv[0] + ' [options]'
        print "     Aide : ", prog, " --help"
        print "        ou : ", prog, " -h"

        print "exemple : "
        print "\t python %s -f folders.txt -c nominal -t 40KCB -s Reunion  -d 20160401 " % sys.argv[0]
        sys.exit(-1)
    else:
        usage = "usage: %prog [options] "
        parser = OptionParser(usage=usage, version='%prog {}'.format(START_MAJA_VERSION))

        parser.add_option("-c", "--context", dest="context", action="store",
                          help="name of the test directory", type="string", default='nominal')

        parser.add_option("-t", "--tile", dest="tile", action="store",
                          help="tile number", type="string", default='31TFJ')

        parser.add_option("-s", "--site", dest="site", action="store",
                          help="site name", type="string", default='Arles')

        parser.add_option("-o", "--orbit", dest="orbit", action="store",
                          help="orbit number", type="string", default=None)

        parser.add_option("-f", "--folder", dest="folder_file", action="store", type="string",
                          help="folder definition file", default=None)

        parser.add_option("-d", "--startDate", dest="startDate", action="store",
                          help="start date for processing (optional)", type="string", default="20150623")

        (options, args) = parser.parse_args()

    logger.debug("options.stardate %s", options.startDate)

    tile = options.tile
    site = options.site
    orbit = options.orbit
    context = options.context
    folder_file = options.folder_file

    nb_backward = 8  # number of images to process in backward mode

    start_maja(folder_file, context, site, tile, orbit, nb_backward)
