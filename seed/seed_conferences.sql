-- Seed the four conferences with their reviewer guidance.
-- Safe to re-run: existing names are updated, missing ones inserted.

with incoming (name, guidelines) as (
  values
  ('ICML', 'ICML 2026 REVIEW GUIDANCE

Source: https://icml.cc/Conferences/2026/ReviewerInstructions

ICML assesses four dimensions. Weigh the pipeline''s six scores against them:
- Soundness: technical correctness, appropriate methodology, quality of the
  evidence offered for each claim. Maps to Technical Soundness and
  Experimental Soundness.
- Presentation: clarity of writing, structure, and how well the work is
  situated in existing literature. Maps to Clarity.
- Significance: relevance of the problem and likely impact on the field.
  Maps to Significance.
- Originality: new insights, new methods or tasks, or a creative combination
  of existing techniques. Maps to Originality.

ICML''s own overall scale runs 1-6, where 6 is a technically flawless paper
with exceptional impact, 4 is technically solid with some weaknesses, 3 means
clear merits that are outweighed by weaknesses, and 1 is a well-known result
or an incomprehensible contribution. Calibrate the /10 final score to that
shape: reserve the top band for work that is both technically solid and high
impact, not merely competent.

Judge the paper on soundness first. A well-written paper with an unsupported
central claim is not a strong paper. Conversely, a technically correct result
that is poorly presented should lose points on Clarity, not on Soundness.

Ask 3-5 specific, numbered questions the authors could actually answer in a
rebuttal. Vague dissatisfaction is not a question.

Assess whether the authors acknowledge their own limitations honestly, and
whether societal impact is addressed where the work warrants it. Flag ethics
concerns explicitly: bias, privacy, research integrity, or applications open
to misuse.'),
  ('ACL', 'ACL / ARR REVIEW GUIDANCE

Source: https://aclrollingreview.org/reviewerguidelines

ARR separates two judgements that reviewers routinely conflate:
- Soundness: are the claims properly supported by the methodology and
  evidence? This is the primary score. Maps to Technical Soundness,
  Experimental Soundness, and Coherence Between Claims and Experiments.
- Excitement: how much the work moves the field. Explicitly orthogonal to
  soundness, and more subjective. Maps to Significance and Originality.

A paper can be entirely sound and unexciting, or exciting and unsound. Score
those separately rather than letting one contaminate the other.

Every soundness judgement must be justified in the text of the review. An
unsupported score is itself a review defect.

ARR maintains an explicit list of reviewing failures. Do not:
- Penalise a result for seeming obvious in retrospect
- Dismiss findings that contradict your expectations
- Assert a lack of novelty without citing the prior work you mean
- Penalise work precisely because it is unprecedented
- Require state-of-the-art results
- Reject negative results
- Dismiss a solution for being simple
- Insist on the methodology you would personally have chosen
- Undervalue work on niche topics or languages other than English
- Over-penalise non-native English phrasing, as distinct from genuine
  incomprehensibility
- Demand experiments that are not needed to support the paper''s claims
- Require comparison against closed models without justification
- Treat an honest limitations section as a weakness
- Use citation counts as a proxy for validity

Write in a neutral, professional register. Sarcasm and dismissiveness are
review defects regardless of whether the criticism is correct.'),
  ('NeurIPS', 'NeurIPS 2026 REVIEW GUIDANCE

Source: https://neurips.cc/Conferences/2026/ReviewerGuidelines

NeurIPS applies four criteria to every submission:
- Quality: is the submission technically sound, and are the claims well
  supported by theoretical analysis or experimental results? Maps to
  Technical Soundness, Experimental Soundness, and Coherence Between Claims
  and Experiments.
- Clarity: is it clearly written and well organised, and does it adequately
  inform the reader? Maps to Clarity.
- Significance: are the results impactful, and are others likely to use these
  ideas or build on them? Maps to Significance.
- Originality: does the work provide new insight, deepen understanding, or
  highlight important properties of existing methods? Maps to Originality.

Note the wording of Originality. Deepening understanding of a method that
already exists counts. A careful analysis that explains why something works is
original in the sense NeurIPS means, even when it proposes nothing new.

Identify what kind of contribution the paper makes and judge it on its own
terms. NeurIPS recognises several, and the standards differ:
- Theory: value lies in the strength and generality of results and the rigour
  of the proofs. Do not demand large-scale experiments.
- Use-inspired: value lies in addressing a real problem well. Judge the fit
  between method and application.
- Concept and feasibility: value lies in showing a new idea is possible.
  Preliminary evidence can be sufficient.
- Negative results: value lies in a well-designed study that credibly rules
  something out. Do not penalise the direction of the finding.

Judging a theory paper by an empirical paper''s standards, or a feasibility
study by a mature system''s standards, is a reviewing error.

Assess whether limitations are acknowledged honestly and whether the work
raises ethical concerns that deserve explicit discussion.'),
  ('ICLR', 'ICLR REVIEW GUIDANCE

Source: https://iclr.cc/Conferences/2025/ReviewerGuide

ICLR frames reviewing as four questions. Answer each explicitly:
1. What specific question or problem does the paper address?
2. Is the approach well motivated, and well positioned with respect to
   existing literature?
3. Do the results support the claims? Are they correct and scientifically
   rigorous?
4. What is the significance of the work? Does it contribute new, relevant and
   impactful knowledge?

Question 2 maps to Originality and Clarity, question 3 to Technical
Soundness, Experimental Soundness and Coherence Between Claims and
Experiments, and question 4 to Significance.

ICLR states directly that a lack of state-of-the-art results does not by
itself constitute grounds for rejection. Do not reduce scores because a
method fails to beat a leaderboard. Ask instead whether the claims made are
supported by the evidence presented.

Begin by summarising the paper''s claimed contributions in a positive register,
then give a comprehensive account of strong and weak points. State a clear
recommendation and the main reasons for it, supported by argument rather than
assertion.

Separate genuine questions from criticisms. A question is something the
authors could resolve in a rebuttal; a criticism is a judgement you have
already reached. Conflating them wastes the rebuttal.

Be constructive in tone and open-minded about value to the community beyond
your own research interests. A paper need not be interesting to you to be
worth accepting.')
)
insert into conferences (name, guidelines)
select i.name, i.guidelines
from incoming i
where not exists (select 1 from conferences c where c.name = i.name);

update conferences c
set guidelines = i.guidelines
from (
  values
  ('ICML', 'ICML 2026 REVIEW GUIDANCE

Source: https://icml.cc/Conferences/2026/ReviewerInstructions

ICML assesses four dimensions. Weigh the pipeline''s six scores against them:
- Soundness: technical correctness, appropriate methodology, quality of the
  evidence offered for each claim. Maps to Technical Soundness and
  Experimental Soundness.
- Presentation: clarity of writing, structure, and how well the work is
  situated in existing literature. Maps to Clarity.
- Significance: relevance of the problem and likely impact on the field.
  Maps to Significance.
- Originality: new insights, new methods or tasks, or a creative combination
  of existing techniques. Maps to Originality.

ICML''s own overall scale runs 1-6, where 6 is a technically flawless paper
with exceptional impact, 4 is technically solid with some weaknesses, 3 means
clear merits that are outweighed by weaknesses, and 1 is a well-known result
or an incomprehensible contribution. Calibrate the /10 final score to that
shape: reserve the top band for work that is both technically solid and high
impact, not merely competent.

Judge the paper on soundness first. A well-written paper with an unsupported
central claim is not a strong paper. Conversely, a technically correct result
that is poorly presented should lose points on Clarity, not on Soundness.

Ask 3-5 specific, numbered questions the authors could actually answer in a
rebuttal. Vague dissatisfaction is not a question.

Assess whether the authors acknowledge their own limitations honestly, and
whether societal impact is addressed where the work warrants it. Flag ethics
concerns explicitly: bias, privacy, research integrity, or applications open
to misuse.'),
  ('ACL', 'ACL / ARR REVIEW GUIDANCE

Source: https://aclrollingreview.org/reviewerguidelines

ARR separates two judgements that reviewers routinely conflate:
- Soundness: are the claims properly supported by the methodology and
  evidence? This is the primary score. Maps to Technical Soundness,
  Experimental Soundness, and Coherence Between Claims and Experiments.
- Excitement: how much the work moves the field. Explicitly orthogonal to
  soundness, and more subjective. Maps to Significance and Originality.

A paper can be entirely sound and unexciting, or exciting and unsound. Score
those separately rather than letting one contaminate the other.

Every soundness judgement must be justified in the text of the review. An
unsupported score is itself a review defect.

ARR maintains an explicit list of reviewing failures. Do not:
- Penalise a result for seeming obvious in retrospect
- Dismiss findings that contradict your expectations
- Assert a lack of novelty without citing the prior work you mean
- Penalise work precisely because it is unprecedented
- Require state-of-the-art results
- Reject negative results
- Dismiss a solution for being simple
- Insist on the methodology you would personally have chosen
- Undervalue work on niche topics or languages other than English
- Over-penalise non-native English phrasing, as distinct from genuine
  incomprehensibility
- Demand experiments that are not needed to support the paper''s claims
- Require comparison against closed models without justification
- Treat an honest limitations section as a weakness
- Use citation counts as a proxy for validity

Write in a neutral, professional register. Sarcasm and dismissiveness are
review defects regardless of whether the criticism is correct.'),
  ('NeurIPS', 'NeurIPS 2026 REVIEW GUIDANCE

Source: https://neurips.cc/Conferences/2026/ReviewerGuidelines

NeurIPS applies four criteria to every submission:
- Quality: is the submission technically sound, and are the claims well
  supported by theoretical analysis or experimental results? Maps to
  Technical Soundness, Experimental Soundness, and Coherence Between Claims
  and Experiments.
- Clarity: is it clearly written and well organised, and does it adequately
  inform the reader? Maps to Clarity.
- Significance: are the results impactful, and are others likely to use these
  ideas or build on them? Maps to Significance.
- Originality: does the work provide new insight, deepen understanding, or
  highlight important properties of existing methods? Maps to Originality.

Note the wording of Originality. Deepening understanding of a method that
already exists counts. A careful analysis that explains why something works is
original in the sense NeurIPS means, even when it proposes nothing new.

Identify what kind of contribution the paper makes and judge it on its own
terms. NeurIPS recognises several, and the standards differ:
- Theory: value lies in the strength and generality of results and the rigour
  of the proofs. Do not demand large-scale experiments.
- Use-inspired: value lies in addressing a real problem well. Judge the fit
  between method and application.
- Concept and feasibility: value lies in showing a new idea is possible.
  Preliminary evidence can be sufficient.
- Negative results: value lies in a well-designed study that credibly rules
  something out. Do not penalise the direction of the finding.

Judging a theory paper by an empirical paper''s standards, or a feasibility
study by a mature system''s standards, is a reviewing error.

Assess whether limitations are acknowledged honestly and whether the work
raises ethical concerns that deserve explicit discussion.'),
  ('ICLR', 'ICLR REVIEW GUIDANCE

Source: https://iclr.cc/Conferences/2025/ReviewerGuide

ICLR frames reviewing as four questions. Answer each explicitly:
1. What specific question or problem does the paper address?
2. Is the approach well motivated, and well positioned with respect to
   existing literature?
3. Do the results support the claims? Are they correct and scientifically
   rigorous?
4. What is the significance of the work? Does it contribute new, relevant and
   impactful knowledge?

Question 2 maps to Originality and Clarity, question 3 to Technical
Soundness, Experimental Soundness and Coherence Between Claims and
Experiments, and question 4 to Significance.

ICLR states directly that a lack of state-of-the-art results does not by
itself constitute grounds for rejection. Do not reduce scores because a
method fails to beat a leaderboard. Ask instead whether the claims made are
supported by the evidence presented.

Begin by summarising the paper''s claimed contributions in a positive register,
then give a comprehensive account of strong and weak points. State a clear
recommendation and the main reasons for it, supported by argument rather than
assertion.

Separate genuine questions from criticisms. A question is something the
authors could resolve in a rebuttal; a criticism is a judgement you have
already reached. Conflating them wastes the rebuttal.

Be constructive in tone and open-minded about value to the community beyond
your own research interests. A paper need not be interesting to you to be
worth accepting.')
) as i(name, guidelines)
where c.name = i.name;

select id, name, length(guidelines) as guidelines_chars
from conferences order by name;
