import fiona
from shapely import geometry
from rtree import index
import click
import os
import tqdm


class CRSError(Exception):
    pass


@click.command()
@click.argument('in_shp')
@click.argument('out_shp')
@click.option('--overwrite', '-O', type=bool, default=False, is_flag=True,
              help="Overwrite the output shapefile if it already exists")
def main(in_shp, out_shp, overwrite):

    # check that the input shapefile exists
    if os.path.exists(in_shp) is False:
        raise FileExistsError("Input {} could not be found.".format(in_shp))
    # check if the output shapefile exists
    if os.path.exists(out_shp) is True:
        if overwrite is False:
            err = "Output {} already exists. Use the overwrite flag or specify a different output.".format(out_shp)
            raise FileExistsError(err)

    # read geometries from the input file
    print("Reading input shapefile.")
    geoms = []
    with fiona.open(in_shp, 'r') as f:
        # make sure the data are projected to UTM
        if 'utm' not in f.crs_wkt.lower():
            raise CRSError("Invalid input coordinate system. Data must be projected to UTM.")

        # check that the input is type Polygon
        geom_type = f.schema['geometry']
        if geom_type != 'Polygon':
            err = "Invalid geometry type ({}). Input shapefile must have geometry type Polygon.".format(geom_type)
            raise TypeError(err)

        # read the geometries
        for feat in f:
            geom = geometry.shape(feat['geometry'])
            geoms.append(geom)

    # create spatial index
    print("Building spatial index.")
    idx = index.Index()
    # load the polygons into it
    for i, geom in enumerate(geoms):
        idx.insert(i, geom.bounds)

    # find the duplicates
    print("Searching for duplicate geometries.")
    duplicate_geoms_all = []
    for i, geom in tqdm.tqdm(enumerate(geoms), total=len(geoms)):
        # find duplicates using a few different rules
        duplicate_geoms = [j for j in idx.intersection(geom.bounds)
                           if geom.intersects(geoms[j])
                           and i != j
                           and (geom.equals(geoms[j])
                                or geom.almost_equals(geoms[j], decimal=6)
                                or geom.symmetric_difference(geoms[j]).buffer(0).area < 0.01)]
        if len(duplicate_geoms) > 0:
            duplicate_geoms_all.append(i)
            duplicate_geoms_all.extend(duplicate_geoms)

    # remove duplicate ids from the list of duplicate geoms
    duplicate_ids_unique = set(duplicate_geoms_all)

    print('Found {} features with duplicate geometries.'.format(len(duplicate_ids_unique)))

    # write out the duplicates
    print("Creating output shapefile of duplicate geometries.")
    with fiona.open(in_shp, 'r') as input:
        with fiona.open(out_shp, 'w', driver='ESRI Shapefile', schema=input.schema, crs=input.crs) as output:
            for i, feat in enumerate(input):
                if i in duplicate_ids_unique:
                    output.write(feat)

if __name__ == '__main__':
    main()
