# jps-release-audit-utils

![Build](https://github.com/jai-python3/jps-release-audit-utils/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/jai-python3/jps-release-audit-utils/actions/workflows/publish-to-pypi.yml/badge.svg)
[![codecov](https://codecov.io/gh/jai-python3/jps-release-audit-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/jai-python3/jps-release-audit-utils)

A comprehensive Python toolkit for **auditing software releases**, **comparing multiple Git branches**, and producing **Excel-based release intelligence reports**.  
Designed to help engineering, QA, release management, and DevOps teams understand **what code is in a release**, **what is missing**, and **how commit history evolved**.

---

## 🚀 Overview

`jps-release-audit-utils` analyzes commit histories across multiple Git branches and generates a multi-worksheet Excel report with rich metadata, topology-aware commit ordering, branch coverage analysis, and color-coded indicators.

It is useful for:

- Preparing release candidates  
- Verifying required commits are present  
- Identifying missing or cherry-pick commits  
- Understanding merge timing vs. authored commit dates  
- Explaining branching and merging behavior to auditors or QA  
- Producing reproducible release audit artifacts  

---

## 🔍 Key Features

### **✔ Multi-branch commit analysis**
- Accepts branches via `--branches` or `--branches-file`
- Compares branch membership for every commit
- Identifies missing, unique, and shared commits

### **✔ Four Excel worksheets (configurable names)**
1. **timeline_by_date**  
   Chronological commit history sorted by authored date.

2. **timeline_by_topology**  
   Git DAG (ancestry) order using `git rev-list --topo-order`.

3. **timeline_hybrid**  
   Combines date and topology order; highlights out-of-order commits.

4. **analytics_summary**  
   High-level metrics across branches: unique commits, missing commits, out-of-order count, etc.

### **✔ Rich metadata extraction**
- Commit hash  
- Commit message  
- Author  
- PR number (when present)  
- Authored date + datetime  
- Presence per branch

### **✔ Color-coded Excel output**
- **Red** for commits missing from a branch  
- **Green** for commits present in *all* branches  
- **Yellow** for commits whose dates contradict topology order  
- Colors configurable via YAML

### **✔ YAML-based configuration**
Located at:  
`src/jps_release_audit_utils/conf/config.yaml`

Configurable items include:

```yaml
sheets:
  timeline_by_date: "Timeline (By Date)"
  timeline_by_topology: "Timeline (By Topology)"
  timeline_hybrid: "Hybrid Timeline"
  analytics_summary: "Analytics Summary"

colors:
  missing: "FFC7CE"
  all_present: "C6EFCE"
  out_of_order: "FFEB9C"
```

### ✔ Enhanced Excel formatting
Frozen header rows

Auto-filter enabled

Auto-adjusted column widths

## 📊 Worksheet Overview
Each worksheet provides a different perspective on commit history:

|Worksheet|	Purpose|
|----------|---------|
|timeline_by_date |	Understand when commits were authored.|
|timeline_by_topology |	Understand how Git applied commits (true ancestry).|
|timeline_hybrid |	Detect rebases/cherry-picks via date vs. topology mismatch.|
|analytics_summary |	Quickly assess branch readiness and commit coverage.|

For detailed explanations, see:
➡️ docs/worksheet_explanations.md (recommended to create as part of project)

## 🧪 Example Usage
Compare 3 branches and output Excel report
```bash
python -m jps_release_audit_utils.commit_report \
    --repo-path /path/to/repo \
    --branches develop,main,release/v5.8.0-rc \
    --output release_audit.xlsx
``

Using a branches file
```bash
python -m jps_release_audit_utils.commit_report \
    --branches-file branches.txt \
    --output audit.xlsx
```

Using a custom YAML configuration
```bash
python -m jps_release_audit_utils.commit_report \
    --branches-file branches.txt \
    --config src/jps_release_audit_utils/conf/config.yaml
```

## 📦 Installation
```bash
make install
```

or:

```bash
pip install jps-release-audit-utils
```

## 🧪 Development
```bash
make fix && make format && make lint
make test
```

## 📝 Roadmap (Optional Suggestions)
Optional PR-scraping via GitHub API

Release note generation

Branch divergence visualization

GitHub Actions plugin integration

HTML dashboards

## 📜 License
MIT License © Jaideep Sundaram