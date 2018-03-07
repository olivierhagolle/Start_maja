#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import os.path
import sys
from start_maja import start_maja, OptionParser

#========== Paramètres
if len(sys.argv) == 1:
	prog = os.path.basename(sys.argv[0])
	print '      '+sys.argv[0]+' [options]' 
	print "     Aide : ", prog, " --help"
	print "        ou : ", prog, " -h"

	print "exemple : "
	print "\t python %s -c nominal -t 40KCB -s Reunion -d 20160401 "%sys.argv[0]
     
	sys.exit(-1)  
else:
	usage = "usage: %prog [options] "
	parser = OptionParser(usage=usage)
	
	parser.add_option("-c", "--context", dest="context", action="store", \
			help="name of the test directory", type="string", default='nominal')

        parser.add_option("-t", "--tile", dest="tile", action="store", \
			help="tile number", type="string",default='31TFJ')

        parser.add_option("-s", "--site", dest="site", action="store", \
			help="site name", type="string",default='Arles')

        parser.add_option("-o", "--orbit", dest="orbit", action="store", \
			  help="orbit number", type="string",default=None)

        
        parser.add_option("-d", "--startDate", dest="startDate", action="store", \
			  help="start date for processing (optional)", type="string",default="20150623")

        (options, args) = parser.parse_args()

tuile=options.tile
site=options.site
orbite=options.orbit
contexte=options.context
nb_backward=6

#=================directories
repCode="/mnt/data/home/hagolleo/PROG/S2/lance_maja"
repConf=repCode+"/userconf"
repDtm =repCode+"/DTM"
repGipp=repCode+"/GIPP_%s"%contexte

repTrav= "/mnt/data/SENTINEL2/MAJA/%s/%s/%s/"%(site,tuile,contexte)
repL1  = "/mnt/data/SENTINEL2/L1C_PDGS/%s/"%site
repL2  = "/mnt/data/SENTINEL2/L2A_MAJA/%s/%s/%s/"%(site,tuile,contexte)

maja  = "/mnt/data/home/petruccib/Install-MAJA/maja/core/1.0/bin/maja"

folders_file = os.path.join(repTrav, "folders.txt")
if not os.path.isfile(folders_file):
    with open(folders_file, "w") as f:
        print >> f, "repCode={}".format(repCode)
        print >> f, "repWork={}".format(repTrav)
        print >> f, "repL1={}".format(repL1)
        print >> f, "repL2={}".format(repL2)
        print >> f, "repMaja={}".format(maja)

start_maja(folders_file, contexte, site, tuile, orbite, nb_backward)
