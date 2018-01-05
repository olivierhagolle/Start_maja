<img  title="logo CNES" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2015/11/logo_cnes.jpg" alt="" width="130"  /> <img  title="logo CESBIO" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2015/11/logo_cesbio.png" alt="" width="110"  /> <img  title="logo DLR" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2015/11/logo_DLR.jpg" alt="" width="90"  /> <img  title="logo MAJA" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2015/11/logo_maja.png" alt="" width="80"  /> 
# Introduction

MAJA stands for Maccs-Atcor Joint Algorithm. This atmospheric correction and cloud screening software is based [on MACCS processor](http://www.cesbio.ups-tlse.fr/multitemp/?p=6203), developped for CNES by CS-SI company, from a method and a prototype developped at CESBIO, <sup>[1](#ref1)</sup> <sup>[2](#ref2)</sup> <sup>[3](#ref3)</sup>. Recently, thanks to an agreement between CNES and DLR and to some funding from ESA, we started adding methods from DLR 's atmospheric correction software ATCOR into MACCS. MACCS then became MAJA. The current distributed version is the first version resulting from this collaboration : MAJA V1-0. 

MAJA has a very unique feature among all atmospheric correction processors : it uses multi-temporal criteria to improve cloud detection and aerosol retrieval. Because of this feature, it is important to use MAJA to process *time series* of images and not single images. Moreover, these images have to be processed chronologically. To initialise processing of a time series, a special mode is used, named "backward mode". To get a correct first product, we process in fact a small number of products in anti-chronological order (default value of number of images processed in backward mode is 8, but consider increasing it if your region is very cloudy). Then all the products are processed in "nominal" mode and chronological order. When a product is fully or nearly fully cloudy, it is not issued to save processing time and disk space.

For more information about MAJA methods but without details, please read : http://www.cesbio.ups-tlse.fr/multitemp/?p=6203
To get all details on the methods, MAJA's ATBD is available here : http://tully.ups-tlse.fr/olivier/maja_atbd/blob/master/atbd_maja.pdf

Following discovery of errors in previous version, we went through all the files and found other updates to make. If most files have been updated, differences in the results are quite small (<0.001 in reflectance) compared to results obtained from version 0.9.

We have also set-up [an internal repository](http://tully.ups-tlse.fr/olivier/gipp/tree/master) containing parameters for all sensors actually processed by MAJA, includng Venµs and LANDSAT 8. This repository will be updated more frequently. 

## What's new in version of (v0.9 2017/10/02)
- this version of start_maja works with both S2A and S2B
- we have found errors, especially regarding water vapour, in the parameters we provided in the "GIPP_nominal" folder. These parameters have been removed and we strongly advise you to do the same.
- we have updated the parameters and provided them for both S2A and S2B in the folder GIPP_S2AS2B


## Data format 
MAJA's native output data format is explained in the document "user, installation and operating manual ([MU] SETG-MU-MAJA-010-CS.pdf)", in the document folder downloaded with MAJA). A simplified explanation of the format is provided here: http://www.cesbio.ups-tlse.fr/multitemp/?page_id=10464

<a href="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2017/05/20160406.png"><img  title="Ambaro Bay, Madagascar" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2017/05/20160406-300x300.png" alt="" width="300" height="300" align="middle"  /></a>

# Content

1. [Test maja with the test data set](#test)
2. [Use a basic supervisor for MAJA processor](#Basic)
3. [Example workflow](#workflow)
4. [Docker](#docker)

<a name="test"></a>
# Test maja with the test data set
## Get MAJA Sofware
MAJA can be downloaded as a binary code from https://logiciels.cnes.fr/en/content/maja
It is provided as a binary code and compiled for *Linux Red Hat and CentOS versions 6 and 7 only*. Its licence prevents commercial use of the code. For a licence allowing commercial use, please contact CNES (Olivier Hagolle).

## install MAJA
This is explained in the documentation provided with MAJA software.

## Test MAJA with a test data_set
We provide a test data set, to verify your installation of MAJA. Please download the following pacakge and follow the provided documentation.

### Test Data set
http://osr-cesbio.ups-tlse.fr/echangeswww/majadata/S2_NOMINAL.tgz

### Test Documentation
http://osr-cesbio.ups-tlse.fr/echangeswww/majadata/S2_NOMINAL-dataset-description.docx
<a name="Basic"></a>

### Run the tests 

Run the tests as mentionned in the test documentation. If sucessful, go to the next step.

# Basic Supervisor for MAJA processor

The basic supervisor **start_maja** enables to process successively all files in a time series of Sentinel-2 images for a given tile, stored in a folder. The initialisation of the time series is performed with the "backward mode", and then all the dates are processed in "nominal" mode. The backward mode takes much more time than the nominal mode. On my computer, which is a fast one, the nominal mode takes 15 minutes, backward mode takes almost one hour. No control is done on the outputs, and it does not check if the time elapsed between two successive products is not too long and would require restarting the initialisation in backward mode.

To use this tool, you will need to configure the directories within the folder.txt file.

## Download Sentinel-2 data :
The use of peps_download.py to download Sentinel-2 l1c PRODUCTS is recommended :
https://github.com/olivierhagolle/peps_download

## Parameters
The tool needs a lot of configuration files which are provided in two directories "userconf" and "GIPP_S2AS2B". I tend to never change the "userconf", but the GIPP_S2AS2B contains the parameters and look-up tables, which you might want to change. Most of the parameters lie within the L2COMM file. When I want to test different sets of parameters, I create a new GIPP folder, which I name GIPP_context, where *context* is passed as a parameter of the command line with option -c 

## DTM
A DTM folder is needed to process data with MAJA. Of course, it depends on the tile you want to process. This DTM must be stored in the DTM folder, which is defined within the code. A tool exists to create this DTM, it is available here : http://tully.ups-tlse.fr/olivier/prepare_mnt

An example of DTM file is available here for tile 31TFJ in Provence, France, near Avignon. Both files should be placed in a folder named DTM/S2__TEST_AUX_REFDE2_T31TFJ_0001 in the start_maja directory.


http://osr-cesbio.ups-tlse.fr/echangeswww/majadata//S2__TEST_AUX_REFDE2_T31TFJ_0001.DBL

http://osr-cesbio.ups-tlse.fr/echangeswww/majadata//S2__TEST_AUX_REFDE2_T31TFJ_0001.HDR

The DBL file is a tar file (I am innocent for this choice...) that can be opened with `tar xvf `. MAJA can use both the archive or un-archived version. My tool above does not provide the archived version.

<a name="workflow"></a>
# Example workflow

Here is how to process a set of data above tile 31TFJ, near Avignon in Provence, France. To process any other tile, you will need to prepare the DTM and store the data in the DTM folder.

## Install

- Install MAJA

- Clone the current repository
`git clone https://github.com/olivierhagolle/Start_maja`




## Retrieve Sentinel-2 L1C data.
- For instance, with peps_download.py (you need to have registered at https://peps.cnes.fr and store the account and password in peps.txt file.

`python ./peps_download.py -c S2ST -l 'Avignon' -a peps.txt -d 2017-01-01 -f 2017-04-01 -w "/path/to/L1C_DATA/Avignon`

- Unzip the LIC files in /path/to/L1C_DATA/Avignon

## Create DTM
Follow DTM generation instructions : http://tully.ups-tlse.fr/olivier/prepare_mnt

## Execute MAJA

- To use the start_maja script, you need to configure the directories, within the folder.txt file.
Here is my own configuration, also provided in the folders.txt file in this repository.
```
repCode=/mnt/data/home/hagolleo/PROG/S2/lance_maja
repWork=/mnt/data/SENTINEL2/MAJA
repL1  =/mnt/data/SENTINEL2/L1C_PDGS
repL2  =/mnt/data/SENTINEL2/L2A_MAJA
repMaja=/mnt/data/home/petruccib/Install-MAJA/maja/core/1.0/bin/maja
```
- repCode is where Start_maja.py is stored, together with the DTM, userconf and GIPP directories
- repWork is a directory to store the temporary files
- repL1 is where to find the L1C data (without the site name which is added aferward)
  - Les produits SAFE doivent donc être stockés à l'emplacement suivant : repL1  = repL1/site
- repL2 is for the L2A data (without the site name which is added aferward)
- repMAJA is where the Maja binary code is




Here is an example of command line
```
Usage   : python ./start_maja.py -f <folder_file>-c <context> -t <tile name> -s <Site Name> -d <start date>
Example : python ./start_maja.py -f folders.txt -c MAJA_1_0_S2AS2B_NATIF -t 31TFJ -s Avignon -d 20170101
```

Caution, *when a product has more than 90% of clouds, the L2A is not issued*. However, a folder with _NOTVALD_ is created.

## Known Errors

If you see this message : "ERROR 1:  Not a TIFF file, bad magic number 0 (0x0) ", donn't worry, it is just a message sent by gdal, that has no consequence. We will try to catch it in next versions...

Some Sentinel-2 L1C products lack the angle information which is required by MAJA. In this case, MAJA stops processing with an error message. This causes issues particularly in the backward mode. These products were acquired in February and March 2016 and have not been reprocessed by ESA (despited repeated asks from my side). You should remove them from the folder which contains the list of L1C products to process.


<a name="docker"></a>
# Docker

Dániel Kristóf provided us with a Dockerfile (Thank you Dániel), which, on any linux system retrieves the CentOS System, installs what is necessary and configures MAJA. I am really not a Docker expert, and when I tried, my system engineer immedialtely told me that there are some securities issues with Docker...

But if we follow Daniel's guidelines :

- First, download the test data set and store them in ~/MAJA/S2_NOMINAL
- Then configure the folders.txt file according to your configuration
- Then :
```
sudo docker build -t maja .

(or behind a proxy)
sudo docker build -t maja --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy --build-arg ftp_proxy=$ftp_proxy .
```
And then, you may run MAJA with the test data sets with
```
sudo docker run -v ~/maja/S2_NOMINAL:/data maja /opt/maja/core/1.0/bin/maja -i /data/input_maja1.0 -o /data/output_maja1.0 -m L2NOMINAL -ucs /data/userconf --TileId 36JTT

```


## References :
<a name="ref1">1</a>: A multi-temporal method for cloud detection, applied to FORMOSAT-2, VENµS, LANDSAT and SENTINEL-2 images, O Hagolle, M Huc, D. Villa Pascual, G Dedieu, Remote Sensing of Environment 114 (8), 1747-1755

<a name="ref2">2</a>: Correction of aerosol effects on multi-temporal images acquired with constant viewing angles: Application to Formosat-2 images, O Hagolle, G Dedieu, B Mougenot, V Debaecker, B Duchemin, A Meygret, Remote Sensing of Environment 112 (4), 1689-1701

<a name="ref3">3</a>: A Multi-Temporal and Multi-Spectral Method to Estimate Aerosol Optical Thickness over Land, for the Atmospheric Correction of FormoSat-2, LandSat, VENμS and Sentinel-2 Images, O Hagolle, M Huc, D Villa Pascual, G Dedieu, Remote Sensing 7 (3), 2668-2691


    
   

   
