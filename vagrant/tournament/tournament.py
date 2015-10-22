#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from decimal import * #handle postgres return type Decimal


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    #get db conn
    conn = connect()

    #get cursor to execute queries
    c = conn.cursor()

    #execute query
    c.execute("DELETE FROM matches;")

    #save the transaction to db and close conn
    conn.commit()
    conn.close


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players;")
    conn.commit()
    conn.close

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM players;")
    num = c.fetchone()
    conn.close
    return num[0]

def registerPlayer(name, tournament_id):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()

    #SQL safe parameter insertion
    c.execute("INSERT INTO players (name) VALUES (%s) RETURNING id", (name,))
    p_id = c.fetchone() #get the player ID returned from the insert above
    #print p_id[0]

    #add the player to the correct tournament
    c.execute("INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (%s,%s)", (tournament_id,p_id[0]))
    
    conn.commit() #commit the transaction
    conn.close

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
        select id,name,wins,total_matches from player_standings p where tournament_id = (%s);
    '''
    conn = connect()
    c = conn.cursor()
    c.execute(query, (tournament_id,)) #execute the query with the specified tournament ID data to retrieve
    results = c.fetchall();
    conn.close


    #check OMW and sort by those too.
    for i in range (0, len(results)):
        n = getOpponentWins(tournament_id,results[i][0])
        results[i] +=  n # add wins to tuple


    #sort results based on wins & the opponent wins
    s_results = sorted(results, key = lambda x : (-x[2], -x[4])) # column 2 = wins, column 4 = OMW

    for i in range (0, len(s_results)):
        s_results[i] = s_results[i][:-1] # remove the extra column from output after sorting
    #return final result
    return s_results;


def reportMatch(tournament_id, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    
    sql = "INSERT INTO matches (tournament_id, winner_id, loser_id) VALUES (%s,%s,%s)";
    data = (tournament_id, winner, loser)
    conn = connect()
    c = conn.cursor()
    c.execute(sql,data)
    conn.commit()
    conn.close

 
 
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

def getOpponentWins(tournament_id, player_id):
    """Helper function to find the opponent match wins sum for player_id in tournament_id
  
    Queries for list of opponents and sums up their wins.

    Returns:
        Tuple with decimal value
    """
    #sql to retrieve sum of wins of opponents that current player has won against
    opponentWinsForGivenPlayerSQL = '''
    SELECT coalesce(sum(opp_wins.wins),0) from (with 
        win_temp as (select winner_id, count(winner_id) win_cnt from matches where winner_id in (select id from players) group by winner_id)
    select 
        p.id, p.name, 
        coalesce(w.win_cnt,0) wins 
    from 
        players p 
        left join win_temp w on (p.id = w.winner_id) 
    where 
        p.id in (select player_id from tournament_registrations as r where r.tournament_id = (%s))
        and 
        p.id in (select m.loser_id as player_id from matches as m where m.winner_id = (%s))
    ) as opp_wins
    '''
    conn = connect()
    c = conn.cursor()

    #SQL safe parameter insertion
    c.execute(opponentWinsForGivenPlayerSQL, (tournament_id,player_id))
    r = c.fetchone() #get the sum of opponent wins returned
    #print num[0]

    conn.close

    return r #return tuple


