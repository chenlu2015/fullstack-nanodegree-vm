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

CREATE TABLE players
   (
      --id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
      id SERIAL PRIMARY KEY, 
      name VARCHAR(90) NOT NULL
   );

INSERT INTO players (name) VALUES ('Chen Lu');
INSERT INTO players (name) VALUES ('Aleka Cheung');
INSERT INTO players (name) VALUES ('Piggy');
INSERT INTO players (name) VALUES ('test');
INSERT INTO players (name) VALUES ('player_name');
SELECT * FROM players;


CREATE TABLE matches
   (
   	match_id SERIAL PRIMARY KEY,
      tournament_id INT NOT NULL,
      winner_id INT references players(id) NOT NULL,
      loser_id INT references players(id) NOT NULL
   );

INSERT INTO matches (tournament_id, winner_id,loser_id) VALUES (1,1,2);
INSERT INTO matches (tournament_id, winner_id,loser_id) VALUES (1,1,3);
INSERT INTO matches (tournament_id, winner_id,loser_id) VALUES (1,2,3);

SELECT * FROM matches;

CREATE TABLE tournament_registrations
   (  
      registration_id SERIAL PRIMARY KEY,
      tournament_id INT NOT NULL,
      player_id INT references players(id) NOT NULL
   );

INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (1, 1);
INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (1, 2);
INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (1, 3);
INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (1, 4);

SELECT * FROM tournament_registrations;

CREATE VIEW player_standings AS (
SELECT 
    tournament_id, id, name, wins, losses, total_matches

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

