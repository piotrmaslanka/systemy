
class Catalog(object):
    """
    Interface allowing access to system-wide catalog.
    
    Catalog is essentially a key-value store, where keys are strings,
    and values are simple entries.
    
    There can be many catalogs - they are identified by their 'catnames'.
    Default catalog is "" (empty string')
    """
    
    class NotFoundError(Exception):
        """Returned by callback when a given entry does not exist"""
    
    @staticmethod
    def store(key: str, value: object, catname: str=''):
        """
        Stores a value by given key in a catalog given by catname
        """

    @staticmethod
    def remove(key: str, value: object, catname: str=''):
        """
        Removes a value by given key in a catalog given by catname
        """
        
    @staticmethod
    def get(key: str, result1: callable, catname: str=''):
        """
        Lookups an entry and returns it.
        
        Alternatively, an exception class can be returned if entry doesn't exist
        """
        
    @staticmethod
    def gather(keys, result1: callable, catname: str=''):
        """
        Queries multiple keys. When results are available, calls result1
        with a dictionary that maps keys to values recovered. A Catalog.NotFoundError
        class will be the value for given key if no entry was found
        """
        
    @staticmethod
    def scatter(kv: dict, catname: str=''):
        """Updates multiple keys at once in given catalog.
        kv contains keys and new values"""