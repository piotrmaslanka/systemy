from yos.rt import BaseTasklet
from yos.ipc import Catalog

class CatalogExample(BaseTasklet):
    def on_startup(self):
        Catalog.store('test1', 'test2', catname='test3')
        Catalog.get('test1', self.on_read, catname='test3')
        
    def on_read(self, val):
        if val == 'test2': 
            print("Test passed")
        else:
            print("Test failed")