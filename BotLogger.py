"""
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
"""


class Logger:
    
    def __init__(self, enabled=True):
        self.logfile = 'log.out'
        self.enabled = enabled

    def log(self, string):
        """Log an element.

        This method will only log the information to the file if logging has
        been enabled."""
        # Log only if logging has been enabled
        if self.enabled:
            with open(self.logfile, 'a') as f:
                f.write(str(string) + '\n')

    def get(self, lines=50):
        """Get the last N lines of the log file, defaults to 50."""
        with open(self.logfile, 'r') as f:
            read_lines = f.readlines()
            requested_lines = read_lines[-lines:]
            return ''.join(requested_lines)

    def clear(self, bot):
        """Clear all the information stored in the log file."""
        with open(self.logfile, 'w') as f:
            f.write('')
