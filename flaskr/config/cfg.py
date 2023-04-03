'''
This is a simple class used to store config values to be accessed by different parts of the backend
'''

class Config:
    DB_DIR = './db/project.db'
    COMMENT_LIMIT=20
    DATE_FORMAT_ISO8601='%Y-%m-%d' # The DATE_FORMAT_ISO8601 datetime format

    search_type_reference = {
        'eq':'=',
        'neq':'!=',
        'g':'>',
        'l':'<',
        'geq':'>=',
        'leq':'<=',
        'LIKE':'LIKE'
    }
    