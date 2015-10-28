
INSERT INTO players (name) VALUES ('Chen Lu');
INSERT INTO players (name) VALUES ('Aleka Cheung');
INSERT INTO players (name) VALUES ('Piggy');
INSERT INTO players (name) VALUES ('test');
INSERT INTO players (name) VALUES ('player_name');
SELECT * FROM players;


INSERT INTO matches (tournament_id, winner_id,loser_id) VALUES (1,1,2);
INSERT INTO matches (tournament_id, winner_id,loser_id) VALUES (1,1,3);
INSERT INTO matches (tournament_id, winner_id,loser_id) VALUES (1,2,3);

SELECT * FROM matches;

INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (1, 1);
INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (1, 2);
INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (1, 3);
INSERT INTO tournament_registrations (tournament_id, player_id) VALUES (1, 4);

SELECT * FROM tournament_registrations;