# Conference seed data

Reviewer guidance for the four supported venues, drawn from each conference's
published reviewer instructions:

| Conference | Source |
| --- | --- |
| ICML | https://icml.cc/Conferences/2026/ReviewerInstructions |
| ACL | https://aclrollingreview.org/reviewerguidelines |
| NeurIPS | https://neurips.cc/Conferences/2026/ReviewerGuidelines |
| ICLR | https://iclr.cc/Conferences/2025/ReviewerGuide |

Each text maps the venue's own criteria onto the six dimensions the review
pipeline scores: Originality, Technical Soundness, Coherence Between Claims
and Experiments, Experimental Soundness, Significance, and Clarity. They do
not introduce new scales, so the JSON the model returns stays parseable.

## Loading

Run `seed_conferences.sql` in the Supabase SQL editor. It inserts missing
conferences and updates the guidance on ones that already exist, so it is
safe to re-run after editing any of the `.txt` files.

To regenerate the SQL after editing a text file, see the plain-text sources
alongside it; the SQL simply embeds them with single quotes doubled.


## Per-venue scoring

Each guidance file ends with a scoring section that overrides the generic
prompt in two ways:

**Dimension weighting.** The generic prompt averages all eight categories
equally. Each venue instead specifies weights summing to 100%, reflecting what
that venue says it cares about. ACL weights the soundness dimensions highest
because ARR treats soundness as the primary judgement; NeurIPS weights
significance and originality highest; ICLR weights experimental soundness
lowest, because it states that missing state-of-the-art results are not by
themselves grounds for rejection.

**Decision thresholds.** Accept cut-offs differ by venue, ordered by how
selective each one is:

| Venue | Accept | Marginal Accept | Marginal Reject | Reject |
| --- | --- | --- | --- | --- |
| ACL | 8.0+ | 7.0-7.9 | 5.5-6.9 | below 5.5 |
| NeurIPS | 8.0+ | 7.0-7.9 | 5.5-6.9 | below 5.5 |
| ICML | 7.5+ | 6.5-7.4 | 5.0-6.4 | below 5.0 |
| ICLR | 7.0+ | 6.0-6.9 | 4.5-5.9 | below 4.5 |

The exceptional-paper bonuses are preserved everywhere, but the final score
is capped at 10 in the prompt and again in code after parsing.

These weights and thresholds are a calibration, not official numbers. No
venue publishes a dimension weighting. Edit the `.txt` files and regenerate
the SQL to tune them.
