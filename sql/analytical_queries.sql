-- R1: Hiring Trends
SELECT d.year, d.month, COUNT(*) AS applications,
       SUM(f.is_hired) AS hired,
       ROUND(100.0 * SUM(f.is_hired) / COUNT(*), 2) AS hiring_rate
FROM fact_applications f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- R2: Technology Analysis
SELECT t.technology_name, COUNT(*) AS applications,
       SUM(f.is_hired) AS hired,
       ROUND(100.0 * SUM(f.is_hired) / COUNT(*), 2) AS hiring_rate
FROM fact_applications f
JOIN dim_technology t ON f.technology_key = t.technology_key
GROUP BY t.technology_name
ORDER BY hiring_rate DESC;

-- R3: Candidate Profile Analysis
SELECT p.seniority, p.yoe_range, COUNT(*) AS applications,
       ROUND(100.0 * SUM(f.is_hired) / COUNT(*), 2) AS hiring_rate
FROM fact_applications f
JOIN dim_candidate_profile p ON f.profile_key = p.profile_key
GROUP BY p.seniority, p.yoe_range;

-- R4: Geographic Recruitment Analysis
SELECT c.country_name, COUNT(*) AS applications,
       ROUND(100.0 * SUM(f.is_hired) / COUNT(*), 2) AS hiring_rate
FROM fact_applications f
JOIN dim_country c ON f.country_key = c.country_key
GROUP BY c.country_name
ORDER BY applications DESC;

-- R5: Assessment Performance Analysis
SELECT is_hired,
       ROUND(AVG(code_challenge_score), 2) AS avg_code_challenge,
       ROUND(AVG(technical_interview_score), 2) AS avg_interview
FROM fact_applications
GROUP BY is_hired;