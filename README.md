# EduPro Instructor Performance & Course Quality Analytics

A data-driven evaluation of instructor effectiveness and course quality on the EduPro online learning platform, built for Unified Mentor.

## 📋 Project Overview

This project analyzes 60 instructors, 60 courses, and 10,000 enrollment transactions to answer:
- Do instructors with more experience receive higher ratings?
- Is there a relationship between instructor rating and course rating?
- Which expertise areas consistently deliver high-quality courses?
- Are highly rated instructors associated with higher enrollments?

## 🔑 Key Findings

- **Experience predicts instructor quality**: Years of experience correlates strongly with teacher rating (Spearman ρ ≈ 0.67).
- **Instructor rating ≠ course quality**: Teacher rating shows almost no relationship with course rating (r ≈ 0.0005) — a well-liked instructor doesn't guarantee a well-liked course.
- **Enrollment is outlier-driven**: A handful of highly popular instructors skew enrollment numbers; rating alone doesn't reliably predict demand.
- **Advanced-level courses underperform** consistently across every category.
- **Marketing/Digital Marketing** lead in course ratings; **Machine Learning and Business** trail.

## 📁 Repository Contents

| File | Description |
|---|---|
| `app.py` | Interactive Streamlit dashboard — instructor leaderboard, experience vs. rating scatter plots, course quality heatmap, expertise comparisons |
| `teachers.csv` | Instructor data (ID, name, age, gender, expertise, experience, rating) |
| `courses.csv` | Course catalog (ID, name, category, level, price, duration, rating) |
| `transactions.csv` | Enrollment transaction records linking learners, courses, and instructors |
| `EduPro_Instructor_Course_Quality_Report.docx` | Full research paper: methodology, findings, KPIs, and recommendations |

## 🚀 Running the Dashboard

```bash
pip install streamlit pandas plotly
streamlit run app.py
```

The app expects `teachers.csv`, `courses.csv`, and `transactions.csv` in the same directory.

## 🛠️ Tools Used

- **Python** (pandas, plotly) for data processing and visualization
- **Streamlit** for the interactive dashboard
- **Word/docx** for the formal research report

## 📊 Recommended KPIs

- Average Teacher Rating
- Average Course Rating
- Rating Consistency Index
- Experience Impact Score
- Enrollment Influence Ratio

---
*Built as part of an instructor performance and course quality evaluation initiative for EduPro.*
