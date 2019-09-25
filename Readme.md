[![Build Status](https://travis-ci.com/petket-5/Start_maja_int.svg?branch=181205_start_maja_reprog)](https://travis-ci.com/petket-5/Start_maja_int)
[![Coverage Status](https://coveralls.io/repos/github/petket-5/Start_maja_int/badge.svg)](https://coveralls.io/github/petket-5/Start_maja_int)

<img  title="logo CNES" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2015/11/logo_cnes.jpg" alt="" width="130"  /> <img  title="logo CESBIO" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2015/11/logo_cesbio.png" alt="" width="110"  /> <img  title="logo DLR" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2015/11/logo_DLR.jpg" alt="" width="90"  /> <img  title="logo MAJA" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2015/11/logo_maja.png" alt="" width="80"  /> 


**-**

**-**

**-**

**-**
 
**============================================================**

**This repository is deprecated. Start_Maja has moved to CNES github repository**

**============================================================**

Except if you really want to use old versions, 
please use the new repository : 

**https://github.com/CNES/Start-MAJA**

**============================================================**

**-**

**-**

**-**

**-**

**-**

**-**





# Content

1. [Introduction](#intro)
2. [MAJA versions](#versions)
3. [MAJA output format](#format)
4. [Get and Install MAJA](#maja)
5. [Use start_maja](#Basic)
6. [Example workflow](#workflow)
7. [Docker](#docker)

<a href="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2017/05/20160406.png"><img  title="Ambaro Bay, Madagascar" src="http://www.cesbio.ups-tlse.fr/multitemp/wp-content/uploads/2017/05/20160406-300x300.png" alt="" width="300" height="300" align="middle"  /></a>

<a name="intro"></a>
# Introduction

**Start maja has been updated to work with MAJA 3.1. It is not compatible with MAJA 1.0. If you wish to use MAJA 1.0, please use the corresponding version of Start_Maja, and [read the corresponding readme file](https://github.com/olivierhagolle/Start_maja/tree/v1.0).** To do that, please use `git checkout Start_maja_V1`.

The following script will help you run the MAJA L2A processor on your computer, for Sentinel-2 data only so far. You can also run MAJA on [CNES PEPS collaborative ground segment](https://theia.cnes.fr) using the [maja-peps script also available on github](https://github.com/olivierhagolle/maja_peps). Using PEPS will be much easier, but is not meant for mass processing.

MAJA stands for Maccs-Atcor Joint Algorithm. This atmospheric correction and cloud screening software is based [on MACCS processor](http://www.cesbio.ups-tlse.fr/multitemp/?p=6203), developped for CNES by CS-SI company, from a method and a prototype developped at CESBIO, <sup>[1](#ref1)</sup> <sup>[2](#ref2)</sup> <sup>[3](#ref3)</sup>. In 2017, thanks to an agreement between CNES and DLR and to some funding from ESA, we started adding methods from DLR 's atmospheric correction software ATCOR into MACCS. MACCS then became MAJA. 

- The first version resulting from this collaboration was MAJA V1-0. If you are using this version, you will also need [the version v1_0 of start_maja](https://github.com/olivierhagolle/Start_maja/releases/tag/v1.0).

- A second version of MAJA, v2-1 was used in Theia, but was not distributed to users, because the version 3 was available shortly afterwards. 

- This version of start_maja.py is made to run MAJA 3.1. 

MAJA has a very unique feature among all atmospheric correction processors: it uses multi-temporal criteria to improve cloud detection and aerosol retrieval. Because of this feature, it is important to use MAJA to process *time series* of images and not single images. Moreover, these images have to be processed chronologically. To initialise processing of a time series, a special mode is used, named "backward mode". To get a correct first product, we process in fact a small number of products in anti-chronological order (default value of number of images processed in backward mode is 8, but consider increasing it if your region is very cloudy). Then all the products are processed in "nominal" mode and chronological order. When a product is fully or nearly fully cloudy, it is not issued to save processing time and disk space.

For more information about MAJA methods but without details, please read : http://www.cesbio.ups-tlse.fr/multitemp/?p=6203
To get all details on the methods, MAJA's ATBD is available here : http://tully.ups-tlse.fr/olivier/maja_atbd/blob/master/atbd_maja.pdf, or reference <sup>[1](#ref4)</sup>, below.


MAJA needs parameters, that ESA names GIPP. We have also set-up [an internal repository](http://tully.ups-tlse.fr/olivier/gipp/tree/master) containing parameters for all sensors actually processed by MAJA, including Sentinel-2, Venµs and LANDSAT 8. This repository is kept up to date with the operational processors. See also [the parameters section](#parameters) below.

<a name="versions"></a>
# Recent changes

## V3.1 (2018/07/09)
Until MAJA V3.1 there were two output formats, one for the products generated at Theia, and one for the products generated by MAJA used with standard ESA L1C products. In the future,  we will adopt the output format of Theia. However, for  this version, we provide a choise of two outputs. To choose which output format is used by MAJA, you will need to choose between two binary versions:
- the MAJA version with "Sentinel2-TM" plugin will provide the Theia format as output. [This format is described here](http://www.cesbio.ups-tlse.fr/multitemp/?page_id=8352). 

- the other version will go on with the current format, [described here](http://www.cesbio.ups-tlse.fr/multitemp/?page_id=10464)

MAJA 3.1 ships several improvements :

- the main improvement is the use of Copernicus Atmosphere Monitoring Service (CAMS) aerosol products, which are used to constrain the aerosol type in the estimates. This brings a major improvement in places where the aerosols can differ a lot from a continental model which was used so far,it might slightly degraded the reults where the aerosol model was the correct one. However, a bug on the time and mlocation interpolation of CAMS data was found, and we recommend to activate the CAMS option only when it is fixed with MAJA 3.1.2. 

- since version V2-1, MAJA also includes a correction for thin cirrus clouds and a directional effect correction used to improve the estimate of AOT when using Sentinel-2 time series coming from adjacent orbits. More information is available here: http://www.cesbio.ups-tlse.fr/multitemp/?p=13291

- depending on the executable downloaded, you can have access to the same output format as the one used by MUSCATE processing center. 

- and finally, MAJA is now provided for RedHat or Ubuntu Linux families. 

### V1.0 (2018/07/09)
We just added a tag, v1.0 to get a similar version number as the one used for MAJA. The corresponding release [can be accessed here](https://github.com/olivierhagolle/Start_maja/releases/tag/v1.0)

### v.0.9.1 (2018/03/29)
Added MAJA error catching. As a result, the processing of a whole time series stops if MAJA fails for a given date.

### v0.9 (2017/10/02)
- this version of start_maja works with both S2A and S2B
- we have found errors, especially regarding water vapour, in the parameters we provided in the "GIPP_nominal" folder. These parameters have been removed and we strongly advise you to do the same.
- we have updated the parameters and provided them for both S2A and S2B in the folder GIPP_S2AS2B

<a name="format"></a>
# Data format 
- the MAJA version with "Sentinel2-TM" plugin uses the Theia format as output. [This format is described here](http://www.cesbio.ups-tlse.fr/multitemp/?page_id=8352). 

- the other version still use the native format, [described here](http://www.cesbio.ups-tlse.fr/multitemp/?page_id=10464). We migght decide to stop support for this format in the coming versions.



<a name="maja"></a>
# Get MAJA
## Get MAJA Sofware

MAJA is provided as a binary code and should at least work on RedHat (6 ad 7), Cesnt 0S, or Ubuntu recent versions. Its licence prevents commercial use of the code. For a licence allowing commercial use, please contact CNES (Olivier Hagolle). MAJA's distribution site is https://logiciels.cnes.fr/en/content/maja. However, this venerable site is limited in size (500 MB) per software, and MAJA excutable, shipped with parameters and libraries is about 1.5 GB. As a result, we provide provisionnaly download links here. 

** MAJA is distributed with a licence that [you have to accept here](https://logiciels.cnes.fr/en/content/maja). Downloading MAJA from the links below without accepting the licence, and providing the necessary information, is therefore illegal.**

MAJA is provided under two versions depending on the format you would like to use. 

[You may download MAJA 3.1 from here if you wish to use MUSCATE format](https://mycore.core-cloud.net/index.php/s/K0wk1OA0SezjreO). The format is documented [here](http://www.cesbio.ups-tlse.fr/multitemp/?page_id=8352).

[You may download MAJA 3.1 from here if you wish to use the native format, as for MAJA 1_0](https://mycore.core-cloud.net/index.php/s/XQKQFxAJjGUtLkK). Anyway, be aware that we will probably not maintain that version in the coming years. The Native format is documented [here](http://www.cesbio.ups-tlse.fr/multitemp/?page_id=10464)



## install MAJA
This is explained in the documentation provided with MAJA software.
Some users have had issues with some missing libraries, depending on how the linux system is configured. Running the following commands, with administration rights, might help.
```
# sudo yum --disableplugin=fastestmirror -y update (if necessary)
sudo yum --disableplugin=fastestmirror -y install gd libxslt libxml2
```


<a name="Basic"></a>
# Basic Supervisor for MAJA processor

The basic supervisor **start_maja** enables to process successively all files in a time series of Sentinel-2 images for a given tile, stored in a folder. The initialisation of the time series is performed with the "backward mode", and then all the dates are processed in "nominal" mode. The backward mode takes much more time than the nominal mode. On my computer, which is a fast one, the nominal mode takes 15 minutes, and the backward mode takes almost one hour. No control is done on the outputs, and it does not check if the time elapsed between two successive products used as input is not too long and would require restarting the initialisation in backward mode.


To use this start_maja.py, you will need to configure the directories within the folder.txt file.

## Download Sentinel-2 data :
The use of peps_download.py to download Sentinel-2 l1c PRODUCTS is recommended :
https://github.com/olivierhagolle/peps_download

<a name="parameters"></a>
## Parameters
The tool needs a lot of configuration files which are provided in two directories "userconf" and "GIPP_S2AS2B". I tend to never change the "userconf", but the GIPP_S2AS2B contains the parameters and look-up tables, which you might want to change. Most of the parameters lie within the L2COMM file. When I want to test different sets of parameters, I create a new GIPP folder, which I name GIPP_context, where *context* is passed as a parameter of the command line with option -c . 

We provide two sets of parameters, one to work without CAMS data, and one to work with CAMS data. The latter needs a lot of disk space (~1.5 GB), as the LUT are provided not only for one aerosol type, but for for 5 aerosol types, and 6 water vapour contents. As Github limits the repository size to 1 GB, we are using a gitlab repository to distribute the parameters (GIPP):  
- Parameters without CAMS : http://tully.ups-tlse.fr/olivier/gipp/tree/master/GIPP_MAJA_3_1_S2AS2B_MUSCATE_TM
- Parameters with CAMS: http://tully.ups-tlse.fr/olivier/gipp/tree/master/GIPP_MAJA_3_1_S2AS2B_CAMS (but we don't recommend to use it)
The look-up tables are too big to be but on our gitlab server, you will have to download them following the link in the GIPP readme file. (I know, it's a bit complicated)

## Folder structure
To run MAJA, you need to store all the necessary data in an input folder. Here is an example of its content in nominal mode.

```
S2A_MSIL1C_20180316T103021_N0206_R108_T32TMR_20180316T123927.SAFE
S2A_TEST_GIP_CKEXTL_S_31TJF____10001_20150703_21000101.EEF
S2A_TEST_GIP_CKQLTL_S_31TJF____10005_20150703_21000101.EEF
S2A_TEST_GIP_L2ALBD_L_CONTINEN_10005_20150703_21000101.DBL.DIR
S2A_TEST_GIP_L2ALBD_L_CONTINEN_10005_20150703_21000101.HDR
S2A_TEST_GIP_L2COMM_L_ALLSITES_10008_20150703_21000101.EEF
S2A_TEST_GIP_L2DIFT_L_CONTINEN_10005_20150703_21000101.DBL.DIR
S2A_TEST_GIP_L2DIFT_L_CONTINEN_10005_20150703_21000101.HDR
S2A_TEST_GIP_L2DIRT_L_CONTINEN_10005_20150703_21000101.DBL.DIR
S2A_TEST_GIP_L2DIRT_L_CONTINEN_10005_20150703_21000101.HDR
S2A_TEST_GIP_L2SMAC_L_ALLSITES_10005_20150703_21000101.EEF
S2A_TEST_GIP_L2TOCR_L_CONTINEN_10005_20150703_21000101.DBL.DIR
S2A_TEST_GIP_L2TOCR_L_CONTINEN_10005_20150703_21000101.HDR
S2A_TEST_GIP_L2WATV_L_CONTINEN_10005_20150703_21000101.DBL.DIR
S2A_TEST_GIP_L2WATV_L_CONTINEN_10005_20150703_21000101.HDR
S2B_OPER_SSC_L2VALD_32TMR____20180308.DBL.DIR
S2B_OPER_SSC_L2VALD_32TMR____20180308.HDR
S2B_TEST_GIP_CKEXTL_S_31TJF____10001_20150703_21000101.EEF
S2B_TEST_GIP_CKQLTL_S_31TJF____10005_20150703_21000101.EEF
S2B_TEST_GIP_L2ALBD_L_CONTINEN_10003_20150703_21000101.DBL.DIR
S2B_TEST_GIP_L2ALBD_L_CONTINEN_10003_20150703_21000101.HDR
S2B_TEST_GIP_L2COMM_L_ALLSITES_10008_20150703_21000101.EEF
S2B_TEST_GIP_L2DIFT_L_CONTINEN_10002_20150703_21000101.DBL.DIR
S2B_TEST_GIP_L2DIFT_L_CONTINEN_10002_20150703_21000101.HDR
S2B_TEST_GIP_L2DIRT_L_CONTINEN_10002_20150703_21000101.DBL.DIR
S2B_TEST_GIP_L2DIRT_L_CONTINEN_10002_20150703_21000101.HDR
S2B_TEST_GIP_L2SMAC_L_ALLSITES_10005_20150703_21000101.EEF
S2B_TEST_GIP_L2TOCR_L_CONTINEN_10002_20150703_21000101.DBL.DIR
S2B_TEST_GIP_L2TOCR_L_CONTINEN_10002_20150703_21000101.HDR
S2B_TEST_GIP_L2WATV_L_CONTINEN_10005_20150703_21000101.DBL.DIR
S2B_TEST_GIP_L2WATV_L_CONTINEN_10005_20150703_21000101.HDR
S2__TEST_AUX_REFDE2_T32TMR_0001.DBL.DIR
S2__TEST_AUX_REFDE2_T32TMR_0001.HDR
S2__TEST_GIP_L2SITE_S_31TJF____10001_00000000_99999999.EEF
```

The .SAFE file is the input product. THE L2VALD files are the L2A product, which is the result from a previous execution  of MAJA. The files with GIP are parameter files for S2A and S2B, that you will find in this repository. The REFDE2 files are the DTM files. How to obtain them is explained below. 

A "userconf" folder is also necessary, but it is also provided in this repository.



## DTM
A DTM folder is needed to process data with MAJA. Of course, it depends on the tile you want to process. This DTM must be stored in the DTM folder, which is defined within the code. A tool exists to create this DTM, [it is available in the "prepare_mnt" folder](https://github.com/olivierhagolle/Start_maja/tree/master/prepare_mnt).

An example of DTM file is available here for tile 31TFJ in Provence, France, near Avignon. Both files should be placed in a folder named DTM/S2__TEST_AUX_REFDE2_T31TFJ_0001 in the start_maja directory.

http://osr-cesbio.ups-tlse.fr/echangeswww/majadata//S2__TEST_AUX_REFDE2_T31TFJ_0001.DBL

http://osr-cesbio.ups-tlse.fr/echangeswww/majadata//S2__TEST_AUX_REFDE2_T31TFJ_0001.HDR

The DBL file is a tar file (I am innocent for this choice...) that can be opened with `tar xvf `. MAJA can use both the archive or un-archived version. The tool above provides the un-archived version (DBL.DIR).

## CAMS
if you intend to use the data from Copernicus Atmosphere Monitoring Service (CAMS), that we use to get an information on the aerosol type, you will need to download the CAMS data. A download tool is provided [in the cams_download directory of this repository](xxx)

<a name="workflow"></a>


# Example workflow

Here is how to process a set of data above tile 31TFJ, near Avignon in Provence, France. To process any other tile, you will need to prepare the DTM and store the data in the DTM folder.

## Install

- Install MAJA

- Clone the current repository to get start_maja.py
`git clone https://github.com/olivierhagolle/Start_maja`




## Retrieve Sentinel-2 L1C data.
- For instance, with peps_download.py (you need to have registered at https://peps.cnes.fr and store the account and password in peps.txt file.

`python ./peps_download.py -c S2ST -l 'Avignon' -a peps.txt -d 2017-01-01 -f 2017-04-01 -w /path/to/L1C_DATA/Avignon`

- I tend to store the data per site. A given site can contain several tiles. All the L1C tiles corresponding to a site are stored in a directory named /path/to/L1C_DATA/Site

- Unzip the LIC files in /path/to/L1C_DATA/Avignon

## Create DTM
Follow DTM generation instructions : http://tully.ups-tlse.fr/olivier/prepare_mnt

## Download CAMS data
Follow cams_download tool instructions : https://github.com/olivierhagolle/Start_maja/tree/master/cams_download

## Execute start_maja.py

- To use the start_maja script, you need to configure the directories, within the folder.txt file.
Here is my own configuration, also provided in the folders.txt file in this repository.
```
repCode=/mnt/data/home/hagolleo/PROG/S2/lance_maja
repWork=/mnt/data/SENTINEL2/MAJA
repL1  =/mnt/data/SENTINEL2/L1C_PDGS
repL2  =/mnt/data/SENTINEL2/L2A_MAJA
repMaja=/mnt/data/home/hagolleo/Install-MAJA/maja/core/1.0/bin/maja
repCAMS  =/mnt/data/SENTINEL2/CAMS
```
- repCode is where Start_maja.py is stored, together with the DTM, userconf and GIPP directories
- repWork is a directory to store the temporary files
- repL1 is where to find the L1C data (without the site name which is added aferward)
  - Les produits SAFE doivent donc être stockés à l'emplacement suivant : repL1  = repL1/site
- repL2 is for the L2A data (without the site name which is added aferward)
- repMAJA is where the Maja binary code is
- repCAMS is where CAMS data are stored



Here is an example of command line
```
Usage   : python ./start_maja.py -f <folder_file>-c <context> -t <tile name> -s <Site Name> -d <start date>
Example : python ./start_maja.py -f folders.txt -c MAJA_3_0_S2AS2B_CAMS -t 31TFJ -s Avignon -d 20170101 -e 20180101
```
Description of command line options :
* -f provides the folders filename
* -c is the context, MAJA uses the GIPP files contained in GIPP_context directory. The L2A products will be created in 
rep_L2/Site/Tile/Context (Several users told me it is weird to use the GIPP folder name after removing GIPP_, I should change that)
* -t is the tile number
* -s is the site name
* -d (aaaammdd) is the first date to process within the time series
* -e (aaaammdd) is the last date to process within the time serie-s
* -z directly uses zipped L1C files

Caution, *when a product has more than 90% of clouds, the L2A is not issued*. However, a folder with _NOTVALD_ is created.

## Known Errors


Some Sentinel-2 L1C products lack the angle information which is required by MAJA. In this case, MAJA stops processing with an error message. This causes issues particularly in the backward mode. These products were acquired in February and March 2016 and have not been reprocessed by ESA (despited repeated asks from my side). You should remove them from the folder which contains the list of L1C products to process. 


<a name="docker"></a>
# Docker

Dániel Kristóf provided us with a Dockerfile (Thank you Dániel), which, on any linux system retrieves the CentOS System, installs what is necessary and configures MAJA. I am really not a Docker expert, and when I tried, our lab system engineer immediately told me that there are some securities issues with Docker, and I should not install it like that...So, I never tested it.

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

```


## References :
<a name="ref1">1</a>: A multi-temporal method for cloud detection, applied to FORMOSAT-2, VENµS, LANDSAT and SENTINEL-2 images, O Hagolle, M Huc, D. Villa Pascual, G Dedieu, Remote Sensing of Environment 114 (8), 1747-1755

<a name="ref2">2</a>: Correction of aerosol effects on multi-temporal images acquired with constant viewing angles: Application to Formosat-2 images, O Hagolle, G Dedieu, B Mougenot, V Debaecker, B Duchemin, A Meygret, Remote Sensing of Environment 112 (4), 1689-1701

<a name="ref3">3</a>: A Multi-Temporal and Multi-Spectral Method to Estimate Aerosol Optical Thickness over Land, for the Atmospheric Correction of FormoSat-2, LandSat, VENμS and Sentinel-2 Images, O Hagolle, M Huc, D Villa Pascual, G Dedieu, Remote Sensing 7 (3), 2668-2691

<a name="ref4">4</a>: MAJA's ATBD, O Hagolle, M. Huc, C. Desjardins; S. Auer; R. Richter, https://doi.org/10.5281/zenodo.1209633


    
   

   
