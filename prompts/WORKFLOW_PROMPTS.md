# Workflow Prompts

# 00 — Project bootstrap

Inspect AGENTS.md and PROJECT_BRIEF.md first.

Then inspect the files currently available in data/raw/.

Set up the repository for an end-to-end product analytics project.

Create only the infrastructure that is currently justified.

Tasks:
- create the agreed project directory structure;
- create Python environment/dependency configuration;
- add an appropriate .gitignore;
- create empty documentation files where necessary;
- create initial notebooks;
- create testing infrastructure;
- verify that the environment works.

Do NOT perform the actual business analysis yet.

Do NOT select a business problem.

Do NOT modify raw data.

At the end:
1. show the resulting project structure;
2. explain briefly what each component is responsible for;
3. identify the next logical step.

---

# 01 — Dataset audit

Perform a technical audit of all source data in data/raw/.

You may autonomously inspect:
- files;
- tables;
- columns;
- data types;
- row counts;
- candidate keys;
- relationships;
- missing values;
- duplicates;
- date ranges;
- suspicious values;
- basic distributions;
- referential-integrity issues.

Create/update:

docs/data_dictionary.md

and create a reproducible audit in:

notebooks/01_data_audit.ipynb

Add automated checks for important data-quality assumptions when useful.

Do NOT select the business problem yet.

Do NOT perform an uncontrolled large EDA.

After the technical audit, give me a concise explanation of:

1. what business entities exist;
2. how they relate to one another;
3. what user/customer journey can potentially be reconstructed;
4. what important information is missing;
5. what kinds of product questions the data can and cannot answer.

Then STOP with:

## YOUR TURN

Ask me to identify potential directions for product investigation.

---

# 02 — Review my business directions

I will propose several possible business/product problems based on the dataset.

Do NOT choose one immediately.

For every direction I propose, evaluate:

- business relevance;
- whether the dataset can actually answer it;
- available metrics;
- risk of making unsupported causal claims;
- analytical depth;
- usefulness for a product-analytics portfolio;
- potential for follow-up hypotheses;
- potential for experiment design.

Challenge weak reasoning.

Then ask me which direction I would choose and why.

Only after my final choice:
- update PROJECT_BRIEF.md;
- update docs/decision_log.md.

---

# 03 — Metric design checkpoint

We have selected a business problem.

Do not calculate metrics yet.

Ask me first to define:

1. primary metric;
2. metric formula;
3. numerator;
4. denominator;
5. unit of analysis;
6. observation window;
7. diagnostic metrics;
8. relevant business guardrails.

Review my definitions as a senior product analyst.

Specifically search for denominator errors, cohort-definition problems, survivorship bias and mismatched observation windows.

After we agree on definitions:
- document them;
- implement reproducible calculations;
- add tests for important metric logic.

---

# 04 — Create analysis plan

Based on the selected business problem and agreed metrics, create a proposed investigation plan.

Do not run the full investigation yet.

Separate questions into:

A. descriptive questions;
B. segmentation questions;
C. analytical hypotheses requiring validation;
D. potential confounders;
E. statistical questions.

For each proposed step explain:
- what question it answers;
- why it is useful;
- what result would cause us to investigate further.

Show the plan to me for review.

Do not execute major new branches of analysis before the plan is approved.

After approval update:

docs/analysis_plan.md

---

# 05 — Execute next investigation step

Read the current analysis plan and decision log.

Execute only the next agreed investigation step.

Keep calculations reproducible.

Save meaningful SQL under sql/.
Move reusable Python logic to src/ when justified.
Save final-quality figures under reports/figures/.

After obtaining the result:

Do NOT immediately interpret it for me.

Show me the important evidence and stop with:

## YOUR TURN

Ask me:
"What do you think this result means, and what would you investigate next?"

After I answer, critique my interpretation.

---

# 06 — Hypothesis checkpoint

We observed an interesting pattern.

Before performing additional analysis, ask me to propose possible explanations for it.

Require me to separate:

1. explanations directly supported by current evidence;
2. plausible analytical hypotheses;
3. causal claims that cannot yet be supported.

After my response:

- challenge the hypotheses;
- identify potential confounders;
- identify selection effects;
- identify alternative explanations;
- propose validation approaches only after reviewing my reasoning.

Record accepted analytical hypotheses in the project documentation.

---

# 07 — Attack our conclusion

Act as a skeptical senior product analyst reviewing this project.

Try to invalidate our current conclusion.

Check for:

- wrong denominator;
- confounding;
- Simpson's paradox;
- survivorship bias;
- censoring;
- seasonality;
- cohort imbalance;
- data leakage;
- aggregation artifacts;
- missing data;
- outliers;
- multiple testing;
- observational-vs-causal confusion.

Do not invent dataset problems.

Use actual evidence from the project.

Rank identified threats by severity:

CRITICAL
IMPORTANT
MINOR

For CRITICAL and IMPORTANT issues, propose a way to test whether they materially affect the conclusion.

---

# 08 — Statistical validation

We have an analytical question that may require statistical inference.

Do not select the statistical test immediately.

First stop with:

## YOUR TURN

Ask me to define:

- population;
- sample/unit of analysis;
- parameter of interest;
- H0;
- H1;
- metric distribution or data-generating assumptions;
- candidate statistical approach.

Review my reasoning.

Then select/confirm the methodology.

Calculate:
- estimate;
- effect size;
- uncertainty/confidence interval where appropriate;
- test statistic/p-value where appropriate.

Clearly separate:

statistical significance
from
business significance.

Document assumptions and limitations.

---

# 09 — Product hypothesis

Based on the completed investigation, ask me to formulate product interventions.

Do not generate the final product hypothesis first.

Require this structure:

If we [change X]
for [target users]
then [metric Y] will [expected effect]
because [mechanism supported by our analysis].

Review whether the proposed mechanism is actually connected to the evidence.

Distinguish analytical evidence from assumptions.

Then help prioritize the hypotheses.

---

# 10 — A/B experiment checkpoint

Take the selected product hypothesis.

Do not design the entire experiment for me.

Ask me first to specify:

- experimental unit;
- randomization unit;
- control;
- treatment;
- H0;
- H1;
- primary metric;
- secondary metrics;
- guardrail metrics;
- alpha;
- power;
- MDE;
- sample-size approach;
- expected experiment duration;
- major experiment risks.

Review every choice.

After methodology is agreed:
- perform the sample-size calculations;
- document experiment design;
- create relevant simulation/calculation code;
- discuss SRM and experiment-quality checks.

---

# 11 — Dashboard design

Do not start coding the dashboard immediately.

First ask me:

1. who the dashboard is for;
2. which decisions it should support;
3. which metrics belong on the first screen;
4. which segmentation/filtering is useful;
5. which charts are actually actionable.

Challenge vanity metrics and redundant charts.

After requirements are agreed:
build the simplest useful dashboard.

Prefer clarity over visual complexity.

---

# 12 — Final project review

Perform a senior-level review of the entire analytics project.

Review:

- business framing;
- data quality;
- metric definitions;
- SQL;
- Python;
- statistics;
- analytical reasoning;
- visualizations;
- causal language;
- product recommendations;
- experiment design;
- reproducibility;
- documentation.

Do not silently rewrite major analytical decisions.

Create a review report categorized as:

BLOCKER
MAJOR
MINOR
OPTIONAL

Fix technical issues autonomously when safe.

For analytical issues, discuss them with me first.

---

# 13 — Portfolio packaging

Use only facts actually established in this repository.

Prepare:

1. GitHub README;
2. concise project summary;
3. methodology section;
4. key findings;
5. visualizations;
6. limitations;
7. proposed experiment;
8. technology stack.

Do not fabricate:
- company experience;
- production deployment;
- implemented experiments;
- business impact that was not measured.

Make the README understandable to a recruiter first and technically defensible to an analyst second.

---

# 14 — Interview defense

Act as an interviewer hiring a junior/middle product analyst.

Read the entire project first.

Interview me specifically about this project.

Start from:

"Расскажи про свой проект и какую бизнес-проблему ты решал."

Then dynamically ask follow-up questions based on my answers.

Focus on:

- why I selected the problem;
- why I selected the metric;
- denominators;
- cohort definitions;
- SQL;
- data quality;
- interpretation;
- correlation vs causation;
- statistics;
- alternative explanations;
- product hypotheses;
- A/B test design;
- limitations.

Do not provide the answer before I attempt it.

After each answer give a short assessment and continue drilling into weak areas.