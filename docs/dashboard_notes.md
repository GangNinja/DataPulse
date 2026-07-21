# Week 4 Dashboard Notes

## Repository Health Score Interpretation

The Week 3 health score currently uses max-based normalization:

```text
repo_value / max_value_in_database * 100
```

This makes the health score a relative ranking across all stored repositories.
When the database contains a very large repository, most smaller repositories
can receive low normalized scores even when they are useful or recently updated.

Example from the Microsoft ingestion run:

```text
Max stars:    196,012
Max forks:     75,264
Max watchers: 196,012
```

A repository with 100 stars, 20 forks, and 100 watchers receives very small
normalized popularity values because it is compared with the largest repository
in the dataset.

## Dashboard Reminder

When building the dashboard, show a short explanation that the health score is a
relative score, not an absolute quality judgment.

Helpful dashboard additions:

- Health score tooltip explaining normalization.
- Score distribution chart.
- Category counts for Excellent, Very Good, Good, Average, and Needs Attention.
- Top healthiest repositories table.
- Repositories needing attention table.

## Possible Week 4 Improvement

Consider log scaling for popularity metrics:

```text
log(1 + repo_value) / log(1 + max_value) * 100
```

Log scaling would keep scores between 0 and 100 while preventing one very large
repository from pushing most smaller repositories below 20.

Do not change the scoring formula silently. If log scaling is added later,
document it clearly in the dashboard and README.
