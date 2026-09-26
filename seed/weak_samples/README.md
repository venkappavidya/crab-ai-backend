# Synthetic weak submissions

Two deliberately poor papers, written for this repository, used to exercise the
reject path so the review screen shows a realistic spread rather than only
accepts.

They are synthetic on purpose. Seeding a real paper as a rejection would put a
low score and a "Reject" decision against work by named researchers who never
submitted to that venue, which would be unfair to them.

Each one carries recognisable weaknesses: claims with no supporting evidence,
no baselines, a single unreplicated run, no statistical treatment, related work
waved away rather than engaged with, and conclusions that outrun the results.

    python3 seed/seed_papers.py --conference ACL --count 2 --weak seed/weak_samples

Scored 1.4/10 and 1.2/10 against ACL guidance, both Reject.

The `.txt` files are the sources; the PDFs were produced from them with
`cupsfilter`. Edit the text and regenerate if you want different failure modes.
