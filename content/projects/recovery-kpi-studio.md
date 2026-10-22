---
title: Recovery KPI Studio
category: Research Software
summary: An interactive website for exploring longitudinal recovery data through transparent indicators, interactive charts, and documented analysis workflows.
status: Local prototype · Version 1
order: 0
featured: yes
tools: Python, Streamlit, pandas, Plotly, openpyxl, pytest
---
## Recovery KPI Studio

I developed Recovery KPI Studio as an interactive website to help researchers explore disaster recovery data while keeping the meaning of each variable, calculation, and comparison clear. The project grew from my work with longitudinal housing recovery records, where examining change over time requires attention to data quality, indicator definitions, and the observations included in each analysis. It brings these needs together in a workspace that connects data engineering, analytics, and visualization.

Researchers can upload CSV or Excel files, select worksheets, and inspect missing values, duplicate records, and column types before combining data across sources. Records can be joined using a shared key or stacked into one dataset, with source labels retained to support later comparisons. Users then identify household IDs, survey waves, events, weights, and recovery measures, documenting how their selected variables should be interpreted.

Building on that foundation, the website supports the definition and exploration of key performance indicators. Formula previews make calculations visible, while weighted and unweighted summaries allow researchers to examine their data from different perspectives. Interactive charts and filters help users follow recovery trajectories across survey waves and compare groups. An equation builder also allows users to select variables and multipliers, construct averages or weighted combinations, and compare the resulting estimates with an observed outcome.

My contribution includes shaping this analytical workflow and developing the interface, data inspection tools, filters, visualizations, and equation builder. Throughout the design, I focused on making analytical choices easy to review: which records enter a comparison, how an indicator is defined, and what a calculation represents. Users can export results together with indicator definitions, data-quality reports, and methodology documentation so that the analysis remains understandable beyond the website.

The website uses Streamlit for its interface, pandas for data manipulation, openpyxl for Excel support, and Plotly for interactive charts. Separate Python modules handle data loading, validation, indicator calculations, longitudinal analysis, and exports, with tests covering calculation and validation behavior. Version 1 currently runs locally and includes a synthetic practice dataset. It is not publicly hosted yet, and this case study does not display confidential household records or unpublished research findings.

[Discuss the project →](contact.html)
