## Basic Supervisor for MAJA processor

MAJA stands for Maccs-Atcor Joint Algorithm. This atmospheric correction and cloud screening software is based [on MACCS processor](http://www.cesbio.ups-tlse.fr/multitemp/?p=6203), developped for CNES by CS-SI company, from a method and a prototype developped at CESBIO, <sup>[1](#ref1)</sup> <sup>[2](#ref2)</sup> <sup>[3](#ref3)</sup>. Recently, thanks to an agreement between CNES and DLR and to some funding from ESA, we started adding methods from DLR 's atmospheric correction software ATCOR into MACCS. MACCS then became MAJA. The current distributed version is the first version resulting from this collaboration : MAJA V1-0. 

MAJA has a very unique feature among all atmospheric correction processors : it uses multi-temporal criteria to improve cloud detection and aerosol retrieval. Because of this feature, it is important to use MAJA to process *time series* of images and not single images. Moreover, these images have to be processed chronogically.

The basic supervisor **start_maja** enables to process successively all files in a time series of Sentinel-2 images for a given tile, stored in a folder. The initialisation of the time series is performed with the "backward mode", and then all the dates are processed in "nominal" mode. But no control is done on the outputs, and it does not check if the time elapsed between two successive products is not too long and would require restarting the initialisation in backward mode.

repCode=/mnt/data/home/hagolleo/PROG/S2/lance_maja
repWork=/mnt/data/SENTINEL2/MAJA
repL1  =/mnt/data/SENTINEL2/L1C_PDGS
repL2  =/mnt/data/SENTINEL2/L2A_MAJA
repMaja=/mnt/data/home/petruccib/Install-MAJA/maja/core/1.0/bin/maja

To use this tool, you will need to configure the directories within the folder.txt file.

## Get MAJA Sofware
MAJA can be downloaded as a binary code from https://logiciels.cnes.fr/content/maja?language=en
It is provided as a binary code and compiled for *Linux Red Hat and CentOS versions 6 and 7 only*. Its licence prevents commercial use of the code. For a licence allowing commercial use, please contact CNES (Gérard Lassalle-Balier).

## Getting the Sentinel-2 data :
The use of peps_download.py to download Sentinel-2 l1c PRODUCTS is recommended :
https://github.com/olivierhagolle/peps_download

## Parameters
The tool needs a lot of configuration files which are provided in two directories "userconf" and "GIPP_nominal". I tend to never change the "userconf", but the GIPP_nominal contains the parameters and look-up tables, which you might want to change. Most of the parameters lie within the L2COMM file. When I want to test different sets of parameters, I create a new GIPP folder, which I name GIPP_context, where *context* is passed as a parameter of the command line with option -c 

## DTM
A DTM file is needed to process data with MAJA. Of course, it depends on the tile you want to process. This DTM must be stored in the DTM folder, which is defined within the code. A tool exists to create this DTM, it is available here : http://tully.ups-tlse.fr/olivier/prepare_mnt

I will try to find a way to provide an example DTM file for tile T31TFJ, but there are size limitations for files in github...

# Example workflow

Once you have installed maja and cloned the current repository, here is how to process a set of data above tile 31TFJ, near Avignon in Provence, France. To process any other tile, you will need to prepare the DTM and store the data in the DTM folder.

## Install

Install MAJA

Clone the current repository
`git clone https://github.com/olivierhagolle/Start_maja`

## Retrieve Sentinel-2 L1C data.
For instance, with peps_download.py (you need to have registered at https://peps.cnes.fr and store the id in a file name peps.txt

`python ./peps_download.py -c S2ST -l 'Avignon' -a peps.txt -d 2017-01-01 -f 2017-04-01 -w "/path/to/L1C_DATA/Avignon`

Unzip the LIC files in /path/to/L1C_DATA/Avignon

## Create DTM
Follow DTM generation instructions : http://tully.ups-tlse.fr/olivier/prepare_mnt

## Execute MAJA

To use the start_maja script, you need to configure the directories, within the folder.txt file.
Here is my own configuration, also provided in the folders.txt file in this repository.
```
repCode=/mnt/data/home/hagolleo/PROG/S2/lance_maja
repWork=/mnt/data/SENTINEL2/MAJA
repL1  =/mnt/data/SENTINEL2/L1C_PDGS
repL2  =/mnt/data/SENTINEL2/L2A_MAJA
repMaja=/mnt/data/home/petruccib/Install-MAJA/maja/core/1.0/bin/maja
```

Here is an example of command line
```
Usage   : python ./start_maja.py -f <folder_file>-c <context> -t <tile name> -s <Site Name> -d <start date>
Example : python ./start_maja.py -f folders.txt -c nominal -t 31TFJ -s Avignon -d 20170101
```

Caution, *When a product has more than 90% of clouds, the L2A is not issued*. However, a folder with _NOTVALD_ is created.

## Known Errors

If you see this message : "ERROR 1:  Not a TIFF file, bad magic number 0 (0x0) ", donn't worry, it is just a message sent by gdal, that has no consequence. We will try to catch it in next versions...

Some Sentinel-2 L1C products lack the angle information which is required by MAJA. In this case, MAJA stops processing with an error message. This causes issues particularly in the backward mode. These products were acquired in February and March 2016 and have not been reprocessed by ESA (despited repeated asks from my side). You should remove them from the folder which contains the list of L1C products to process.

 
## References :
<a name="ref1">1</a>: A multi-temporal method for cloud detection, applied to FORMOSAT-2, VENµS, LANDSAT and SENTINEL-2 images, O Hagolle, M Huc, D. Villa Pascual, G Dedieu, Remote Sensing of Environment 114 (8), 1747-1755

<a name="ref2">2</a>: Correction of aerosol effects on multi-temporal images acquired with constant viewing angles: Application to Formosat-2 images, O Hagolle, G Dedieu, B Mougenot, V Debaecker, B Duchemin, A Meygret, Remote Sensing of Environment 112 (4), 1689-1701

<a name="ref3">3</a>: A Multi-Temporal and Multi-Spectral Method to Estimate Aerosol Optical Thickness over Land, for the Atmospheric Correction of FormoSat-2, LandSat, VENμS and Sentinel-2 Images, O Hagolle, M Huc, D Villa Pascual, G Dedieu, Remote Sensing 7 (3), 2668-2691


    
   

   
