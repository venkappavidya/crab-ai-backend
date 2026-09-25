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
