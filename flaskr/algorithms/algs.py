'''
This is a collection of algorithms that are used throughout different routes/pages of the website. They are collected here so that the
only functions in the main set of files are route functions.
'''

def sql_prepared_tuple(length, count=1, output=""):
    '''
    A recursive function that returns a string with a variable number of
    question marks seperated by commas, such to be inserted into an SQL statement where an
    array needs to be taken as a value.
    '''
    if count==length:
        return output+'?'
    else:
        return sql_prepared_tuple(length, count+1, output+'?,')
