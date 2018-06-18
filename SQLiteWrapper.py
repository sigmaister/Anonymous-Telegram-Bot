'''
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github 
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
'''
import sqlite3

class SQLiteWrapper():
    
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name,check_same_thread=False)
        self.cursor = self.connection.cursor()
	
	
    def __execute(self, query, parameters):
        if parameters is None:
            self.cursor.execute(query)
        elif isinstance(parameters, list): 
            self.cursor.executemany(query, parameters)
        else:
            self.cursor.execute(query, parameters)


    def execute_script_and_commit(self, script):
        self.cursor.executescript(script)
        self.connection.commit()


    def execute_and_commit(self, query, parameters=None):
        self.__execute(query, parameters)
        self.connection.commit()


    def select_and_fetch(self, query, parameters=None):
        self.__execute(query, parameters)
        return self.cursor.fetchall()
