# Workshop 1 — From Business Requirements to a Dimensional Data Warehouse

**Course:** ETL (G01) — Data Engineering and Artificial Intelligence
**Universidad Autónoma de Occidente**

---

## 1. Project Objective

The objective of this project is not simply to build a Data Warehouse, but to design and
implement a complete **analytical data system** that transforms raw candidate application
data into a **Dimensional Data Warehouse** capable of answering specific business
questions and supporting recruitment decisions.

The project follows the engineering workflow:

```
Business Requirements → Data Understanding → Dimensional Modeling → ETL →
Data Warehouse → Analytics → Business Decisions
```

---

## 2. Business Context

A technology recruitment company receives thousands of candidate applications from
different countries, seniority levels, technologies, and experience backgrounds. Each
candidate is evaluated through two technical assessments:

- **Code Challenge Score**
- **Technical Interview Score**

Currently, this information only exists as raw application data. The company needs an
analytical system that allows decision-makers to understand hiring patterns and evaluate
recruitment performance from multiple perspectives (time, technology, geography, and
candidate profile).

**Hiring business rule:**

```
HIRED = (Code Challenge Score >= 7) AND (Technical Interview Score >= 7)
Otherwise: NOT HIRED
```

This rule is applied during the ETL transformation step, not in the source data.

---

## 3. Business Requirements

| ID | Business Requirement | Business Question | Decision Supported |
|----|----------------------|--------------------|---------------------|
| **R1** | Hiring Trends | How have hiring outcomes changed across different time periods? | Identify whether recruitment performance is improving, worsening, or stable, to adjust recruitment planning over time. |
| **R2** | Technology Analysis | Which technologies generate the largest number and highest proportion of hired candidates? | Prioritize sourcing and recruitment effort toward technologies with better hiring outcomes. |
| **R3** | Candidate Profile Analysis | How do hiring outcomes differ across candidate seniority levels and years of experience? | Adjust recruitment criteria or expectations per seniority/experience segment. |
| **R4** | Geographic Recruitment Analysis | Which countries generate the highest volume of applications, and how does their hiring success rate compare? | Prioritize sourcing investment in countries with strong volume **and** high hiring success, and re-evaluate strategy in countries with high volume but low success. |
| **R5** | Assessment Score Pattern Analysis | Is there a meaningful difference between Code Challenge and Technical Interview performance, and does one assessment disqualify more candidates than the other? | Determine whether the recruitment process should adjust the difficulty, weighting, or preparation support for a specific assessment stage. |

> **Note:** R4 and R5 are proposed requirements for this project, meeting the criteria of
> being analytical, decision-oriented, answerable with the available data, and distinct
> from R1–R3.

---

## 4. Requirements Traceability

| Requirement | Business Question | Data Required | Expected Analytical Output |
|---|---|---|---|
| **R1** | How have hiring outcomes changed across different time periods? | Application Date, Hiring Outcome | Number/rate of hires per month or year (trend over time) |
| **R2** | Which technologies generate the most and the highest proportion of hires? | Technology, Hiring Outcome | Ranking of technologies by hire count and hire rate (%) |
| **R3** | How do hiring outcomes differ by seniority and years of experience? | Seniority, YOE, Hiring Outcome | Hire rate broken down by seniority level and YOE range |
| **R4** | Which countries generate the highest application volume, and how do their hiring rates compare? | Country, Hiring Outcome | Ranking of countries by application volume and hire rate |
| **R5** | Is there a meaningful gap between the two assessment scores among hired vs. not-hired candidates? | Code Challenge Score, Technical Interview Score, Hiring Outcome | Distribution/average comparison of each score by hiring outcome, and identification of which assessment disqualifies more candidates |

---

## 5. Dataset Description

The source dataset (`candidates.csv`) contains **50,000 candidate applications**, where
each row represents one application to a technical position.

**Attributes:**

| Column | Description |
|---|---|
| First Name | Candidate's first name |
| Last Name | Candidate's last name |
| Email | Candidate's email |
| Application Date | Date the application was submitted |
| Country | Candidate's country |
| YOE | Years of professional experience |
| Seniority | Candidate seniority level |
| Technology | Technology/profile the candidate applied for |
| Code Challenge Score | Score obtained in the code challenge (0–10) |
| Technical Interview Score | Score obtained in the technical interview (0–10) |

### Main Profiling Findings

- **Rows / Columns:** 50,000 rows × 10 columns.
- **Missing values:** none found in any column.
- **Duplicate records:** none found.
- **Unique countries:** 244.
- **Seniority levels (7):** Intern, Trainee, Junior, Mid-Level, Senior, Lead, Architect.
- **Unique technologies:** 24.
- **Application Date range:** 2018-01-01 to 2022-07-04.
- **YOE range:** 0 to 30 years.
- **Code Challenge Score range:** 0 to 10.
- **Technical Interview Score range:** 0 to 10.

These findings confirm the dataset is clean enough (no nulls, no duplicates) to move
directly into dimensional modeling, with minimal data preparation required (mainly type
casting for the date column and applying the hiring business rule).

---

## 6. Business Process

**Business process:** *Candidate Application Evaluation* — within the technical
recruitment pipeline, the process in which a candidate applies for a position, is
scored through two technical assessments (Code Challenge and Technical Interview),
and receives a hiring outcome (HIRED / NOT HIRED).

**Justification:** All five business requirements (R1–R5) analyze this exact process
from different angles — time (R1), technology (R2), candidate profile (R3), geography
(R4), and assessment behavior (R5) — but they all ultimately measure the same
underlying event: *an application being evaluated and resolved into a hiring outcome*.
Modeling any other process (e.g., "candidate lifecycle" or "interview scheduling")
would not be supported by the available data.

---

## 7. Grain Definition

> **One row in `fact_applications` represents one individual candidate application** —
> i.e., one candidate, applying for one technology profile, on one application date,
> with its corresponding Code Challenge Score, Technical Interview Score, and derived
> hiring outcome.

This grain is consistent with the source data (each row in `candidates.csv` is already
one application) and is fine enough to support all five requirements, since none of
them require a coarser or finer level of detail (e.g., no requirement needs
per-question or per-interviewer detail).

---

## 8. Star Schema Diagram

![Star Schema](diagrams/star_schema.png)

The model follows a classic Star Schema: one central fact table
(`fact_applications`) connected to four dimension tables, each with its own
surrogate key. Diagram generated from the DBML definition in
`diagrams/star_schema.dbml` using [dbdiagram.io](https://dbdiagram.io).

---

## 9. Explanation of Dimensions and Facts

### Dimensions

| Dimension | Purpose | Main Attributes | Requirement(s) Supported |
|---|---|---|---|
| **dim_date** | Provides temporal context to analyze hiring trends over time. | `date_key (PK)`, `full_date`, `day`, `month`, `quarter`, `year` | R1 |
| **dim_technology** | Groups applications by the technology profile applied for. | `technology_key (PK)`, `technology_name` | R2 |
| **dim_seniority** | Groups applications by candidate seniority level, with a logical (non-alphabetical) order. | `seniority_key (PK)`, `seniority_name`, `seniority_order` | R3 |
| **dim_country** | Groups applications by candidate country for geographic analysis. | `country_key (PK)`, `country_name` | R4 |

`YOE` (years of experience) and the two assessment scores were **deliberately not**
turned into dimensions: they are continuous numeric attributes, not low-cardinality
categorical values, so they stay as descriptive attributes in the fact table. This
keeps them flexible for grouping/bucketing at query time instead of locking in a
bucket definition at modeling time.

### Facts / Measures

| Measure | Meaning | Source / Calculation | Requirement(s) Supported | Additive? |
|---|---|---|---|---|
| `is_hired` | Whether the application resulted in a hire | Derived: `(Code Challenge Score >= 7) AND (Technical Interview Score >= 7)` | R1, R2, R3, R4, R5 | Yes — can be `SUM`'d to get total hires, or `AVG`'d to get hire rate |
| `application_count` | Number of applications | Implicit — `COUNT(*)` over `fact_applications` | R1, R2, R3, R4 | Yes |
| `code_challenge_score` | Score obtained in the code challenge (0–10) | Source column | R5 | **No** — use `AVG`, not `SUM` |
| `technical_interview_score` | Score obtained in the technical interview (0–10) | Source column | R5 | **No** — use `AVG`, not `SUM` |
| `yoe` | Candidate's years of professional experience | Source column | R3 | **No** — use `AVG` or bucket into ranges |

### Step 6 — Model Validation Against Requirements

| Requirement | Dimension(s) Required | Measure(s) Required | Supported? |
|---|---|---|---|
| R1 | dim_date | is_hired, application_count | Yes |
| R2 | dim_technology | is_hired, application_count | Yes |
| R3 | dim_seniority | yoe, is_hired | Yes |
| R4 | dim_country | is_hired, application_count | Yes |
| R5 | *(none needed)* | code_challenge_score, technical_interview_score, is_hired | Yes |

All five requirements are covered by the current model — no additional dimensions or
measures are required at this stage.

---

## 10. ETL Architecture

The pipeline follows a strict **ETL** approach (transform before load), orchestrated
by `src/main.py`:

![ETL Architecture](diagrams/etl_architecture.png)

Each module has a single responsibility (Extract / Prepare+Transform /
Dimensional Modeling / Load), which keeps the pipeline reproducible and testable
in isolation — matching the folder structure under `src/`. `load.py` also handles
creating the database and schema automatically (`ensure_database_exists()`,
`create_schema()`) and resetting the tables before each run (`reset_tables()`), so
`main.py` can be executed repeatedly without manual setup in MySQL Workbench.

## 11. Main Transformation Decisions

Decisions applied in `transform.py`, and why:

| Decision | Reasoning |
|---|---|
| `Application Date` cast to `datetime` | Needed to build `dim_date` and to group by year/month/quarter for R1. |
| Text columns (`Country`, `Seniority`, `Technology`, names, email) stripped of extra whitespace | Prevents accidental duplicate dimension members (e.g., `"Spain"` vs `"Spain "` becoming two different `dim_country` rows). |
| `YOE` and both scores cast explicitly to numeric | Guards against the pipeline silently treating them as text if the source format ever changes. |
| Null/duplicate handling kept defensive, not hardcoded | Initial profiling confirmed 0 nulls and 0 duplicates, but `prepare_data()` still checks and would drop them if a future data refresh introduced any — without assuming the current clean state will always hold. |
| `is_hired` computed as `(Code Challenge Score >= 7) AND (Technical Interview Score >= 7)` | Exact business rule from Section 5.1 of the assignment. Implemented as a boolean so it's directly usable both as a filter and as an additive measure (`SUM(is_hired)` = total hires). |
| `YOE` ranges (e.g., `0-2`, `3-5`, ...) computed **at query time** in SQL, not stored as a new column | Keeps the fact table grain clean and avoids baking a bucket definition into the ETL that analysts might want to change later (see README section 9). |
| No additional derived columns created | R4 and R5 are fully answerable with existing attributes (`Country`, both scores, `is_hired`) — creating extra columns "just in case" would violate the assignment's instruction to avoid transformations without analytical purpose. |

## 12. Technologies

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Data manipulation | Pandas |
| Initial profiling | Jupyter Notebook |
| Data Warehouse | **MySQL 8+** |
| DB driver (Python) | PyMySQL (via SQLAlchemy) |
| Version control | Git + GitHub |
| BI Visualization | Power BI / Tableau / Looker Studio (connected directly to MySQL) |

**Why MySQL over PostgreSQL:** both are valid per the assignment; MySQL was chosen to
keep the local setup simpler, using **MySQL Server + MySQL Workbench** as the local
Data Warehouse environment. `PyMySQL` is used as the Python driver — it's a pure-Python
implementation, so it doesn't require a system-level compiler or extra OS packages to
install, unlike `psycopg2` for PostgreSQL.

---

## 13. Instructions to Run the Project

### 13.1 Prerequisites
- Python 3.10+
- MySQL Server installed and running locally, administered with MySQL Workbench
- The `root` password you defined during MySQL Server installation (or a dedicated ETL user)

### 13.2 Set up the Python environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 13.3 Configure the database connection
```bash
cp .env.example .env
# Edit .env and set DB_USER / DB_PASSWORD to your real MySQL Server credentials
```

### 13.4 Run the initial profiling (optional but recommended)
```bash
jupyter notebook notebooks/data_profiling.ipynb
```

### 13.5 Run the ETL pipeline
```bash
python src/main.py
```
This single command runs the full pipeline end to end:
Extract → Prepare/Transform → Dimensional Modeling → **create the `recruitment_dw`
database and schema if they don't exist yet** → reset tables → Load dimensions →
Load fact table → validate referential integrity and row counts.

No manual step in MySQL Workbench is required — `src/load.py` creates the database
and runs `sql/create_tables.sql` automatically the first time it's executed. That SQL
file is still kept in the repo as the schema's source of truth / for manual reference,
but the pipeline no longer depends on it being run by hand. The script can be re-run
safely at any time; it truncates and reloads the tables instead of duplicating rows.

### 13.6 Run the analytical queries
Open `sql/analytical_queries.sql` in MySQL Workbench (connected to `recruitment_dw`)
and run each query to get the R1–R5 analytical outputs.

### 13.7 Connect the BI tool
Point your BI tool (Power BI / Tableau / Looker Studio) directly at the
`recruitment_dw` MySQL database to build the required visualizations.

## 14. Analytical Queries and KPIs

All results below were generated directly from the Data Warehouse (`fact_applications` joined with its dimensions), using the queries in `sql/analytical_queries.sql`.

### R1 — Hiring Trends

**Business question:** How have hiring outcomes changed over time?

| Year | Applications | Hires | Hire Rate % |
|---|---|---|---|
| 2018 | 11,061 | 1,409 | 12.74% |
| 2019 | 11,009 | 1,524 | 13.84% |
| 2020 | 11,237 | 1,485 | 13.22% |
| 2021 | 11,051 | 1,485 | 13.44% |
| 2022* | 5,642 | 795 | 14.09% |

*2022 is a partial year (data goes up to 2022-07-04).

**Interpretation:** The hire rate has stayed in a narrow band (~12.7%–14.1%) across five years, with a slight upward trend since 2018. There's no dramatic swing — recruitment outcomes have been relatively stable, which suggests hiring standards/process haven't shifted much year over year.

### R2 — Technology Analysis

**Business question:** Which technologies generate the largest number and highest proportion of hired candidates?

| Technology | Applications | Hires | Hire Rate % |
|---|---|---|---|
| Game Development | 3,818 | 519 | 13.59% |
| DevOps | 3,808 | 495 | 13.00% |
| System Administration | 2,014 | 293 | 14.55% |
| Development - CMS Backend | 1,882 | 284 | 15.09% |
| Database Administration | 1,933 | 282 | 14.59% |

**Interpretation:** *Game Development* and *DevOps* produce the largest absolute number of hires simply because they receive the most applications — but their hire *rate* (13.0–13.6%) is actually below several smaller technologies. *Development - CMS Backend* has both solid volume and the best hire rate (15.09%) among the top 5, making it the strongest combination of volume + quality for sourcing investment.

### R3 — Candidate Profile Analysis

**Business question:** How do hiring outcomes differ by seniority and years of experience?

**By seniority level:**

| Seniority | Applications | Hires | Hire Rate % |
|---|---|---|---|
| Intern | 7,255 | 985 | 13.58% |
| Trainee | 7,183 | 973 | 13.55% |
| Junior | 7,100 | 977 | 13.76% |
| Mid-Level | 7,253 | 924 | 12.74% |
| Senior | 7,059 | 939 | 13.30% |
| Lead | 7,071 | 929 | 13.14% |
| Architect | 7,079 | 971 | 13.72% |

**By years of experience (YOE):**

| YOE Range | Applications | Hires | Hire Rate % |
|---|---|---|---|
| 0-2 | 4,063 | 574 | 14.13% |
| 3-5 | 4,993 | 652 | 13.06% |
| 6-10 | 8,185 | 1,055 | 12.89% |
| 11-15 | 8,052 | 1,108 | 13.76% |
| 16-20 | 8,094 | 1,097 | 13.55% |
| 21+ | 16,613 | 2,212 | 13.31% |

**Interpretation:** Hire rate is remarkably flat across both seniority (12.7%–13.8%) and YOE ranges (12.9%–14.1%) — seniority and experience, on their own, don't meaningfully predict a candidate's chance of being hired in this dataset. This is a useful (if counter-intuitive) finding: it suggests the two technical assessments are the real gatekeepers, not the candidate's declared background.

### R4 — Geographic Recruitment Analysis

**Business question:** Which countries generate the highest application volume, and how does their hiring success rate compare?

| Country | Applications | Hires | Hire Rate % |
|---|---|---|---|
| Malawi | 242 | 23 | 9.50% |
| Spain | 238 | 31 | 13.03% |
| Cook Islands | 234 | 28 | 11.97% |
| Svalbard & Jan Mayen Islands | 234 | 26 | 11.11% |
| Netherlands Antilles | 234 | 29 | 12.39% |

*(Full ranking of the 244 countries in the DW; average ~205 applications/country.)*

**Interpretation:** Application volume is spread very evenly across 244 countries (~205 applications each on average, with the top country at only 242) — there's no single dominant sourcing market. However, hire rate does vary meaningfully: **Malawi**, despite being the top country by volume, has the lowest hire rate in the top 5 (9.50%), while **Malaysia** (not in the top-5-by-volume list but nearby) reaches 14.66%. This is exactly the kind of gap R4 was designed to surface — high volume does not guarantee high hiring success.

### R5 — Assessment Score Pattern Analysis

**Business question:** Is there a meaningful gap between the two assessments, and does one disqualify more candidates than the other?

| Outcome | Avg Code Challenge | Avg Technical Interview | Candidates |
|---|---|---|---|
| NOT HIRED | 4.45 | 4.47 | 43,302 |
| HIRED | 8.50 | 8.48 | 6,698 |

**Among NOT HIRED candidates (43,302 total):**
- Failed **only** the Code Challenge (Technical Interview ≥ 7): **11,571** (26.7%)
- Failed **only** the Technical Interview (Code Challenge ≥ 7): **11,534** (26.6%)
- Failed **both**: 20,197 (46.7%)

**Interpretation:** The two assessments behave almost identically — nearly the same average score in both groups, and almost the same number of candidates disqualified by each one individually (11,571 vs. 11,534). **Neither assessment is disproportionately harder or acting as the "real" bottleneck** — the hiring funnel is balanced. This is a reassuring finding for the recruitment process design: there's no evidence to justify reweighting or adjusting the difficulty of either stage.

---

## 15. Main Business Findings

1. **Hiring outcomes are stable over time** (R1): hire rate has stayed between 12.7% and 14.1% from 2018 to mid-2022, with a mild upward trend — no major disruption to recruitment performance.
2. **Volume ≠ quality in technology sourcing** (R2): the technologies with the most applications (Game Development, DevOps) are not the ones with the best hire rates. *Development - CMS Backend* offers the best combination of solid volume and top hire rate.
3. **Seniority and experience are weak predictors of hiring outcome** (R3): hire rate barely varies across seniority levels or YOE brackets (roughly 12.7%–14.1% in both cases) — the technical assessments appear to be the actual differentiator, not the candidate's declared background.
4. **Geographic volume is very evenly distributed, but hiring success is not** (R4): no country dominates application volume (~205 applications on average across 244 countries), yet hire rates range from under 10% to over 14% — a clear signal for where sourcing investment could be adjusted.
5. **The two technical assessments are balanced gatekeepers** (R5): Code Challenge and Technical Interview disqualify almost the exact same number of otherwise-qualified candidates (11,571 vs. 11,534) — there's no evidence either stage needs to be recalibrated relative to the other.

**Overall takeaway:** the organization's ~13.4% overall hire rate is driven primarily by assessment performance rather than by *who* is applying (seniority, experience, country). This reframes where recruitment strategy could have the most impact — e.g., candidate preparation/screening before the assessments, rather than targeting specific seniority levels or geographies.

---

## 16. Final Requirements Validation

| Requirement | Implemented? | DW Tables Used | Query / KPI | Main Finding |
|---|---|---|---|---|
| R1 | Yes | `fact_applications`, `dim_date` | Applications/hires/hire rate by year | Hire rate stable (~12.7%–14.1%), mild upward trend |
| R2 | Yes | `fact_applications`, `dim_technology` | Top 5 technologies by hires + hire rate | Volume leaders ≠ hire-rate leaders; CMS Backend best combo |
| R3 | Yes | `fact_applications`, `dim_seniority` | Hire rate by seniority + by YOE range | Seniority/experience barely affect hire rate |
| R4 | Yes | `fact_applications`, `dim_country` | Top 10 countries by volume + hire rate | Volume is even across countries; hire rate is not |
| R5 | Yes | `fact_applications` | Avg scores by outcome + disqualification breakdown | Both assessments disqualify almost equally — balanced funnel |

**Does the final Data Warehouse provide enough information to satisfy all five business requirements?**
Yes. Every requirement was answered directly from `fact_applications` joined with its dimensions, without needing to go back to the source CSV or an intermediate DataFrame.

**Does the dimensional model contain elements that are not justified by the analytical requirements?**
No. Each of the 4 dimensions (`dim_date`, `dim_technology`, `dim_seniority`, `dim_country`) maps to exactly one requirement's grouping need, and every fact table attribute (`yoe`, both scores, `is_hired`) is used by at least one requirement. No dimension or measure was added "just in case."

**What business decisions can now be supported by the implemented analytical system?**
- Prioritize sourcing/marketing spend toward technologies and countries with above-average hire rates, not just above-average volume (R2, R4).
- Stop over-indexing recruitment criteria on seniority or years of experience, since neither meaningfully predicts hiring outcome (R3) — assessment performance matters far more.
- Treat the two technical assessments as equally weighted gatekeepers; no immediate need to redesign either one, since they disqualify candidates at almost identical rates (R5).
- Monitor the year-over-year hire rate trend (R1) as an early signal if recruitment process changes start affecting outcomes.
