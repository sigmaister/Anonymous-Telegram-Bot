'''
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github 
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
'''
class Logger():
    
    def __init__(self, logpath):
        self.logpath = logpath
        self.logfile = self.logpath + 'log.out'

    def log(self, string):
        with open(self.logfile, 'a') as f:
            f.write(string + '\n')

    def get(self, lines=50):
        with open(self.logfile, 'r') as f:
            read_lines = f.readlines()
            requested_lines = read_lines[-lines:]
            return ''.join(requested_lines)
        
    def clear(self):
        with open(self.logfile, 'w') as f:
            f.write('')            
