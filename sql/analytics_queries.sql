-- DataPulse Week 2 analytics queries

-- 1. Top repositories by stars
SELECT owner, repo_name, stars
FROM repositories
ORDER BY stars DESC
LIMIT 10;

-- 2. Top repositories by forks
SELECT owner, repo_name, forks
FROM repositories
ORDER BY forks DESC
LIMIT 10;

-- 3. Top repositories by popularity score
SELECT owner, repo_name, popularity_score
FROM repository_metrics
ORDER BY popularity_score DESC
LIMIT 10;

-- 4. Most common primary languages
SELECT language, COUNT(*) AS repository_count
FROM repositories
WHERE language IS NOT NULL
GROUP BY language
ORDER BY repository_count DESC, language
LIMIT 10;

-- 5. Average stars by language
SELECT language, ROUND(AVG(stars), 2) AS average_stars
FROM repositories
WHERE language IS NOT NULL
GROUP BY language
ORDER BY average_stars DESC;

-- 6. Repositories created this year
SELECT owner, repo_name, created_at
FROM repositories
WHERE created_at >= DATE_TRUNC('year', CURRENT_DATE)
ORDER BY created_at DESC;

-- 7. Recently updated repositories
SELECT owner, repo_name, updated_at
FROM repositories
ORDER BY updated_at DESC
LIMIT 20;

-- 8. Repository age distribution
SELECT
    CASE
        WHEN repository_age_days < 365 THEN 'Under 1 year'
        WHEN repository_age_days < 1095 THEN '1 to 3 years'
        WHEN repository_age_days < 1825 THEN '3 to 5 years'
        ELSE '5+ years'
    END AS age_bucket,
    COUNT(*) AS repository_count
FROM repository_metrics
GROUP BY age_bucket
ORDER BY repository_count DESC;

-- 9. Largest organizations by repository count
SELECT owner, COUNT(*) AS repository_count
FROM repositories
GROUP BY owner
ORDER BY repository_count DESC, owner
LIMIT 10;

-- 10. Most active repositories by open issues
SELECT owner, repo_name, open_issues, updated_at
FROM repositories
ORDER BY open_issues DESC, updated_at DESC
LIMIT 10;

-- 11. Repositories with no primary language
SELECT owner, repo_name, stars, forks
FROM repositories
WHERE language IS NULL
ORDER BY stars DESC;

-- 12. Repository size category distribution
SELECT size_category, COUNT(*) AS repository_count
FROM repository_metrics
GROUP BY size_category
ORDER BY repository_count DESC;

-- 13. Language categories by popularity
SELECT
    language_category,
    ROUND(AVG(popularity_score)::numeric, 2) AS average_popularity_score,
    COUNT(*) AS repository_count
FROM repository_metrics
GROUP BY language_category
ORDER BY average_popularity_score DESC;

-- 14. Stale repositories not updated in the last year
SELECT rm.owner, rm.repo_name, rm.days_since_last_update, r.updated_at
FROM repository_metrics AS rm
JOIN repositories AS r ON r.id = rm.repository_id
WHERE rm.days_since_last_update >= 365
ORDER BY rm.days_since_last_update DESC;

-- 15. Best fork-to-star ratios for popular repositories
SELECT
    owner,
    repo_name,
    stars,
    forks,
    ROUND((forks::numeric / NULLIF(stars, 0)), 4) AS fork_to_star_ratio
FROM repositories
WHERE stars >= 100
ORDER BY fork_to_star_ratio DESC
LIMIT 20;

-- 16. Analytics rows that need refreshing
SELECT r.owner, r.repo_name, r.last_synced, rm.calculated_at
FROM repositories AS r
LEFT JOIN repository_metrics AS rm ON rm.repository_id = r.id
WHERE rm.calculated_at IS NULL OR rm.calculated_at < r.last_synced
ORDER BY r.last_synced DESC;
