#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import glob
import os, os.path
import shutil

#=============== Modules de copie et liens de fichiers
def remplace_nom_tuile(fic_in,fic_out,tuile_in,tuile_out):
    with file(fic_in) as f_in :
        with file(fic_out,"w") as f_out :
            lignes=f_in.readlines()
            for l in lignes:
                if l.find(tuile_in)>0 :
                    l=l.replace(tuile_in,tuile_out)
                f_out.write(l)


def ajouter_gipp(repGipp,repTravIn,tuile):
    for fic in glob.glob(repGipp+"/*"):

        base=os.path.basename(fic)
        if fic.find("36JTT")>0:
             remplace_nom_tuile(fic,repTravIn+'/'+base.replace("36JTT",tuile),"36JTT",tuile)
        else :
            os.symlink(fic,repTravIn+'/'+base)
        

def ajouter_DTM(repMNT,repTravIn,tuile):
    print repMNT+"/*%s*/*"%tuile
    for fic in glob.glob(repMNT+"/*%s*/*"%tuile):
        print fic 
        base=os.path.basename(fic)
        os.symlink(fic,repTravIn+base)

def ajouter_conf(repConf,repTravConf):
    os.symlink(repConf,repTravConf)


#========== Paramètres 
tuile="31TFJ"
site="Arles"
orbite="R108"
contexte="nominal"
nb_backward=6

repCode="/mnt/data/home/hagolleo/PROG/S2/lance_maja"
repConf=repCode+"/userconf"
repDtm =repCode+"/DTM"
repGipp=repCode+"/GIPP"

repTrav= "/mnt/data/SENTINEL2/MAJA/%s/"%site
repL1  = "/mnt/data/SENTINEL2/L1C_PDGS/%s/"%site
repL2  = "/mnt/data/SENTINEL2/L2A_MAJA/%s/%s/%s/"%(site,tuile,contexte)

maja  = "/mnt/data/home/petruccib/Install-MAJA/maja/core/1.0/bin/maja"


if not os.path.exists(repL2):
    os.makedirs(repL2)
    
print repL1+"/*%s*.SAFE"%(orbite)
listeProd=glob.glob(repL1+"/*MSIL1C*%s*.SAFE"%(orbite))

# liste des images à traiter
dateProd=[]
dateAcq=[]
for elem in listeProd:
    print elem
    dateAcq.append(os.path.basename(elem).split('_')[7][1:9])
    dateProd.append(os.path.basename(elem).split('_')[5])

#filtrage des doublons
dates_diff=list(set(dateAcq))
dates_diff.sort()

prod_par_dateAcq={}
nomL2_par_dateAcq={}
for d in dates_diff:
    nb=dateAcq.count(d)
 
    dpmax=""
    ind=-1
    #on cherche la dernière date de production
    for i in range(0,nb):
        ind=dateAcq.index(d,ind+1)
        dp=dateProd[ind]
        if dp>dpmax :
            dpmax=dp

    ind=-1
    #on garde les produist avec la date de production la plus récente
    for i in range(0,nb):
        ind=dateAcq.index(d,ind+1) 
        if dateProd[ind]==dpmax:
            prod_par_dateAcq[d]=listeProd[ind]
            nomL2_par_dateAcq[d]="S2A_OPER_SSC_L2VALD_%s____%s.DBL.DIR"%(tuile,d)


#Recherche de la première date à traiter

derniereDate=""
for d in dates_diff:
    nomL2="%s/%s"%(repL2,nomL2_par_dateAcq[d])
    if os.path.exists(nomL2):
        derniereDate=d


print "dernière data traitee :", derniereDate

###############Boucle sur les produits
nb_dates=len(dates_diff)

if not(os.path.exists(repTrav)):
    os.makedirs(repTrav)
if not(os.path.exists(repTrav+"userconf")):
    print "creation de"+ repTrav+"userconf"
    ajouter_conf(repConf,repTrav+"userconf")

for i in range(nb_dates):
    d=dates_diff[i]
    if d>derniereDate:
        if os.path.exists(repTrav+"/in"):            
            shutil.rmtree(repTrav+"/in")
        os.makedirs(repTrav+"/in")  
        #Mode Backward
        if i==0 :
            nb_prod_backward=min(len(dates_diff),nb_backward)
            for date_backward in dates_diff[0:nb_prod_backward]:
                os.symlink(prod_par_dateAcq[date_backward],repTrav+"/in/"+os.path.basename(prod_par_dateAcq[date_backward]))
            ajouter_gipp(repGipp,repTrav+"/in/",tuile)
            ajouter_DTM(repDtm,repTrav+"/in/",tuile)
 
            commande= "%s -i %s -o %s -m L2BACKWARD -ucs %s --TileId %s"%(maja,repTrav+"/in",repL2,repTrav+"/userconf",tuile)
            print commande
            os.system(commande)
         #else mode nominal
        else :
            #recherche du L2 précédent
            for dAnterieure in dates_diff[0:i]:
                nom_courant="%s/%s"%(repL2,nomL2_par_dateAcq[dAnterieure])
                if os.path.exists(nom_courant):
                    nomL2=nom_courant
            print "precedent L2 : ", nomL2

            
            os.symlink(prod_par_dateAcq[d],repTrav+"/in/"+os.path.basename(prod_par_dateAcq[d]))
            os.symlink(nomL2,repTrav+"/in/"+os.path.basename(nomL2))
            os.symlink(nomL2.replace("DBL.DIR","HDR"),repTrav+"/in/"+os.path.basename(nomL2).replace("DBL.DIR","HDR"))
            os.symlink(nomL2.replace("DIR",""),repTrav+"/in/"+os.path.basename(nomL2).replace("DIR",""))
                        

            ajouter_gipp(repGipp,repTrav+"/in/",tuile)
            ajouter_DTM(repDtm,repTrav+"/in/",tuile)

            commande= "%s -i %s -o %s -m L2NOMINAL -ucs %s --TileId %s"%(maja,repTrav+"/in",repL2,repTrav+"/userconf",tuile)
            print commande
            os.system(commande)

        
    

