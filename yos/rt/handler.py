def Handler(self, func, *args, **kwargs):
    """
    Returns a function that takes obj as it's first parameter, then takes received arguments, and
    then takes extra passed (here as args and kwargs)
    """
    def decf(*locargs, **lockwargs):
        lockwargs.update(kwargs)
        print(locargs+args)
        return func(self, *(locargs + args), **lockwargs)
    
    return decf