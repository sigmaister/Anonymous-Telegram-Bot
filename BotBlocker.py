"""
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
"""


class Blocker:
    
    def __init__(self, sql_wrapper):
        self.sql = sql_wrapper
        self.sql.execute_and_commit(
            "CREATE TABLE IF NOT EXISTS blocked_user_ids (user_id);")

    def block_user(self, user_id):
        """
        Block a user.

        Updated the blocked table by adding the user ID if it is not already
        there."""
        if not self.is_user_blocked(user_id):
            self.sql.execute_and_commit(
                "INSERT INTO blocked_user_ids (user_id) VALUES (?);",
                (user_id,))

    def unblock_user(self, user_id):
        """
        Unblock a user.

        Remove the blocked user ID from the block table if the ID exists."""
        self.sql.execute_and_commit(
            "DELETE FROM blocked_user_ids WHERE user_id=?;",
            (user_id,))

    def get_blocked_users(self):
        """Retrieve a list of the currently blocked user IDs."""
        rows = self.sql.select_and_fetch(
            "SELECT user_id FROM blocked_user_ids;")
        user_ids = [str(user_id[0]) for user_id in rows]
        return user_ids

    def is_user_blocked(self, user_id):
        """Verify if a user ID is stored in the block table."""
        matched_ids = self.sql.select_and_fetch(
            "SELECT COUNT(*) FROM blocked_user_ids WHERE user_id=?",
            (user_id,))
        # Return format from query is [(count,)]
        return matched_ids[0][0]
