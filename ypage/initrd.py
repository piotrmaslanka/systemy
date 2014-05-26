"""
System y init list


Here you can specify tasklets you want to load on startup, in the form of tuples

    first element of tuple is a str, with target user value
    second element of tuple is a str, with target group value
    third element of tuple is a str, with target name value
    fourth element of tuple is either a str with path to tasklet class, or tasklet class itself
        ( so last element is the class name )
    
    fifth OPTIONAL element of tuple is an args tuple
    sixth OPTIONAL element of a tuple is a kwargs dictionary
"""
initrd = (       
    ('USER', 'group', 'asyncCommTest', 'examples.terminationExample.TerminationExampleTasklet'),
)