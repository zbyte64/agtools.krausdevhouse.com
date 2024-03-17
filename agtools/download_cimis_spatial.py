import datetime
import georasters as gr
import tempfile
import requests
import gzip
from sqlalchemy import create_engine
import os
from pyproj import Transformer
from shapely.ops import transform
import logging


# TODO configure this elsewhere
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

DATASETS_PATH = os.environ.get("DATASETS_PATH", './datasets')

project = Transformer.from_crs("EPSG:3310", "EPSG:4326").transform

local_eto_path = lambda date: f"{DATASETS_PATH}/cimis-spatial/{date.strftime('%Y/%m/%d')}/Eto.asc.gz"


def download_cimis_spatial_date(date, check_for_existing=True):
    """
    Downloads for a date
    """
    write_to_path = local_eto_path(date)
    if check_for_existing and os.path.exists(write_to_path):
        return
    subpath = date.strftime("%Y/%m/%d")
    logger.info(f'Downloading CIMIS for ${subpath}')

    location = "https://spatialcimis.water.ca.gov/cimis/{subpath}/ETo.asc.gz".format(
        subpath=subpath
    )

    response = requests.get(location)
    response.raise_for_status()
    os.makedirs(os.path.dirname(write_to_path), exist_ok=True)
    with open(write_to_path, mode='wb') as fp:
        fp.write(response.content)
        fp.close()


def read_cimis_spatial_date(date):
    """
    Must download first!
    Reads for a date, returns a pandas dataframe of ETo values with lat lng
    """
    read_path = local_eto_path(date)
    content = gzip.GzipFile(fileobj=open(read_path, 'rb'), mode="r").read()
    with tempfile.TemporaryDirectory() as tmpdirname:
        fname = os.path.join(tmpdirname, "Eto.asc")
        fp = open(fname, "wb")
        fp.write(content)
        fp.close()
        data = gr.from_file(fname)
    df = data.to_geopandas()
    df["date"] = date
    # convert mm to inches
    df["value_inches"] = df["value"] / 25.4
    # we only care about centroids
    # reproject geometry to lat lng
    df["geometry"] = df["geometry"].values.map(lambda x: transform(project, x.centroid))
    # import code; code.interact(local=locals()) 
    return df


def process_cimis_spatial_date(date):
    download_cimis_spatial_date(date)
    df = read_cimis_spatial_date(date)
    engine = create_engine(os.environ['DATABASE_URL'])
    logger.info(f'Writing CIMIS [${date}] to database with columns ${df.columns}')
    # TODO squash by date
    df.to_postgis("cimis_spacetime", engine, if_exists='replace')


if __name__ == "__main__":
    process_cimis_spatial_date(datetime.date.today() - datetime.timedelta(days=2))