# -*- coding: utf-8 -*-

import logging
import os
import uuid
import time

from iso_metadata import *
from geo_profiles import vector_data
from geo_profiles import raster_data
from geo_profiles import geo_database
import utils


# set up logging
log = logging.getLogger(__name__)

def extract_metadata(input_file_path, default_values=[]):
    """ 
    Function to create an XML format metadata file. 
        
    Arguments: 
        output_file_path (string): The path of the output metadata file.   
    """

    input_file_path = input_file_path
    file_name_with_extension = os.path.basename(input_file_path)
    file_name = os.path.splitext(file_name_with_extension)[0]
    file_extension = os.path.splitext(file_name_with_extension)[1].upper()
    file_type = utils.lookup_extension_type(file_extension)
    file_format = utils.lookup_extension_format(file_extension)
    file_date = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(input_file_path)))

    if default_values:
        LanguageCode = default_values["LanguageCode"]
        CharacterSetCode = default_values["CharacterSetCode"]
        ResourceScope = default_values["ResourceScope"]
        OrganisationName = default_values["OrganisationName"]
        IndividualName = default_values["IndividualName"]
        RoleCode = default_values["RoleCode"]
        Abstract = default_values["Abstract"]
        Keywords = default_values["Keywords"]
        ProgressCode = default_values["ProgressCode"]
        TimePeriod = default_values["TimePeriod"]
        ClassificationCode = default_values["ClassificationCode"]
        UseLimitations = default_values["UseLimitations"]
    else:
        LanguageCode = "eng"
        CharacterSetCode = "UTF-8"
        ResourceScope = "dataset"
        OrganisationName = "No name"
        IndividualName = "No name"
        RoleCode = "author"
        Abstract = "This file was automatically generated and has no abstract."
        Keywords = []
        ProgressCode = ""
        TimePeriod = ["", ""]
        ClassificationCode = ""
        UseLimitations = ""
 
    iso_metadata = ISO_Metadata()

    ###############
    # Vector data #
    ###############
    if file_type == 'Vector':
        profiles = vector_data.read_profiles(input_file_path)

        # set vectorSpatialRepresentation
        vectorSpatialRepresentation = {}
        vectorSpatialRepresentation['topologyLevelCode'] = "geometryOnly"
        geometricObjectsList = []
        for geom_type, count in profiles['geometry_types_count'].items():
            if geom_type == 'Point':
                objectType = 'point'
            elif geom_type == 'LineString':
                objectType = 'curve'
            elif geom_type == 'Polygon':
                objectType = 'surface'
            else:
                objectType = 'complex'
            geometricObject = {}
            geometricObject['objectType'] = objectType
            geometricObject['count'] = count
            geometricObjectsList.append(geometricObject)
        vectorSpatialRepresentation['geometricObjectsList'] = geometricObjectsList
        
        # set featureTypeList
        featureTypeList = []
        characteristicsList = []
        for field_summary in profiles['field_summary_list']:
            characteristics = {}
            characteristics['memberName'] = field_summary['field_name']
            characteristics['valueType'] = field_summary['value_type']
            characteristics['listedValueList'] = field_summary['10_unique_values']
            characteristicsList.append(characteristics)
        featureType = {}
        featureType['typeName'] = profiles['layerName']
        featureType['definition'] = profiles['layerName']
        featureType['carrierOfCharacteristicsList'] = characteristicsList
        featureTypeList.append(featureType)

        # add elements
        iso_metadata.metadataIdentifier(str(uuid.uuid1()))   
        if LanguageCode and CharacterSetCode:
            iso_metadata.defaultLocale(LanguageCode, CharacterSetCode)
        if ResourceScope:
            iso_metadata.metadataScope(ResourceScope)
        iso_metadata.contact(OrganisationName, IndividualName, RoleCode)
        iso_metadata.dateInfo(file_date, 'creation')
        if vectorSpatialRepresentation:
            iso_metadata.spatialRepresentationInfo(vectorSpatialRepresentation, None)
        if profiles['EPSG']:
            iso_metadata.referenceSystemInfo(profiles['EPSG'], profiles['referenceSystemTypeCode'])
        iso_metadata.identificationInfo(file_name, Abstract, ProgressCode, None, profiles['BBOX'], TimePeriod, file_format, Keywords, ClassificationCode, UseLimitations)
        if featureTypeList:
            iso_metadata.contentInfo(profiles['layerName'], [profiles['layerName']], "v", file_date, LanguageCode, OrganisationName, IndividualName, RoleCode, featureTypeList)
        iso_metadata.distributionInfo('Offline File.', file_name_with_extension)
        


    ###############
    # Raster data #
    ###############
    elif file_type == 'Raster':
        profiles = raster_data.read_profiles(input_file_path)
    

    ################
    # Geo database #
    ################
    elif file_type == 'Geographic Database':
        profiles = geo_database.read_profiles(input_file_path)
    
    else:
        raise Exception(f"This package does not support {file_type}.")
    
    return iso_metadata
