-- =====================================================================
-- Analysis queries. Each block is standalone; run the one you want.
-- Percentages are printed as proportions so they compose with the models.
-- =====================================================================

-- Q1 ---- ASSIGNMENT BALANCE ------------------------------------------
-- DataPipe's getCondition rotates through 10 cells, but the engine falls
-- back to Math.random() if that call throws, and the fallback is not
-- recorded. Badly uneven cells are the only visible symptom.
SELECT frame, rung, COUNT(*) AS n_raw,
       SUM(CASE WHEN LOWER(attn_pass)='true' THEN 1 ELSE 0 END) AS n_passed
FROM raw GROUP BY frame, rung ORDER BY frame, rung;

-- Q2 ---- THE HEADLINE TABLE ------------------------------------------
SELECT frame, rung, n,
       ROUND(p_cause,3) AS p_cause, ROUND(p_selfblame,3) AS p_selfblame,
       ROUND(p_scene,3) AS p_scene, ROUND(p_neutral,3) AS p_neutral
FROM v_cell_rates ORDER BY frame, rung;

-- Q3 ---- THE HINGE ---------------------------------------------------
-- Rungs 1-2 still refer to the birthday; rungs 3-5 do not. If the ladder
-- is a switch rather than a dial, the gap lives here.
SELECT frame, side, n, ROUND(p_cause,3) AS p_cause, ROUND(p_selfblame,3) AS p_selfblame
FROM v_hinge ORDER BY frame, side;

-- Q4 ---- DOES THE FRAME BITE LESS AT DEPTH? --------------------------
-- The 'setting aside how it makes the writer feel' instruction names a
-- FEELING. Rungs 3-5 are belief reports. This is the interaction that
-- asks whether the instruction reaches them.
SELECT CASE person_bound WHEN 0 THEN 'episode-bound (r1-2)' ELSE 'person-bound (r3-5)' END AS side,
       ROUND(AVG(CASE WHEN frame='plain'    THEN CAST(picked_is_selfblame AS REAL) END),3) AS p_B_plain,
       ROUND(AVG(CASE WHEN frame='setaside' THEN CAST(picked_is_selfblame AS REAL) END),3) AS p_B_setaside,
       ROUND(AVG(CASE WHEN frame='plain'    THEN CAST(picked_is_selfblame AS REAL) END)
           - AVG(CASE WHEN frame='setaside' THEN CAST(picked_is_selfblame AS REAL) END),3) AS frame_effect
FROM v_clean GROUP BY person_bound;

-- Q5 ---- SERIAL POSITION ---------------------------------------------
-- Paragraph order is randomised, and the option buttons repeat that order,
-- so whatever lands first is read as the topic sentence. Randomisation
-- makes this unbiased on average; it does not make it small.
SELECT position, COUNT(*) AS n_offered, SUM(chosen) AS n_chosen,
       ROUND(1.0*SUM(chosen)/COUNT(*),3) AS p_chosen
FROM v_choice_set GROUP BY position ORDER BY position;

-- Q6 ---- ROLE x POSITION ---------------------------------------------
-- Does the causal sentence only win when it is read first?
SELECT role, position, COUNT(*) AS n_offered,
       ROUND(1.0*SUM(chosen)/COUNT(*),3) AS p_chosen
FROM v_choice_set GROUP BY role, position ORDER BY role, position;

-- Q7 ---- DIFFERENTIAL ATTRITION --------------------------------------
-- If the deep rungs fail the attention check more often, exclusions are
-- not random with respect to the manipulation.
SELECT rung,
       COUNT(*) AS n_raw,
       ROUND(1.0*SUM(CASE WHEN LOWER(attn_pass)='true' THEN 1 ELSE 0 END)/COUNT(*),3) AS pass_rate
FROM raw GROUP BY rung ORDER BY rung;

-- Q8 ---- TIME ON THE CHOICE ------------------------------------------
-- Deeper rungs are longer sentences. If reading time tracks rung, some of
-- any 'depth' effect is reading effort.
SELECT rung, COUNT(*) AS n,
       ROUND(AVG(rt_pick_ms)) AS mean_rt_pick_ms,
       ROUND(AVG(total_ms))   AS mean_total_ms
FROM v_clean GROUP BY rung ORDER BY rung;

-- Q9 ---- EXPORT FOR THE CONDITIONAL LOGIT ----------------------------
-- One row per option: this is the design matrix, ready for Python/R.
SELECT pid, frame, rung, person_bound, position, role, chosen,
       n_words, sigma_predication, tau_temporal, epsilon_commitment,
       delta_domain, alpha_agency, kappa_free
FROM v_choice_set ORDER BY pid, position;

-- Q10 ---- WHY-TEXT TRIAGE --------------------------------------------
-- The free text is the only channel where a reader says WHY. Pull it
-- beside the role they picked so coding is done blind to nothing.
SELECT picked_role, rung, frame, why_text, rt_why_ms
FROM v_clean WHERE LENGTH(TRIM(why_text)) > 0 ORDER BY picked_role, rung;
