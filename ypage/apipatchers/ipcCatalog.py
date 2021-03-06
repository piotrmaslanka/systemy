from yos.ipc import Catalog
from collections import defaultdict
from threading import RLock
from ypage.nukleon import S

class CatalogHandler(Catalog):

    catalog_lock = RLock()
    catalog_root = defaultdict(dict)
    
    @staticmethod
    def store(key: str, value: object, catname: str=''):
        with CatalogHandler.catalog_lock:
            CatalogHandler.catalog_root[catname][key] = value
        
    @staticmethod
    def remove(key: str, value: object, catname: str=''):
        with CatalogHandler.catalog_lock:
            del CatalogHandler.catalog_root[catname][key]
            if len(CatalogHandler.catalog_root[catname]) == 0:
                del CatalogHandler.catalog_root[catname]
        
    @staticmethod
    def get(key: str, result1: callable, catname: str=''):
        with CatalogHandler.catalog_lock:
            try:
                val = CatalogHandler.catalog_root[catname][key]
            except KeyError:
                S.schedule(S.loc.tcb, result1, Catalog.NotFoundError)
            else:
                S.schedule(S.loc.tcb, result1, val)
        
    @staticmethod
    def gather(keys, result1: callable, catname: str=''):
        result = {}
        with CatalogHandler.catalog_lock:
            for key in keys:
                try:
                    result[key] = CatalogHandler.catalog_root[catname][key]
                except KeyError:
                   result[key] = Catalog.NotFoundError
        S.schedule(S.loc.tcb, result1, result)
                
    @staticmethod
    def scatter(kv: dict, catname: str=''):
        with CatalogHandler.catalog_lock:
            CatalogHandler.catalog_root[catname].update(kv)
        
import yos.ipc
yos.ipc.Catalog = CatalogHandler        