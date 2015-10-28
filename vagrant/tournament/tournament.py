#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from decimal import * #handle postgres return type Decimal
from contextlib import contextmanager

@contextmanager
def get_cursor():
    """
    Don't forget to document this function if you use it!
    """
    conn = connect()
    cur = conn.cursor()
    try:
        yield cur
    except:
        raise
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    #helper function to get connection & cursor & commit & close
    with get_cursor() as cursor:
         #execute query
        cursor.execute("DELETE FROM matches;")


def deletePlayers():
    """Remove all the player records from the database."""
    #helper function to get connection & cursor & commit & close
    with get_cursor() as cursor:
         #execute query
        cursor.execute("DELETE FROM players;")

def countPlayers():
    """Returns the number of players currently registered."""
    num = 0;
    with get_cursor() as cursor:
         #execute query
        cursor.execute("SELECT COUNT(*) FROM players;")
        num = cursor.fetchone()
    return num[0]


def registerPlayer(name, tournament_id):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    p_id = 0
    with get_cursor() as cursor:
        #SQL safe parameter insertion
        cursor.execute("INSERT INTO players (name) VALUES (%s) RETURNING id", (name,))
        p_id = cursor.fetchone()
        #add the player to the correct tournament
        cursor.execute("INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (%s,%s)", (tournament_id,p_id[0]))

def playerStandings(tournament_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    # oldquery = '''select players.id, players.name,
    #              count(CASE WHEN matches.winner_id = players.id THEN 1 END) as wins,
    #              count(CASE WHEN matches.winner_id = players.id or matches.loser_id = players.id THEN 1 END) as total_matches
    #            from 
    #              players LEFT JOIN matches on matches.winner_id = players.id or matches.loser_id = players.id
    #            group by players.id
    #            order by wins desc;
    #         '''

    query = '''
        select id,name,wins,total_matches from player_standings ps join opponent_match_wins omw on (ps.tournament_id = omw.tournament_id) and (ps.id = omw.player_id) and (ps.tournament_id = (1)) order by wins desc, omw.opponent_match_wins desc;
    '''
    results = [];
    with get_cursor() as cursor:
         #execute query
        cursor.execute(query, (tournament_id,))
        results = cursor.fetchall()
    return results;


def reportMatch(tournament_id, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    
    sql = "INSERT INTO matches (tournament_id, winner_id, loser_id) VALUES (%s,%s,%s)";
    data = (tournament_id, winner, loser)

    with get_cursor() as cursor:
        #execute query
        cursor.execute(sql,data)

 
 
def swissPairings(tournament_id):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    currentStandings = playerStandings(tournament_id) # get current player standings for specified tournament

    pairings = [] #create empty list

    #for loop from 0 to number of players increment by 2 assuming always even number of players
    for i in range(0, len(currentStandings),2):
        player1 = currentStandings[i]   #player 1
        player2 = currentStandings[i+1] #player 2
        pairings.append((player1[0],player1[1],player2[0],player2[1])) #append one swisspairing tuple
    return pairings #return all paired tuples




