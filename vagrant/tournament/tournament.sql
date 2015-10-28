-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;
\c tournament;

--CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- import the uuid-ossp module to generate uuids, but need to be superuser..?

CREATE TABLE tournaments
  (
    id INT PRIMARY KEY,
    name VARCHAR(90)
  );

CREATE TABLE players
   (
      --id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
      id SERIAL PRIMARY KEY, 
      name VARCHAR(90) NOT NULL
   );

CREATE TABLE matches
   (
   	  match_id SERIAL PRIMARY KEY,
      tournament_id INT references tournaments(id) ON DELETE CASCADE,
      winner_id INT references players(id) ON DELETE CASCADE,
      loser_id INT references players(id) ON DELETE CASCADE
   );


CREATE TABLE tournament_registrations
   (  
      registration_id SERIAL PRIMARY KEY,
      tournament_id INT references tournaments(id) ON DELETE CASCADE,
      player_id INT references players(id) ON DELETE CASCADE
   );

CREATE VIEW opponent_match_wins AS (

SELECT tournament_id, player_id, (SELECT coalesce(sum(opp_wins.wins),0) from (with 
        win_temp as (select winner_id, count(winner_id) win_cnt from matches where winner_id in (select id from players) group by winner_id)
      select 
          p.id, p.name, 
          coalesce(w.win_cnt,0) wins 
      from 
          players p 
          left join win_temp w on (p.id = w.winner_id) 
      where 
          p.id in (select player_id from tournament_registrations as r where r.tournament_id = (tournament_registrations.tournament_id))
          and 
          p.id in (select m.loser_id as player_id from matches as m where m.winner_id = (players.id))
      ) as opp_wins) AS omw
  FROM
    players join tournament_registrations on (players.id = tournament_registrations.player_id)
);

CREATE VIEW player_standings AS (
select standings.tournament_id, opponent_match_wins.player_id, name, wins, losses, total_matches, omw  from 
  (SELECT 
    tournament_registrations.tournament_id, id, name, wins, losses, total_matches
    from 
    (
        with 
            win_temp as (select winner_id, count(winner_id) win_cnt from matches where winner_id in (select id from players) group by winner_id), 
            lose_temp as (select loser_id, count(loser_id) lose_cnt from matches where loser_id in (select id from players) group by loser_id)
        select 
            p.id, p.name,
            coalesce(w.win_cnt,0) wins, 
            coalesce(l.lose_cnt,0) losses, 
            coalesce(w.win_cnt,0) + coalesce(l.lose_cnt,0) total_matches
        from 
            players p 
            left join win_temp w on (p.id = w.winner_id) 
            left join lose_temp l on (p.id = l.loser_id) 
        where 
            p.id in (select id from players)
    ) as t1 left join tournament_registrations on (t1.id = tournament_registrations.player_id)
  ) AS standings join 
  opponent_match_wins on (standings.id = opponent_match_wins.player_id) and (standings.tournament_id = opponent_match_wins.tournament_id) order by wins desc, omw desc
  );

select * from player_standings;

-- select t1.id, t1.name, t1.wins, t2.total_matches 
-- from 
-- (select players.id, players.name, count(matches.winner_id) as wins
-- from players left join matches
-- on players.id = matches.winner_id
-- group by players.id
-- order by wins desc) 
-- as t1, 
-- (select players.id, count(matches.match_id) as total_matches
-- from players left join matches
-- on players.id = matches.winner_id or players.id = matches.loser_id
-- group by players.id
-- order by total_matches desc) as t2
-- where t1.id = t2.id
-- order by t1.wins desc;


-- select t1.id, t1.name, t1.wins, t1.total_matches from (
-- with win_temp as (select winner_id, count(winner_id) win_cnt, tournament_id from matches where winner_id in (select id from players) group by winner_id, tournament_id), 
-- lose_temp as (select loser_id, count(loser_id) lose_cnt, tournament_id from matches where loser_id in (select id from players) group by loser_id, tournament_id)
-- select coalesce(w.tournament_id,l.tournament_id) tournament_number, p.id, p.name, coalesce(w.win_cnt,0) wins, coalesce(l.lose_cnt,0) losses, coalesce(w.win_cnt,0) + coalesce(l.lose_cnt,0) total_matches
-- from players p left join win_temp w on (p.id = w.winner_id) left join lose_temp l on (p.id = l.loser_id) order by tournament_number, wins desc
-- ) as t1 
-- where t1.id in (select player_id from tournament_registrations as r where r.tournament_id = 1);



-- with win_temp as (select winner_id, count(winner_id) win_cnt from matches where winner_id in (select id from players) group by winner_id), 
-- lose_temp as (select loser_id, count(loser_id) lose_cnt from matches where loser_id in (select id from players) group by loser_id)
-- select p.id, p.name, coalesce(w.win_cnt,0) wins, coalesce(l.lose_cnt,0) losses, coalesce(w.win_cnt,0) + coalesce(l.lose_cnt,0) total_matches
-- from players p left join win_temp w on (p.id = w.winner_id) left join lose_temp l on (p.id = l.loser_id) 
-- where p.id in (select player_id from tournament_registrations as r where r.tournament_id = 1)

