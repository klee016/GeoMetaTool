# -*- coding: utf-8 -*-

import logging
import os
import uuid
import datetime

from metadata_formatter import *
import vector_data
import raster_data
import geo_database
import utils


# set up logging
log = logging.getLogger(__name__)

class MetadataExtractor:
    """ 
    Class to extract metadata from a geospatial data file.
    File extension, file type, catchwords and date information are, if possible, extracted by the directory and filenames.
    """
    
    def __init__(self, input_file_path, default_values=[]):
        """ 
        The constructor for the MetadataExtractor class. 
          
        Arguments: 
            file_path (string): The path of an input geospatial file. 
            default_values (list): A list of certain default values for the matedata.
        """
        self.input_file_path = input_file_path
        self.file_name_with_extension = os.path.basename(input_file_path)
        self.file_name = os.path.splitext(input_file_path)[0]
        self.file_extension = os.path.splitext(input_file_path)[1].upper()
        self.file_type = utils.lookup_extension_type(self.file_extension)
        self.file_format = utils.lookup_extension_format(self.file_extension)
        # self.file_date = utils.search_date(os.path.basename(os.path.normpath(input_file_path)))

        if default_values:
            self.DefaultLocale = default_values[0]
            self.ResourceScope = default_values[1]
            self.RoleCode = default_values[2]
            self.Organisation = default_values[3]
            self.Abstract = default_values[4]
            self.Keywords = default_values[5]
            self.ProgressCode = default_values[6]
            self.TimePeriod = default_values[8]
            self.ClassificationCode = default_values[9]
            self.UseLimitations = default_values[10]
        else:
            self.DefaultLocale = ""
            self.ResourceScope = ""
            self.RoleCode = ""
            self.Organisation = ""
            self.Abstract = ""
            self.Keywords = ""
            self.ProgressCode = ""
            self.TimePeriod = ["", ""]
            self.ClassificationCode = ""
            self.UseLimitations = ""
        
        log.info(f'MetadataExtractor successfully initialized. file path: {input_file_path}')
        

    def create_metadata(self, output_file_path):
        """ 
        Function to create an XML format metadata file. 
          
        Arguments: 
            output_file_path (string): The path of the output metadata file.   
        """

        meatadata_formatter = MetadataFormatter()
        self.metadata_formatter = meatadata_formatter

        ###############
        # Vector data #
        ###############
        if self.file_type == 'Vector':
            profiles = vector_data.read_profiles(self.input_file_path)

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
            meatadata_formatter.metadataIdentifier(str(uuid.uuid1()))   
            if self.DefaultLocale:
                meatadata_formatter.defaultLocale(self.DefaultLocale)
            if self.ResourceScope:
                meatadata_formatter.metadataScope(self.ResourceScope)
            meatadata_formatter.contact(self.RoleCode, self.Organisation)
            meatadata_formatter.dateInfo(datetime.datetime.today().strftime('%Y-%m-%d'), 'creation')
            if profiles['EPSG']:
                meatadata_formatter.referenceSystemInfo(profiles['EPSG'], profiles['referenceSystemTypeCode'])
            meatadata_formatter.identificationInfo(self.file_name, self.Abstract, self.ProgressCode, None, profiles['BBOX'], self.TimePeriod, self.file_format, self.Keywords, self.ClassificationCode, self.UseLimitations)
            meatadata_formatter.distributionInfo('Offline File.', self.file_name_with_extension)
            if vectorSpatialRepresentation:
                meatadata_formatter.spatialRepresentationInfo(vectorSpatialRepresentation, None)
            if featureTypeList:
                meatadata_formatter.contentInfo(profiles['layerName'], self.DefaultLocale, featureTypeList)
            meatadata_formatter.write_to_file(output_file_path)


        ###############
        # Raster data #
        ###############
        elif self.file_type == 'Raster':
            profiles = raster_data.read_profiles(self.input_file_path)
        

        ################
        # Geo database #
        ################
        elif self.file_type == 'Geographic Database':
            profiles = geo_database.read_profiles(self.input_file_path)
        
        else:
            raise Exception(f"This package does not support {self.file_type}.")
