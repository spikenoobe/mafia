import sqlite3 as sq
import random

def insert_player(player_id: int, username: str) -> None:
    con = sq.connect("db.db")
    cur = con.cursor()
    sql = f"INSERT INTO players (player_id, username, mafia_vote, citizen_vote, voted, dead) VALUES (?, ?, 0, 0, 0, 0)"
    cur.execute(sql, (player_id, username))
    con.commit()
    con.close()

def player_amount() -> int:
    con = sq.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT * FROM players"
    cur.execute(sql)
    res = cur.fetchall()
    con.close()
    return len(res)


def get_mafia_usernames() -> str:
    con = sq.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE role = 'mafia'"
    cur.execute(sql)
    data = cur.fetchall()
    names = ''
    for row in data:
        name = row[0]
        names += name + '\n'
    con.close()
    return names


def get_player_roles( ) -> list:
    con = sq.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data


def get_all_alive() -> list:
    con = sq.connect("db.db")
    cur = con.cursor()
    sql = "SELECT username FROM players WHERE dead=0"
    cur.execute(sql)
    data = cur.fetchall()
    data = [row[0] for row in data]
    con.close()
    return data

def set_roles(players: int)-> None:
    games_role = ['citizen'] * players
    mafias = int(players * 0.3)
    for i in range(mafias):
        games_role[i] = 'mafia'
        random.shuffle(games_role)
        con = sq.connect("db.db")
        cur = con.cursor()
        cur.execute("SELECT player_id FROM players")
        players_ids = cur.fetchall()
        for role, id in zip(games_role, players_ids):
            sql = "UPDATE players SET role=? WHERE player_id=?"
            cur.execute(sql, (role, id[0]))
        con.commit()
        con.close()

def get_users() -> list:
    con = sq.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT username, role FROM players")
    users = cur.fetchall()
    return users

def vote(type: str, username: str, player_id: int) -> bool:
    con = sq.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT username FROM players WHERE player_id=? AND dead=0 AND voted=-0", (player_id,))
    can_vote = cur.fetchone()
    if can_vote:
        cur.execute(f"UPDATE players SET {type} = {type} + 1 WHERE username=?", (username,))
        cur.execute(f"UPDATE players SET voted = 1 WHERE player_id=?", (player_id,))
        con.commit()
        con.close()
        return True
    con.close()
    return False

def mafia_kill() -> str:
    con = sq.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE dead=0 AND role='mafia'")
    mafia_alive = cur.fetchone()[0]
    username_killed = 'никого'
    if max_votes == mafia_alive:
        cur.execute("SELECT username FROM players WHERE mafia_vote=?", (max_votes, ))
        username_killed = cur.fetchone()[0]
        cur.execute("UPDATE players SET dead=1 WHERE username=?", (username_killed,))
        con.commit()
    con.close()
    return username_killed

def citizen_kill() -> str:
    con = sq.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE citizen_vote=?", (max_votes,))
    max_count = cur.fetchone()[0]
    username_killed = 'никого'
    if max_count == 1:
        cur.execute("SELECT username FROM players WHERE citizen_vote=?", (max_votes,))
        username_killed = cur.fetchone()[0]
        cur.execute("UPDATE players SET dead=1 WHERE username=?", (username_killed,))
        con.commit()
    con.close()
    return username_killed

def check_winner() -> str | None:
    con = sq.connect("db.db")
    cur = con.cursor()
    cur.execute('SELECT COUNT(*) FROM players WHERE role="mafia" AND dead=0')
    mafia_alive = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM players WHERE role!="mafia" AND dead=0')
    citizen_alive = cur.fetchone()[0]
    if mafia_alive >= citizen_alive:
        return 'Мафия'
    elif mafia_alive == 0:
        return 'Горожане'
    return None

def clear(dead: bool=False) -> None:
    con = sq.connect("db.db")
    cur = con.cursor()
    sql = "UPDATE players SET citizen_vote = 0 , mafia_vote = 0, voted = 0"
    if dead:
        sql += ", dead = 0"
    cur.execute(sql)
    con.commit()
    con.close()

def create_tables():
    con = sq.connect("db.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        player_id INTEGER,
        username TEXT,
        role TEXT,
        mafia_vote INTEGER,
        citizen_vote INTEGER,
        voted INTEGER,
        dead INTEGER)
    """)
    con.commit()
    con.close()

if __name__ == "__main__":
#     #insert_player(1, "Денис")
#     #print(get_all_alive())
#     #set_roles(2)
#     # print(get_users())
#     print(vote())
#     # print(vote("citizen_vote", "е", 926725212))
#     # print(vote("mafia_vote", "мятя", 3))
#     # print(vote("citizen_vote", "мятя", 2))
#     # print(vote("citizen_vote", "п", 1))
#     # print(citizen_kill())
    # print(check_winner())
    pass