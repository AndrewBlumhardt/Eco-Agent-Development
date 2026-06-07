# Final Project: AI Agent Development and Evaluation

## Project Overview

AI agents are a relatively new development paradigm in the enterprise. Best practices are emerging, but rapid increases in capabilities and new developments require creativity and new responsibilities from employees who want to bring agents into production.

The final project uses the skills learned in this course to propose, develop, and evaluate an AI agent. The goal is to build practical understanding across the full project lifecycle.

## Team Scenario

Your team has been tasked with building a new AI feature for your company. Leadership knows very little about AI, but faces pressure from the board to invest more in AI.

Your team includes:

| Role | Primary Responsibility |
| --- | --- |
| Product Manager (PM) | Business case, project planning, business artifacts, and presentation coordination |
| Data Engineer (DE) | Data pipeline and supporting technical artifacts |
| AI Engineer (AIE) | Agent definition, tracing, model comparison, and evaluation |

You may divide the roles distinctly or share responsibilities across the team. Because the AI Engineer role may require more work than the Data Engineer role, sharing AIE responsibilities may make sense.

## Project Goal

Develop a project plan and deliver a code-first AI agent for your company.

The project has two stages:

1. Project proposal
2. Agent deliverable

You may use Databricks, as in other course assignments, or another preferred agent-building solution. The solution must be code-first.

---

# Part A: Agent Deliverable, Technical Artifacts

## Required Technical Deliverables

### 1. Data Pipeline Notebook

- Owner: Data Engineer
- Submit a notebook that contains the data pipeline used by the agent.

### 2. Agent Definition Notebook

- Owner: AI Engineer
- Submit a notebook that shows the agent definition.
- Review the course rubric to confirm all agent requirements.

### 3. Traces and Evaluation Examples

- Owner: AI Engineer
- Provide five example traces that include evaluation of the agent.
- Traces must be presented through an established tracing provider.

Acceptable providers include:

- MLflow, used by default in Databricks
- Arize Phoenix
- LangSmith
- Braintrust
- Another established provider

## LLM Comparison Requirement

At least one of the five traces must compare two different LLMs within the agent on the same trace.

- Use the same task or input for both models.
- Compare performance.
- This comparison counts as one trace toward the five required traces.

## Evaluation Requirement

Evaluation may be completed through:

- An LLM judge, strongly encouraged
- Manual evaluation

Include commentary in a notebook cell that explains:

- How the agent performed
- What the evaluation showed
- How performance differed when using the two selected LLMs

## Graceful Rejection Requirement

Show two examples of the agent gracefully rejecting irrelevant user input.

## Agent Definition Requirement

The solution must fit the course definition of an agent. It must use:

- An LLM
- Relevant tools

Tools may include:

- MCP servers
- Custom functions
- Vector search indices
- Other relevant tools used by the agent

---

# Part B: Agent Deliverable, Business Artifacts

## Video Presentation Requirement

Submit a 10 to 15 minute video presentation.

- Owner: Product Manager
- Participation: Every team member must participate in the video.

## Presentation Content

The presentation must include the following sections.

### 1. Technical Solution Walkthrough

- Walk through the technical solution.
- Use the notebook for the technical walkthrough.
- Slides may be used for the remaining presentation content.
- A notebook may also be used for additional sections when easier.

### 2. Evaluation Process

Explain how the solution was evaluated.

Include:

- Example evaluations
- A description of how a human is involved in the evaluation process
- A comparison of agent performance across the selected LLMs

### 3. ROI Calculation for the Selected LLMs

Include an explicit return on investment calculation for the different LLMs selected.

Example scenario:

- LLM 1 costs twice as much as LLM 2.
- LLM 1 is 20% more effective than LLM 2.
- Calculate whether the additional effectiveness creates enough business value to justify the increased cost.

Your analysis should connect:

- Model cost
- Effectiveness difference
- Business value produced by the improvement
- Recommended model choice

### 4. Final Business Value

Describe the final business value of the solution.

Address:

- The problem the agent solves
- The expected benefit for the company
- The users or teams who would benefit
- How agent performance affects business value

### 5. Deployment Recommendation

Recommend how the agent would be deployed.

Note: Deployment is not required as part of the submitted solution.

### 6. Project Plan Deviations

If the team deviated from the original project plan, explain:

- What changed
- Why it changed
- How the change affected the final solution

### 7. Agent Quality Commentary

Provide clear commentary about the quality of the agent.

Address:

- Whether it exceeded expectations
- What it performed well
- What it performed poorly
- What the team learned while building and evaluating the agent

---

# Submission Requirements

By Day 7 of Week 7, submit the final project as:

- A file upload of the GitHub repository
- A file upload of the video presentation

---

# Deliverable Checklist

## Technical Artifacts

- [ ] Data pipeline notebook completed
- [ ] Agent definition notebook completed
- [ ] Agent uses an LLM and relevant tools
- [ ] Five evaluated traces included
- [ ] At least one trace compares two different LLMs on the same task
- [ ] Evaluation method documented
- [ ] Notebook commentary explains performance and model comparison
- [ ] Two irrelevant-input rejection examples included
- [ ] Traces displayed through an established provider

## Business Artifacts

- [ ] 10 to 15 minute video presentation recorded
- [ ] Every team member participates
- [ ] Technical solution walkthrough included
- [ ] Evaluation examples included
- [ ] Human involvement in evaluation described
- [ ] ROI calculation for the selected LLMs included
- [ ] Final business value described
- [ ] Deployment recommendation provided
- [ ] Any deviations from the original plan explained
- [ ] Opinionated quality assessment included

## Submission

- [ ] GitHub repository file uploaded
- [ ] Video presentation file uploaded
- [ ] Submitted by Day 7 of Week 7


## Grading Rubrik

Assignment 7.1 Final Team Project Scoring Rubric
Rubric Summary
Criterion	Weight	Maximum Points
Data Pipeline Code	10%	21 pts
Agent Code	25%	52.5 pts
Evaluation Examples	15%	31.5 pts
Video Presentation, No AI Usage	50%	105 pts
Total	100%	210 pts
Data Pipeline Code

Weight: 10%
Maximum Points: 21 pts

Rating	Points	Requirements
Meets or Exceeds Expectations	21 pts	Data pipeline code executes and extracts data needed for the use case.
Approaches Expectations	18.89 pts	Data pipeline code is incomplete or does not retrieve all data needed for the use case.
Below Expectations	17.23 pts	Data pipeline is incomplete and does not retrieve all data needed for the use case.
Inadequate Attempt	14.69 pts	Submission does not meet graduate-level standards.
Non-Performance	0 pts	Non-performance.
Agent Code

Weight: 25%
Maximum Points: 52.5 pts

Rating	Points	Requirements
Meets or Exceeds Expectations	52.5 pts	Agent code includes an LLM, at least two tools, is not missing obvious tools that would be useful for the agent, and can gracefully handle errors and out-of-scope user queries.
Approaches Expectations	47.23 pts	Agent code does not include an LLM, has only one tool, is missing obvious tools that would be useful for the agent, or cannot gracefully handle errors or out-of-scope queries.
Below Expectations	43.07 pts	Agent code does not include an LLM, is completely missing tools, or is missing any form of error handling.
Inadequate Attempt	36.73 pts	Submission does not meet graduate-level standards.
Non-Performance	0 pts	Non-performance.
Evaluation Examples

Weight: 15%
Maximum Points: 31.5 pts

Rating	Points	Requirements
Meets or Exceeds Expectations	31.5 pts	Five evaluation examples are shown, including at least one trace that uses different LLMs. A written description explains how the agent is performing.
Approaches Expectations	23.5 pts	Fewer than five evaluation examples are shown, a trace using different LLMs is missing, or the written description does not explain how the agent is performing.
Below Expectations	15.5 pts	Fewer than five evaluation examples are shown, a trace using different LLMs is missing, and the written description does not explain how the agent is performing.
Inadequate Attempt	7.5 pts	Submission does not meet graduate-level standards.
Non-Performance	0 pts	Non-performance.
Video Presentation, No AI Usage

Weight: 50%
Maximum Points: 105 pts

Rating	Points	Requirements
Meets or Exceeds Expectations	105 pts	No AI usage. All team members participate. The technical solution overview includes relevant details and covers evaluation. The business value is articulated, and there is a recommendation on deployment. The opinionated commentary is thoughtful.
Approaches Expectations	94.5 pts	No AI usage. Not all team members participate, the technical solution overview does not include relevant details, evaluation is not covered, the business value is not articulated, there is no deployment recommendation, or the opinionated commentary is minimal.
Below Expectations	86.1 pts	No AI usage. One of the following is extremely substandard: the technical solution, business value and deployment recommendations, or opinionated commentary.
Inadequate Attempt	73.5 pts	The deliverable does not meet graduate-level standards, possibly because the deliverable was generated using AI.
Non-Performance	0 pts	Non-performance.

Full-Credit Checklist
Data Pipeline Code, 21 pts

[ ] Data pipeline notebook executes successfully.

[ ] Pipeline extracts the data needed for the selected use case.

Agent Code, 52.5 pts

[ ] Agent includes an LLM.

[ ] Agent includes at least two relevant tools.

[ ] Agent includes all obvious tools needed for the use case.

[ ] Agent handles errors gracefully.

[ ] Agent handles out-of-scope user queries gracefully.

Evaluation Examples, 31.5 pts

[ ] Five evaluated traces are provided.

[ ] At least one trace compares different LLMs.

[ ] Written commentary clearly explains agent performance.

Video Presentation, 105 pts

[ ] Follow the course rule stated in the rubric regarding no AI usage for the video presentation.

[ ] Every team member participates.

[ ] Technical solution overview includes relevant details.

[ ] Evaluation process and results are covered.

[ ] Business value is explained.

[ ] Deployment recommendation is provided.

[ ] Opinionated commentary about agent quality is thoughtful.