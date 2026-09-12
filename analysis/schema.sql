-- =====================================================================
-- Reading task: storage schema.
--
-- DataPipe writes ONE CSV PER PARTICIPANT, each with its own header row
-- (filename = <pid>_<rand>.csv). Everything arrives as TEXT because the
-- engine builds the row with String(v) -- so `picked_is_cause` is the
-- four characters 'true', not an integer 1. `raw` preserves that exactly;
-- the typed views do the casting once, in one place.
-- =====================================================================

DROP VIEW  IF EXISTS v_hinge;
DROP VIEW  IF EXISTS v_cell_rates;
DROP VIEW  IF EXISTS v_choice_set;
DROP VIEW  IF EXISTS v_clean;
DROP VIEW  IF EXISTS v_public;
DROP VIEW  IF EXISTS v_typed;
DROP TABLE IF EXISTS participant_map;
DROP TABLE IF EXISTS stimuli;
DROP TABLE IF EXISTS raw;

-- ---------------------------------------------------------------- raw ----
-- Byte-faithful landing table: column names and order exactly as wideRow()
-- emits them. Never edit rows here; corrections belong in views.
CREATE TABLE raw (
  source_file        TEXT NOT NULL,     -- which DataPipe CSV this came from
  trial_type         TEXT,
  pid                TEXT,              -- Prolific ID: identifying, never published
  rung               TEXT,
  frame              TEXT,
  pos1_role          TEXT,
  pos2_role          TEXT,
  pos3_role          TEXT,
  pos4_role          TEXT,
  cause_position     TEXT,
  selfblame_position TEXT,
  picked_position    TEXT,
  picked_role        TEXT,
  picked_is_cause    TEXT,              -- 'true' / 'false', NOT 1 / 0
  why_text           TEXT,
  attn_response      TEXT,
  attn_pass          TEXT,              -- 'true' / 'false'
  age                TEXT,
  gender             TEXT,
  rt_pick_ms         TEXT,
  rt_why_ms          TEXT,
  total_ms           TEXT,
  completed          TEXT,              -- 'true' / 'false'
  jspsych_version    TEXT
);

-- ------------------------------------------------------------ stimuli ----
-- The sentences themselves, lifted out of reading_study_engine.html by
-- analysis/extract_stimuli.py, plus the hand-coded grammar dimensions.
-- This is what lets an option-level row know WHAT it was.
CREATE TABLE stimuli (
  frame              TEXT NOT NULL,
  rung               INTEGER NOT NULL,
  role               TEXT NOT NULL,     -- C cause / B self-blame / S scene / N neutral
  role_name          TEXT NOT NULL,
  text               TEXT NOT NULL,
  n_words            INTEGER,
  sigma_predication  REAL,              -- event -> individual-level property
  tau_temporal       REAL,              -- one past act -> universal over a lifetime
  epsilon_commitment REAL,              -- hedged -> certain
  delta_domain       REAL,              -- one person -> anyone
  alpha_agency       REAL,              -- agent -> patient
  kappa_free         REAL,              -- bound to the event -> free-standing claim
  PRIMARY KEY (frame, rung, role)
);

-- --------------------------------------------------- participant_map ----
-- The consent form promises the Prolific ID "will not be included in any
-- published data". This table is the ONLY place the link is kept, and it
-- is the one table that must not ship with the dataset.
CREATE TABLE participant_map (
  pid            TEXT PRIMARY KEY,
  participant_id TEXT NOT NULL UNIQUE
);

-- -------------------------------------------------------------- typed ----
CREATE VIEW v_typed AS
SELECT
  r.source_file,
  r.pid,
  CAST(r.rung AS INTEGER)            AS rung,
  r.frame,
  r.pos1_role, r.pos2_role, r.pos3_role, r.pos4_role,
  CAST(r.cause_position     AS INTEGER) AS cause_position,
  CAST(r.selfblame_position AS INTEGER) AS selfblame_position,
  CAST(r.picked_position    AS INTEGER) AS picked_position,
  r.picked_role,
  CASE WHEN LOWER(r.picked_is_cause) = 'true' THEN 1 ELSE 0 END AS picked_is_cause,
  CASE WHEN r.picked_role = 'B'              THEN 1 ELSE 0 END AS picked_is_selfblame,
  r.why_text,
  r.attn_response,
  CASE WHEN LOWER(r.attn_pass)  = 'true' THEN 1 ELSE 0 END AS attn_pass,
  CASE WHEN LOWER(r.completed)  = 'true' THEN 1 ELSE 0 END AS completed,
  r.age, r.gender,
  CAST(r.rt_pick_ms AS REAL) AS rt_pick_ms,
  CAST(r.rt_why_ms  AS REAL) AS rt_why_ms,
  CAST(r.total_ms   AS REAL) AS total_ms,
  CASE WHEN r.rung IN ('3','4','5') THEN 1 ELSE 0 END AS person_bound  -- the hinge
FROM raw r;

-- -------------------------------------------------------------- clean ----
-- Pre-registered exclusions, in one place so the N is never ambiguous.
CREATE VIEW v_clean AS
SELECT * FROM v_typed
WHERE completed = 1
  AND attn_pass = 1
  AND picked_role IS NOT NULL AND picked_role <> ''
  AND rung BETWEEN 1 AND 5
  AND frame IN ('plain','setaside');

-- ------------------------------------------------------------- public ----
-- Shareable extract: no Prolific ID, no free text (free text can identify).
CREATE VIEW v_public AS
SELECT m.participant_id, c.frame, c.rung, c.person_bound,
       c.pos1_role, c.pos2_role, c.pos3_role, c.pos4_role,
       c.picked_position, c.picked_role, c.picked_is_cause, c.picked_is_selfblame,
       c.age, c.gender, c.rt_pick_ms, c.rt_why_ms, c.total_ms
FROM v_clean c JOIN participant_map m ON m.pid = c.pid;

-- --------------------------------------------------------- choice set ----
-- The wide row is a COMPRESSED choice set. This unpivots it back into the
-- four options the participant actually faced -- one row per option --
-- which is the design matrix the conditional logit needs. The wide row is
-- sufficient for this: pos1..pos4_role + picked_position reconstruct
-- every option's role, serial position, and (by join) its text.
CREATE VIEW v_choice_set AS
WITH slots(position) AS (VALUES (1),(2),(3),(4))
SELECT
  c.pid,
  c.frame,
  c.rung,
  c.person_bound,
  s.position,
  CASE s.position WHEN 1 THEN c.pos1_role WHEN 2 THEN c.pos2_role
                  WHEN 3 THEN c.pos3_role ELSE c.pos4_role END AS role,
  CASE WHEN c.picked_position = s.position THEN 1 ELSE 0 END   AS chosen,
  st.text, st.n_words,
  st.sigma_predication, st.tau_temporal, st.epsilon_commitment,
  st.delta_domain, st.alpha_agency, st.kappa_free
FROM v_clean c
CROSS JOIN slots s
LEFT JOIN stimuli st
  ON st.frame = c.frame AND st.rung = c.rung
 AND st.role  = CASE s.position WHEN 1 THEN c.pos1_role WHEN 2 THEN c.pos2_role
                                WHEN 3 THEN c.pos3_role ELSE c.pos4_role END;

-- ------------------------------------------------------- cell summary ----
CREATE VIEW v_cell_rates AS
SELECT frame, rung, COUNT(*) AS n,
       AVG(picked_is_cause)                                  AS p_cause,
       AVG(picked_is_selfblame)                              AS p_selfblame,
       AVG(CASE WHEN picked_role='S' THEN 1.0 ELSE 0 END)    AS p_scene,
       AVG(CASE WHEN picked_role='N' THEN 1.0 ELSE 0 END)    AS p_neutral,
       AVG(rt_pick_ms)                                       AS mean_rt_pick_ms
FROM v_clean GROUP BY frame, rung;

-- The contrast the grammar predicts: rungs 1-2 (the sentence still refers to
-- the birthday) vs rungs 3-5 (it no longer does), within each frame.
CREATE VIEW v_hinge AS
SELECT frame,
       CASE person_bound WHEN 0 THEN 'episode-bound (r1-2)'
                                ELSE 'person-bound (r3-5)' END AS side,
       COUNT(*) AS n,
       AVG(picked_is_cause)     AS p_cause,
       AVG(picked_is_selfblame) AS p_selfblame
FROM v_clean GROUP BY frame, person_bound;
