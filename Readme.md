# Basic Supervisor for MAJA processor

This tool enables to process successively all files in a time series of MAJA images, stored in a folder. The initialisation of the time series is performed with the "backward mode", and then all the dates are processed in "nominal" mode. But no control is done on the outputs, and it does not check if the time elapsed between two successive products is not too long and would require restarting the initialisation in backward mode.


To use this tool, you will need to configure the directories within the code (I know, it's not very professional).

## Get MAJA Sofware
MAJA can be downloaded as a binary code from https://logiciels.cnes.fr/content/maja?language=en
It is provided as a binary code and compiled for *Linux Red Hat and CentOS versions 6 and 7 only*. Its licence prevents commercial use of the code.

## Getting the Sentinel-2 data :
The use of peps_download.py is recommended :
https://github.com/olivierhagolle/peps_download

## Parameters
The tool needs a lot of configuration files which are provided in two directories "userconf" and "GIPP_nominal". I tend to never change the "userconf", but the GIPP_nominal contains the parameters and look-up tables, which you might want to change. Most of the parameters lie within the L2COMM file. When I want to test different sets of parameters, I create a new GIPP folder, which I name GIPP_<context>, where <context> is spassed as a parameter of the command line.


## DTM
A DTM file is needed to process data with MAJA. Of course, it depends on the tile you want to process. This DTM must be stored in the DTM folder, which is defined within the code. A tool exists to create this DTM, it is available here : http://tully.ups-tlse.fr/olivier/prepare_mnt

# Command line
Here is an example of command line
```
Usage   : python ./lance_maja.py -c <context> -t <tile name> -s <Site Name> -d <start date>
Example : python ./lance_maja.py -c nominal -t 40KCB -s Reunion -d 20160401
```

*When a product has more than 90% of clouds, the L2A is not issued*

## Known Errors

Some Sentinel-2 L1C products lack the angle information which is required by MAJA. In this case, MAJA stop processing with an error message. This causes issues particularly in the backward mode. These products were acquired in February and March 2016 and have not been reprocessed by ESA (despited repeated asks from my side). You should remove them from the folder which contains the list of L1C products to process.



 

