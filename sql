-- LEFT JOIN: svi mečevi, gemovi ako postoje
SELECT m.match_id,
       m.player1_name,
       m.player2_name,
       m.result_player1,
       m.result_player2,
       m.odds_player1,
       m.odds_player2,
       g.set_number,
       g.game_number,
       g.player_name AS game_player_name,
       g.result_type,
       g.score1,
       g.score2
FROM matches m
LEFT JOIN games g ON m.match_id = g.match_id
ORDER BY m.match_id, g.set_number, g.game_number;

delete from games;
delete from matches;

commit;
