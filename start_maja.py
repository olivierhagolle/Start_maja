#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Processes a Sentinel-2 time series for a tile using MAJA processor for atmospheric correction and cloud screening.

MAJA was developped by CS-SI, under a CNES contract, using a multi-temporal method developped at CESBIO, for the MACCS processor and including methods developped by DLR for ATCOR.

This tool, developped by O.Hagolle (CNES:CESBIO) is a very basic one to show how to use MAJA to process a time series. If anything does not go as anticipated, the tool will probably crash 
"""

import glob
import os, os.path
import shutil
import sys
import optparse

##########################################################################
class OptionParser (optparse.OptionParser):

    def check_required (self, opt):
      option = self.get_option(opt)

      # Assumes the option's 'default' is set to None!
      if getattr(self.values, option.dest) is None:
          self.error("%s option not supplied" % option)

##################################### Lecture de fichier de parametres "Mot_clé=Valeur"
def read_folders(fic_txt):
    with file(fic_txt, 'r') as f :
        for ligne in f.readlines() :
            if ligne.find('repCode')==0:
                repCode = (ligne.split('=')[1]).strip()
            if ligne.find('repWork')==0:
                repWork = (ligne.split('=')[1]).strip()
            if ligne.find('repL1')==0:
                repL1   = (ligne.split('=')[1]).strip()
            if ligne.find('repL2')==0:
                repL2   = (ligne.split('=')[1]).strip()
            if ligne.find('repMaja')==0:
                repMaja = (ligne.split('=')[1]).strip()

    return(repCode,repWork,repL1,repL2,repMaja)
          
#=============== Module to copy and link files

# replace tile name in example files
def replace_tile_name(fic_in,fic_out,tile_in,tile_out):
    with file(fic_in) as f_in :
        with file(fic_out,"w") as f_out :
            lignes=f_in.readlines()
            for l in lignes:
                if l.find(tile_in)>0 :
                    l=l.replace(tile_in,tile_out)
                f_out.write(l)


def add_parameter_files(repGipp,repWorkIn,tile):
    for fic in glob.glob(repGipp+"/*"):

        base=os.path.basename(fic)
        if fic.find("36JTT")>0:
             replace_tile_name(fic,repWorkIn+'/'+base.replace("36JTT",tile),"36JTT",tile)
        else :
            os.symlink(fic,repWorkIn+'/'+base)
        

def add_DEM(repDEM,repWorkIn,tile):
    print repDEM+"/*%s*/*"%tile
    for fic in glob.glob(repDEM+"/S2_*%s*/*"%tile):
        base=os.path.basename(fic)
        os.symlink(fic,repWorkIn+base)

def add_config_files(repConf,repWorkConf):
    os.symlink(repConf,repWorkConf)


#========== command line
if len(sys.argv) == 1:
	prog = os.path.basename(sys.argv[0])
	print '      '+sys.argv[0]+' [options]' 
	print "     Aide : ", prog, " --help"
	print "        ou : ", prog, " -h"

	print "exemple : "
	print "\t python %s -f folders.txt -c nominal -t 40KCB -s Reunion  -d 20160401 "%sys.argv[0]     
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

        parser.add_option("-f", "--folder", dest="folder_file", action="store", type="string", \
			help="folder definition file",default=None)
            
        parser.add_option("-d", "--startDate", dest="startDate", action="store", \
			  help="start date for processing (optional)", type="string",default="20150623")

        (options, args) = parser.parse_args()

tile=options.tile
site=options.site
orbit=options.orbit
context=options.context
folder_file=options.folder_file

nb_backward=8 # number of images to process in backward mode

#=================directories
(repCode,repWork,repL1,repL2,maja)=read_folders(folder_file)

repConf=repCode+"/userconf"
repDtm =repCode+"/DTM"
repGipp=repCode+"/GIPP_%s"%context

repWork= "%s/%s/%s/%s/"%(repWork,site,tile,context)
if  not (os.path.exists(repWork)):
    try :
        os.makedirs(repWork)
    except :
        print "something wrong when creating %s"%repWork
        sys.exit(1)
repL1  = "%s/%s/"%(repL1,site)
repL2  = "%s/%s/%s/%s/"%(repL2,site,tile,context)

#check existence of folders
for fic in repL1,repCode,repWork,maja:
    if not (os.path.exists(fic)):
        print "ERROR : %s does not exist"%fic
        sys.exit(-1)

if not os.path.exists(repL2):
    os.makedirs(repL2)
    
    
print repL1+"/S2?_OPER_PRD_MSIL1C*_%s_*.SAFE/GRANULE/*%s*"%(orbit,tile)
if orbit!=None :
    listeProd=glob.glob(repL1+"/S2?_OPER_PRD_MSIL1C*%s_*.SAFE/GRANULE/*%s*"%(orbit,tile))
    listeProd=listeProd+glob.glob(repL1+"/S2?_MSIL1C*%s_*.SAFE/GRANULE/*%s*"%(orbit,tile))
else :
    listeProd=glob.glob(repL1+"/S2?_OPER_PRD_MSIL1C*.SAFE/GRANULE/*%s*"%(tile))
    listeProd=listeProd+glob.glob(repL1+"/S2?_MSIL1C*.SAFE/GRANULE/*%s*"%(tile))

# list of images to process
dateProd=[]
dateImg=[]
listeProdFiltree=[]
for elem in listeProd:
    rac=elem.split("/")[-3]
    elem='/'.join(elem.split("/")[0:-2])
    print elem
    rac=os.path.basename(elem)
    print rac
                   
    if rac.startswith("S2A_OPER_PRD_MSIL1C") or rac.startswith("S2B_OPER_PRD_MSIL1C") :
        date_asc=rac.split('_')[7][1:9]
    else:
        date_asc=rac.split('_')[6][0:8]
    print date_asc
    if date_asc>= options.startDate:
        dateImg.append(date_asc)
        if rac.startswith("S2A_OPER_PRD_MSIL1C") or rac.startswith("S2B_OPER_PRD_MSIL1C") :
            dateProd.append(rac.split('_')[5])
        else:
            dateProd.append(rac.split('_')[2])
        listeProdFiltree.append(elem)
        
#removing multiple images with same date and tile
 
dates_diff=list(set(dateImg))
dates_diff.sort()

prod_par_dateImg={}
nomL2_par_dateImg={}
for d in dates_diff:
    nb=dateImg.count(d)
 
    dpmax=""
    ind=-1
    #search the most recent production date
    for i in range(0,nb):
        ind=dateImg.index(d,ind+1)
        dp=dateProd[ind]
        if dp>dpmax :
            dpmax=dp

 
    #keep only the products with the most recent date
    ind=dateProd.index(dpmax)
    print dpmax, ind
    prod_par_dateImg[d]=listeProdFiltree[ind]
    nomL2_par_dateImg[d]="S2?_OPER_SSC_L2VALD_%s____%s.DBL.DIR"%(tile,d)

    print d,prod_par_dateImg[d]

print
#find the first image to process

derniereDate=""
for d in dates_diff:
    try :
        nomL2init=glob.glob("%s/%s"%(repL2,nomL2_par_dateImg[d]))[0]
        derniereDate=d
    except :
        pass


print "Most recent processed date :", derniereDate

############### For each product
nb_dates=len(dates_diff)


if not(os.path.exists(repWork)):
    os.makedirs(repWork)
if not(os.path.exists(repWork+"userconf")):
    print "create "+ repWork+"userconf"
    add_config_files(repConf,repWork+"userconf")

for i in range(nb_dates):
    d=dates_diff[i]
    if d>derniereDate:
        if os.path.exists(repWork+"/in"):            
            shutil.rmtree(repWork+"/in")
        os.makedirs(repWork+"/in")  
        #Mode Backward
        if i==0 :
            nb_prod_backward=min(len(dates_diff),nb_backward)
            for date_backward in dates_diff[0:nb_prod_backward]:
                print "#### dates à traiter", date_backward
                print prod_par_dateImg[date_backward]
                os.symlink(prod_par_dateImg[date_backward],repWork+"/in/"+os.path.basename(prod_par_dateImg[date_backward]))
            add_parameter_files(repGipp,repWork+"/in/",tile)
            add_DEM(repDtm,repWork+"/in/",tile)
 
            commande= "%s -i %s -o %s -m L2BACKWARD -ucs %s --TileId %s"%(maja,repWork+"/in",repL2,repWork+"/userconf",tile)
            print "#################################"
            print "#################################"
            print commande
            print "#################################"
            print "#################################"
            os.system(commande)
        #else mode nominal
        else :
            #Search for previous L2 product
            for PreviousDate in dates_diff[0:i]:
                nom_courant="%s/%s"%(repL2,nomL2_par_dateImg[PreviousDate])
                try :
                    print nom_courant
                    nomL2=glob.glob(nom_courant)[0]
                    print "Previous L2 names, per increasing date :",nomL2
                except :
                    print "pas de L2 pour :", nom_courant
                    pass
            print "previous L2 : ", nomL2
            os.symlink(prod_par_dateImg[d],repWork+"/in/"+os.path.basename(prod_par_dateImg[d]))
            os.symlink(nomL2,repWork+"/in/"+os.path.basename(nomL2))
            os.symlink(nomL2.replace("DBL.DIR","HDR"),repWork+"/in/"+os.path.basename(nomL2).replace("DBL.DIR","HDR"))
            os.symlink(nomL2.replace("DIR",""),repWork+"/in/"+os.path.basename(nomL2).replace("DIR",""))
                        

            add_parameter_files(repGipp,repWork+"/in/",tile)
            add_DEM(repDtm,repWork+"/in/",tile)

            commande= "%s -i %s -o %s -m L2NOMINAL -ucs %s --TileId %s"%(maja,repWork+"/in",repL2,repWork+"/userconf",tile)
            print "#################################"
            print "#################################"
            print commande
            print "#################################"
            print "#################################"
            os.system(commande)

        
    

