# Data Dictionary for UFC Analytics Scraper

Below are the columns that may appear in the generated CSV file, along with their meanings. "Fighter" refers to the main fighter you queried, and "Opponent" refers to their opponent in that particular fight.

## General Columns

- **fighter_name**: Name of the main fighter for all rows.
- **opponent_name**: Name of the opponent for the given fight.
- **event_name**: Name of the event (e.g., "UFC 243: Whittaker vs. Adesanya").
- **event_date**: Date of the event.
- **result**: Outcome of the fight for the fighter (`win`, `loss`, `draw`, etc.).
- **method_main**: High-level fight-ending method (e.g., KO/TKO, Submission, U-DEC).
- **method_detail**: More specific detail about the method (e.g., "Punches", "Rear Naked Choke").
- **round**: The round in which the fight ended.
- **Time**: Total fight time in seconds at the end of the match.
- **TimeFormat**: The scheduled format of the fight (e.g., "3 Rnd (5-5-5)" or "5 Rnd (5-5-5-5-5)").
- **Referee**: The referee's name.
- **Details**: Additional fight-end details provided by UFCStats (if available).
- **fight_link**: URL link to the individual fight details page on UFCStats.

## Aggregate Totals (Prefix: `TOT_`)

These columns represent totals for the entire fight (all rounds combined):

- **TOT_fighter_KD**, **TOT_opponent_KD**: Knockdowns by fighter/opponent.
- **TOT_fighter_SigStr**, **TOT_opponent_SigStr**: Significant strikes landed vs. attempted combined into separate columns (`_landed`, `_attempted`, `_percentage` after transformation).
- **TOT_fighter_SigStr_pct**, **TOT_opponent_SigStr_pct**: Significant strike success percentage (0-100).
- **TOT_fighter_Str**, **TOT_opponent_Str**: Total strikes landed vs. attempted.
- **TOT_fighter_Td**, **TOT_opponent_Td**: Takedowns landed vs. attempted.
- **TOT_fighter_Td_pct**, **TOT_opponent_Td_pct**: Takedown success percentage.
- **TOT_fighter_SubAtt**, **TOT_opponent_SubAtt**: Submission attempts.
- **TOT_fighter_Rev**, **TOT_opponent_Rev**: Reversals.
- **TOT_fighter_Ctrl**, **TOT_opponent_Ctrl**: Total control time in seconds.

Each "X of Y" column will be split into `_landed`, `_attempted`, and `_percentage` columns. For example, TOT_fighter_SigStr might become TOT_fighter_SigStr_landed, TOT_fighter_SigStr_attempted, TOT_fighter_SigStr_percentage.

## Round-by-Round Totals (Prefix: `RoundX_`)

For each round `X`, the following columns may appear, showing that round’s metrics:

- **RoundX_fighter_KD**, **RoundX_opponent_KD**: Knockdowns in that round.
- **RoundX_fighter_SigStr**, **RoundX_opponent_SigStr**: Significant strikes (again split into landed, attempted, percentage).
- **RoundX_fighter_SigStr_pct**, **RoundX_opponent_SigStr_pct**: Significant strike percentage for that round.
- **RoundX_fighter_Str**, **RoundX_opponent_Str**: Total strikes (landed, attempted, percentage).
- **RoundX_fighter_Td_pct**, **RoundX_opponent_Td_pct**: Takedown percentage that round. (Note: TOT per round only gives percentage, not attempts/landed.)
- **RoundX_fighter_SubAtt**, **RoundX_opponent_SubAtt**: Submissions attempted that round.
- **RoundX_fighter_Rev**, **RoundX_opponent_Rev**: Reversals that round.
- **RoundX_fighter_Ctrl**, **RoundX_opponent_Ctrl**: Control time in seconds that round.

## Round-by-Round Significant Strikes (Prefix: `RoundX_fighter_` or `RoundX_opponent_`)

From the significant strikes per round table, you may also see:

- **RoundX_fighter_HEAD**, **RoundX_opponent_HEAD**: Head strikes.
- **RoundX_fighter_BODY**, **RoundX_opponent_BODY**: Body strikes.
- **RoundX_fighter_LEG**, **RoundX_opponent_LEG**: Leg strikes.
- **RoundX_fighter_DISTANCE**, **RoundX_opponent_DISTANCE**: Strikes landed at distance.
- **RoundX_fighter_CLINCH**, **RoundX_opponent_CLINCH**: Strikes landed in clinch.
- **RoundX_fighter_GROUND**, **RoundX_opponent_GROUND**: Strikes landed on the ground.

These also originally appear as "X of Y" and will be split into landed, attempted, and percentage columns accordingly.

---

**Note:** If any column does not apply to a particular fighter or fight (e.g., no attempts), that column may contain `NaN`.  
All `---` values are converted to `NaN` for consistency.

