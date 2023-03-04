'''
This is a collection of algorithms that are used throughout different routes/pages of the website. They are collected here so that the
only functions in the main set of files are route functions.
'''
import datetime

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

def check_email(email):
    local = False
    seperator = False
    domain_name = False
    domain_toplevel = False

    for i, char in enumerate(email):
        if char == ' ':
            return False
        if not local and char!='@':
            local = True
        elif not seperator and char=='@':
            seperator = True
        elif not domain_name and char!='.':
            domain_name = True
        elif not domain_toplevel and char=='.' and i!=len(email)-1:
            domain_toplevel = True

    return (local and seperator and domain_name and domain_toplevel)

def validate_isodate(date_str):
    try:
        datetime.date.fromisoformat(date_str)
    except ValueError:
        return False
    return True
