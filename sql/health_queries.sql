-- DataPulse Week 3 repository health queries

-- 1. Top 10 healthiest repositories
SELECT
    r.owner,
    r.repo_name,
    rh.health_score,
    rh.health_category
FROM repository_health AS rh
JOIN repositories AS r ON r.id = rh.repository_id
ORDER BY rh.health_score DESC, r.stars DESC
LIMIT 10;

-- 2. Average health score
SELECT ROUND(AVG(health_score)::numeric, 2) AS average_health_score
FROM repository_health;

-- 3. Health score distribution
SELECT
    health_category,
    COUNT(*) AS repository_count
FROM repository_health
GROUP BY health_category
ORDER BY repository_count DESC;

-- 4. Repositories needing attention
SELECT
    r.owner,
    r.repo_name,
    r.stars,
    r.forks,
    r.watchers,
    rh.health_score
FROM repository_health AS rh
JOIN repositories AS r ON r.id = rh.repository_id
WHERE rh.health_category = 'Needs Attention'
ORDER BY rh.health_score ASC, r.updated_at ASC
LIMIT 50;

-- 5. Health score by language
SELECT
    COALESCE(r.language, 'No Language') AS language,
    ROUND(AVG(rh.health_score)::numeric, 2) AS average_health_score,
    COUNT(*) AS repository_count
FROM repository_health AS rh
JOIN repositories AS r ON r.id = rh.repository_id
GROUP BY COALESCE(r.language, 'No Language')
ORDER BY average_health_score DESC;

-- 6. Health category by language
SELECT
    COALESCE(r.language, 'No Language') AS language,
    rh.health_category,
    COUNT(*) AS repository_count
FROM repository_health AS rh
JOIN repositories AS r ON r.id = rh.repository_id
GROUP BY COALESCE(r.language, 'No Language'), rh.health_category
ORDER BY language, repository_count DESC;

-- 7. Repositories with strong popularity but low recent activity
SELECT
    r.owner,
    r.repo_name,
    r.stars,
    r.forks,
    r.watchers,
    r.updated_at,
    rh.health_score,
    rh.health_category
FROM repository_health AS rh
JOIN repositories AS r ON r.id = rh.repository_id
WHERE r.stars >= 1000
  AND rh.health_category IN ('Average', 'Needs Attention')
ORDER BY r.stars DESC
LIMIT 25;

-- 8. Recently refreshed health rows
SELECT
    r.owner,
    r.repo_name,
    rh.health_score,
    rh.health_category,
    rh.created_at
FROM repository_health AS rh
JOIN repositories AS r ON r.id = rh.repository_id
ORDER BY rh.created_at DESC
LIMIT 20;
