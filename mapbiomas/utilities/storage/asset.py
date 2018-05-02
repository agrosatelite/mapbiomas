import ee
import ee.data

ee.Initialize()

class AssetStorage(object):
    @staticmethod
    def create(asset, opt_path=None):
        ee.data.createAsset(asset, opt_path)
        print('Asset created.')

    @staticmethod
    def delete(asset, cascade=False):
        if cascade:
            collection = ee.ImageCollection(asset).toList(10000)
            assets = collection.map(lambda x: ee.String(asset + '/').cat(ee.Image(x).id())).getInfo()
            for a in assets:
                AssetStorage.delete(a)
        ee.data.deleteAsset(asset)
        print('Asset {0} deleted.'.format(asset))

    @staticmethod
    def copy(asset_origin, asset_destination, cascade=False):
        if cascade:
            collection = ee.ImageCollection(asset_origin).toList(10000)
            assets = collection.map(lambda x: ee.Image(x).id()).getInfo()
            for a in assets:
                AssetStorage.copy(asset_origin + "/" + a, asset_destination + "/" + a)
        else:
            ee.data.copyAsset(asset_origin, asset_destination)
            print('Asset {0} copied to {1}.'.format(asset_origin, asset_destination))

    @staticmethod
    def rename(asset_origin, asset_destination):
        ee.data.renameAsset(asset_origin, asset_destination)
        print('Asset {0} renamed to {1}.'.format(asset_origin, asset_destination))