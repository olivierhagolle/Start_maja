# -*- coding: utf-8 -*-

from datetime import datetime as dt

def datetimeToString(timestamp):
    """
    @brief Convert datetime to string %Y-%m-%dT%H:%M:%S.%f
    """
    return timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def datetimeToStringShort(timestamp):
    """
    @brief Convert datetime to string YYYYMMDD
    """
    return timestamp.strftime("%Y%m%d")

def datetimeToStringName(timestamp):
    """
    @brief Convert datetime to string YYYYMMDD
    """
    return timestamp.strftime("%Y%m%d-%H%M%S-%f")[:-3]

def stringToDatetime(s):
    """
    @brief Convert string of format YYYYMMDD or %Y-%m-%dT%H:%M:%S.%f to datetime
    """
    if(len(s) == 24):
        return dt.strptime(s[:-1], "%Y-%m-%dT%H:%M:%S.%f")
    if(len(s) == 8):
        return dt.strptime(s, "%Y%m%d")
    raise ValueError("Unknown datetime string {0}".format(s))
    
    
def getDateFromProduct(product, platform):
    """
    Get the acquisition date of a S2, L8 or Vns product using its filename
    :param product: Tuple of product name and productID (0,1...) for different Regexes
    :param platform: Platform ID (0 == S2, 1 == L8, 2 == Vns)
    :return: The datetime of the product
    :type return: datetime.datetime
    """
    from Common import DateConverter
    import os
    path, productType = product
    filename = os.path.basename(path)
    datetimeAsString = None
    if(platform == 0):
        if(productType == 0):
            datetimeAsString = filename.split("_")[2].split("T")[0]
        elif(productType == 1):
            datetimeAsString = filename.split("_")[1].split("-")[0]
        elif(productType == 2):
            datetimeAsString = os.path.splitext(filename)[0].split("_")[-1]
        elif(productType == 3):
            datetimeAsString = filename.split("_")[5].split("T")[0]
    elif(platform == 1):
        if(productType == 0):
            datetimeAsString = filename.split("_")[3]
        elif(productType == 1):
            #Special treatment here: Acq date is given as YYYYJJJ where JJJ
            #is the Julian date of the year
            from datetime import datetime
            yeardoy = filename[9:16]
            return datetime.strptime(yeardoy, '%Y%j').date()
        elif(productType == 2):
            datetimeAsString = filename.split("_")[1].split("-")[0]
        elif(productType == 3):
            datetimeAsString = os.path.splitext(filename)[0].split("_")[-1]
    elif(platform == 2):
        if(productType == 0):
            datetimeAsString = filename.split("_")[1].split("-")[0]
        elif(productType == 1):
            datetimeAsString = os.path.splitext(filename)[0].split("_")[-1]
    if(datetimeAsString == None):
        raise ValueError("Unknown platform found for product %s" % filename)
    return DateConverter.stringToDatetime(datetimeAsString)
