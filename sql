-- Kreiraj usera (promijeni 'lozinka123' u nešto svoje)
CREATE USER macinger WITH PASSWORD '1324';

-- Kreiraj bazu
CREATE DATABASE tennis_analysis OWNER macinger;

-- Spoji se na tu novu bazu
\c tennis_analysis

-- Kreiraj shemu macinger
CREATE SCHEMA macinger AUTHORIZATION macinger;

-- Postavi putanju da macinger uvijek prvo vidi svoju shemu
ALTER ROLE macinger SET search_path TO macinger, public;

-- Brišemo staru tablicu ako postoji da izbjegnemo konflikte
DROP TABLE IF EXISTS clay.match_scores;

-- Kreiramo novu, poboljšanu tablicu
CREATE TABLE clay.match_scores (
    id SERIAL PRIMARY KEY,           -- Automatski ID (sekvenca)
    match_name TEXT NOT NULL,         -- Ime meča (npr. JODAR vs ...)
    match_id INTEGER,                   -- ID meča (iz sekvene match_id_seq)
    set_number INTEGER,               -- Broj seta
    game_number INTEGER,              -- Broj gema u setu
    player_name TEXT,                 -- Ime igrača koji je osvojio ili na koga se odnosi red
    result_type TEXT,                 -- Tip rezultata (BREAK, HOLD, itd.)
    score1 TEXT,                      -- Rezultat igrača 1 (npr. "40")
    score2 TEXT,                      -- Rezultat igrača 2 (npr. "15")
    duration TEXT,                    -- Trajanje (npr. "02:15")
    created_at TIMESTAMP DEFAULT now() -- Automatski sprema VRIJEME unosa u bazu
);

CREATE SEQUENCE clay.match_id_seq START WITH 1;

cur.execute("SELECT nextval('clay.match_scores_seq')")

select * from clay.match_scores

ALTER TABLE match_scores 
ADD COLUMN match_url TEXT;

ALTER TABLE match_scores 
ADD COLUMN tournament_name TEXT;

ALTER TABLE match_scores 
ADD COLUMN tournament_location TEXT;

truncate table clay.match_scores;
truncate table clay.match_service_stats;

truncate table clay.match_return_stats;

truncate Table clay.match_point_stats;

CREATE TABLE match_service_stats (
    id SERIAL PRIMARY KEY,            
    player_name TEXT,             -- Ime igrača na kojeg se statistika odnosi
    set_number INTEGER,                   -- 0 za cijeli meč, 1, 2, 3 za specifične setove
    serve_rating INTEGER,
    aces INTEGER,
    double_faults INTEGER,  -- First Serve (npr. 53/96)
    first_serve_in INTEGER,
    first_serve_total INTEGER,
    first_serve_pct DECIMAL(5,2),-- 1st Serve Points Won (npr. 34/53)
    first_serve_points_won INTEGER,
    first_serve_points_total INTEGER,
    first_serve_points_pct DECIMAL(5,2),-- 2nd Serve Points Won (npr. 24/43)
    second_serve_points_won INTEGER,
    second_serve_points_total INTEGER,
    second_serve_points_pct DECIMAL(5,2),-- Break Points Saved (npr. 1/5)
    break_points_saved INTEGER,
    break_points_facing INTEGER,
    break_points_saved_pct DECIMAL(5,2),
    service_games_played INTEGER,
    match_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE match_return_stats (
    id SERIAL PRIMARY KEY,
    match_url TEXT,                       -- Ovo je sada tvoja glavna poveznica
    player_name TEXT,                     -- Ime igrača (npr. ĐOKOVIĆ)
    set_number INTEGER,                   -- 0 za cijeli meč, 1, 2, 3 za setove
    return_rating INTEGER,  -- 1st Serve Return Points Won (npr. 19/72 (26%))
    first_return_won INTEGER,             -- 19
    first_return_total INTEGER,           -- 72
    first_return_pct DECIMAL(5,2),        -- 26.00-- 2nd Serve Return Points Won (npr. 31/53 (58%))
    second_return_won INTEGER,            -- 31
    second_return_total INTEGER,          -- 53
    second_return_pct DECIMAL(5,2),       -- 58.00-- Break Points Converted (npr. 3/15 (20%))
    bp_converted INTEGER,                 -- 3
    bp_opportunities INTEGER,             -- 15
    bp_converted_pct DECIMAL(5,2),        -- 20.00
    return_games_played INTEGER,          -- 17
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE match_point_stats (
    id SERIAL PRIMARY KEY,
    match_url TEXT,                       -- Poveznica s ostalim tablicama
    player_name TEXT,                     -- Ime igrača
    set_number INTEGER,                   -- 0 za meč, 1, 2, 3 za setove-- Net Points Won (npr. 11/13 (85%))
    net_points_won INTEGER,               -- 11
    net_points_total INTEGER,             -- 13
    net_points_pct DECIMAL(5,2),          -- 85.00 
    winners INTEGER,                      -- 31
    unforced_errors INTEGER,              -- 52-- Service Points Won (npr. 58/96 (60%))
    service_points_won INTEGER,           -- 58
    service_points_total INTEGER,         -- 96
    service_points_pct DECIMAL(5,2),      -- 60.00-- Return Points Won (npr. 50/125 (40%))
    return_points_won INTEGER,            -- 50
    return_points_total INTEGER,          -- 125
    return_points_pct DECIMAL(5,2),       -- 40.00-- Total Points Won (npr. 108/221 (49%))
    total_points_won INTEGER,             -- 108
    total_points_total INTEGER,           -- 221
    total_points_pct DECIMAL(5,2),        -- 49.00
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from clay.match_scores