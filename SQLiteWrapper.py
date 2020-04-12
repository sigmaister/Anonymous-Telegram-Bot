"""
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
"""
import sqlite3


class SQLiteWrapper:
    
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def __execute(self, query, parameters):
        """Run a query, optionally with parameters."""
        if parameters is None:
            self.cursor.execute(query)
        elif isinstance(parameters, list): 
            self.cursor.executemany(query, parameters)
        else:
            self.cursor.execute(query, parameters)

    def execute_file(self, path):
        with open(path, "r") as file:
            lines = []
            for line in file.readlines():
                lines.append(line.replace("\\n", "\n"))
            self.execute_script_and_commit("\n".join(lines))

    def execute_script_and_commit(self, script):
        """Execute an SQL script and commit its operations."""
        self.cursor.executescript(script)
        self.connection.commit()

    def execute_and_commit(self, query, parameters=None):
        """Execute an SQL command and commit its operation."""
        self.__execute(query, parameters)
        self.connection.commit()

    def select_and_fetch(self, query, parameters=None):
        """Select a set of rows.

        Returns an array containing one or several tuples, one for each
        matched row."""
        self.__execute(query, parameters)
        return self.cursor.fetchall()
