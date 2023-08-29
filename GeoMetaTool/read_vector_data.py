import os
import geopandas as gpd
import logging
import utils

#Set up logging
log = logging.getLogger(__name__)

def read_vector_data(file_path):
    """ 
    read vector data 
        
    Arguments: 
        file_path (string): The path of the file to be opened.   
    """
    data = {}
    data['file_extension'] = os.path.splitext(file_path)[1].upper()
    data['file_type'] = utils.lookup_extension_format(data['file_extension'])
    data['EPSG'] = None
    data['BBOX'] = None
    data['referenceSystemTypeCode'] = None
    data['distributionDescription'] = 'Offline File'
    data['geometry_types_count'] = None
    data['field_summary_list'] = []


    if data['file_extension'] == '.SHP':
        log.debug('Opening Shapefile')
        try:
            gdf_content = gpd.read_file(file_path)
        except:
            log.error('Failed to open Shapefile')
            raise

    # Set referenceSystemTypeCode
    data['referenceSystemTypeCode'] = 'geodeticGeographic2D'

    # Get EPSG
    data['EPSG'] = str(gdf_content.crs.to_epsg())

    # Get bounding box
    data['BBOX'] = [0,0,0,0]
    data['BBOX'][0], data['BBOX'][2], data['BBOX'][1], data['BBOX'][3] = gdf_content.total_bounds 
    if data['EPSG'] != '4326':
        data['BBOX'] = utils.BBOXtoWGS84(data['BBOX'], data['EPSG'])
    data['BBOX'][0] = str(data['BBOX'][0])
    data['BBOX'][1] = str(data['BBOX'][1])
    data['BBOX'][2] = str(data['BBOX'][2])
    data['BBOX'][3] = str(data['BBOX'][3])

    # Get the number of each geometry type
    data['geometry_types_count'] = gdf_content['geometry'].geom_type.value_counts()

    # Get summary info on each field            
    for column_name in gdf_content.columns:
        if column_name == 'geometry':
            continue
        field_summary = {}
        field_summary['fieldName'] = column_name
        field_summary['valueType'] = gdf_content[column_name].dtype
        field_summary['numUniqueValues'] = len(gdf_content[column_name].unique())
        field_summary['10UniqueValues'] = gdf_content[column_name].unique()[:10]
        data['field_summary_list'].append(field_summary)

    return data


                