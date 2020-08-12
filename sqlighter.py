import sqlite3

class SQLighter:

    database_file = "db.sqlite3"

    def __init__(self):
        self.connections = sqlite3.connect(self.database_file)
        with self.connections:
            self.cursor = self.connections.cursor()
            self.cursor.execute('CREATE TABLE IF NOT EXISTS instagram_users (id INTEGER PRIMARY KEY,instagram_username VARCHAR (255) NOT NULL,last_post_id VARCHAR (255) NOT NULL,instagram_user_id VARCHAR (255) NOT NULL);')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,user_id VARCHAR (255) NOT NULL);')
            self.cursor.execute('CREATE TABLE IF NOT EXISTS subscriptions (user_id INTEGER REFERENCES users (id),instagram_id INTEGER REFERENCES instagram_users (id));')

    def user_exists(self, user_id):
        with self.connections:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id):
        with self.connections:
            self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    def get_user_id(self, user_id):
        result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return result[0]

    def instagram_user_exists(self, instagram_username):
        with self.connections:
            result = self.cursor.execute("SELECT * FROM instagram_users WHERE instagram_username = ?", (instagram_username,)).fetchall()
            return bool(len(result))

    def add_instagram_user(self, instagram_username, last_post_id, instagram_user_id):
        with self.connections:
            self.cursor.execute("INSERT INTO instagram_users (instagram_username,last_post_id,instagram_user_id) VALUES (?,?,?)", (instagram_username, last_post_id, instagram_user_id))

    def get_instagram_id(self, instagram_username):
        result = self.cursor.execute("SELECT id FROM instagram_users WHERE instagram_username = ?", (instagram_username,)).fetchone()
        return result[0]
    
    def get_instagram_last_post_id(self, instagram_user_id):
        result = self.cursor.execute("SELECT last_post_id FROM instagram_users WHERE instagram_user_id = ?", (instagram_user_id,)).fetchone()
        return result[0]

    def get_all_instagram_user_id(self):
        result = self.cursor.execute("SELECT instagram_user_id FROM instagram_users").fetchall()
        return result

    def update_last_post_id(self, last_post_id, instagram_user_id):
        self.cursor.execute("UPDATE instagram_users SET last_post_id = ? WHERE instagram_user_id = ?", (last_post_id,instagram_user_id))

    def subscribe(self, user_id, instagram_username):
        u_id = self.get_user_id(user_id)
        i_id = self.get_instagram_id(instagram_username)
        self.cursor.execute("INSERT INTO subscriptions (user_id, instagram_id) VALUES (?,?)", (u_id,i_id))

    def unsubscribe(self,user_id,instagram_username):
        u_id = self.get_user_id(user_id)
        i_id = self.get_instagram_id(instagram_username)
        self.cursor.execute("DELETE FROM subscriptions WHERE user_id = ? AND instagram_id = ?", (u_id,i_id))

    def subscriptions_exist(self, user_id, instagram_username):
        u_id = self.get_user_id(user_id)
        i_id = self.get_instagram_id(instagram_username)
        result = self.cursor.execute("SELECT * FROM subscriptions WHERE user_id = ? AND instagram_id = ?", (u_id, i_id)).fetchall()
        return bool(len(result))

    def get_subscriptions(self, user_id):
        result = self.cursor.execute("Select instagram_users.instagram_username From (users Join subscriptions ON (subscriptions.user_id = users.id)) JOIN instagram_users ON (subscriptions.instagram_id = instagram_users.id) WHERE users.user_id = ?", (user_id,)).fetchall()
        return result

    def get_subscribers(self, instagram_user_id):
        result = self.cursor.execute("SELECT users.user_id FROM (users JOIN subscriptions ON (subscriptions.user_id = users.id)) JOIN instagram_users ON (subscriptions.instagram_id = instagram_users.id) WHERE instagram_users.instagram_user_id = ?", (instagram_user_id,)).fetchall()
        return result

    def close(self):
        self.connections.close()