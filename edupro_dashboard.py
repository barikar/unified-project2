"""
EduPro — Instructor Performance & Course Quality Dashboard
Run with:  streamlit run edupro_dashboard.py

Expects three CSVs in the same folder as this script:
  teachers.csv      (TeacherID, TeacherName, Age, Gender, Expertise, YearsOfExperience, TeacherRating)
  courses.csv       (CourseID, CourseName, CourseCategory, CourseType, CourseLevel, CoursePrice, CourseDuration, CourseRating)
  transactions.csv  (TransactionID, UserID, CourseID, TransactionDate, Amount, PaymentMethod, TeacherID)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="EduPro | Instructor & Course Quality", layout="wide")

DATA_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    teachers = pd.read_csv(DATA_DIR / "teachers.csv")
    courses = pd.read_csv(DATA_DIR / "courses.csv")
    transactions = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["TransactionDate"])

    merged = (
        transactions.merge(teachers, on="TeacherID", how="left")
        .merge(courses, on="CourseID", how="left")
    )

    enroll_per_teacher = merged.groupby("TeacherID").size().rename("Enrollments")
    avg_course_rating_taught = merged.groupby("TeacherID")["CourseRating"].mean().rename("AvgCourseRatingTaught")
    n_unique_courses = merged.groupby("TeacherID")["CourseID"].nunique().rename("UniqueCoursesTaught")
    course_rating_std = merged.groupby("TeacherID")["CourseRating"].std().rename("CourseRatingConsistency")

    teachers_full = (
        teachers.set_index("TeacherID")
        .join([enroll_per_teacher, avg_course_rating_taught, n_unique_courses, course_rating_std])
        .reset_index()
    )
    teachers_full["Enrollments"] = teachers_full["Enrollments"].fillna(0)
    teachers_full["RatingTier"] = pd.cut(
        teachers_full["TeacherRating"], bins=[0, 2.5, 3.75, 5], labels=["Low", "Mid", "High"]
    )

    return teachers, courses, transactions, merged, teachers_full


teachers, courses, transactions, merged, teachers_full = load_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")

expertise_options = sorted(teachers["Expertise"].dropna().unique())
selected_expertise = st.sidebar.multiselect("Instructor Expertise", expertise_options, default=expertise_options)

category_options = sorted(courses["CourseCategory"].dropna().unique())
selected_categories = st.sidebar.multiselect("Course Category", category_options, default=category_options)

level_options = sorted(courses["CourseLevel"].dropna().unique())
selected_levels = st.sidebar.multiselect("Course Level", level_options, default=level_options)

rating_range = st.sidebar.slider(
    "Teacher Rating Range", min_value=1.0, max_value=5.0, value=(1.0, 5.0), step=0.05
)

exp_range = st.sidebar.slider(
    "Years of Experience",
    min_value=int(teachers["YearsOfExperience"].min()),
    max_value=int(teachers["YearsOfExperience"].max()),
    value=(int(teachers["YearsOfExperience"].min()), int(teachers["YearsOfExperience"].max())),
)

# Apply filters
f_teachers = teachers_full[
    teachers_full["Expertise"].isin(selected_expertise)
    & teachers_full["TeacherRating"].between(*rating_range)
    & teachers_full["YearsOfExperience"].between(*exp_range)
]
f_courses = courses[
    courses["CourseCategory"].isin(selected_categories) & courses["CourseLevel"].isin(selected_levels)
]
f_merged = merged[
    merged["Expertise"].isin(selected_expertise)
    & merged["CourseCategory"].isin(selected_categories)
    & merged["CourseLevel"].isin(selected_levels)
    & merged["TeacherRating"].between(*rating_range)
    & merged["YearsOfExperience"].between(*exp_range)
]

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------
st.title("📊 EduPro — Instructor Performance & Course Quality")
st.caption("Data-driven evaluation of instructor effectiveness and course quality consistency")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Avg Teacher Rating", f"{f_teachers['TeacherRating'].mean():.2f}" if len(f_teachers) else "—")
k2.metric("Avg Course Rating", f"{f_courses['CourseRating'].mean():.2f}" if len(f_courses) else "—")
k3.metric(
    "Rating Consistency Index",
    f"{f_teachers['CourseRatingConsistency'].mean():.2f}" if len(f_teachers) else "—",
    help="Avg std-dev of course ratings across each instructor's courses. Lower = more consistent quality.",
)
exp_corr = f_teachers[["YearsOfExperience", "TeacherRating"]].corr().iloc[0, 1] if len(f_teachers) > 2 else np.nan
k4.metric("Experience Impact Score", f"{exp_corr:.2f}" if pd.notna(exp_corr) else "—",
          help="Correlation between years of experience and teacher rating.")
k5.metric("Total Enrollments (filtered)", f"{len(f_merged):,}")

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🏆 Instructor Leaderboard", "📈 Experience vs Rating", "🔥 Course Quality Heatmap", "🎯 Expertise Comparison"]
)

with tab1:
    st.subheader("Instructor Leaderboard")
    sort_by = st.selectbox("Sort by", ["TeacherRating", "Enrollments", "YearsOfExperience", "UniqueCoursesTaught"])
    lb = f_teachers.sort_values(sort_by, ascending=False)[
        ["TeacherName", "Expertise", "YearsOfExperience", "TeacherRating",
         "Enrollments", "UniqueCoursesTaught", "AvgCourseRatingTaught", "RatingTier"]
    ].reset_index(drop=True)
    lb.index += 1
    st.dataframe(lb, use_container_width=True, height=450)

    col_a, col_b = st.columns(2)
    with col_a:
        top10 = f_teachers.sort_values("TeacherRating", ascending=False).head(10)
        fig = px.bar(top10, x="TeacherRating", y="TeacherName", orientation="h",
                     title="Top 10 Instructors by Rating", color="TeacherRating",
                     color_continuous_scale="Blues")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        tier_enroll = f_teachers.groupby("RatingTier", observed=True)["Enrollments"].mean().reset_index()
        fig2 = px.bar(tier_enroll, x="RatingTier", y="Enrollments",
                      title="Avg Enrollments by Rating Tier (watch for outlier skew)")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("⚠️ This platform's data shows this metric is heavily skewed by 1-2 "
                   "highly popular instructors — check the raw scatter before concluding rating drives demand.")

with tab2:
    st.subheader("Experience vs Rating")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(f_teachers, x="YearsOfExperience", y="TeacherRating",
                          hover_data=["TeacherName", "Expertise"],
                          title="Years of Experience vs Teacher Rating")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.scatter(f_teachers, x="YearsOfExperience", y="AvgCourseRatingTaught",
                           hover_data=["TeacherName", "Expertise"],
                           title="Years of Experience vs Avg Course Rating Taught")
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(f_teachers, x="TeacherRating", y="AvgCourseRatingTaught",
                       hover_data=["TeacherName"],
                       title="Teacher Rating vs Course Rating (does a liked teacher mean a liked course?)")
    st.plotly_chart(fig3, use_container_width=True)

    bins = [0, 3, 6, 10, 15, 25]
    labels = ["1-3", "4-6", "7-10", "11-15", "16-24"]
    f_teachers_binned = f_teachers.copy()
    f_teachers_binned["ExpBucket"] = pd.cut(f_teachers_binned["YearsOfExperience"], bins=bins, labels=labels)
    bucket_avg = f_teachers_binned.groupby("ExpBucket", observed=True)["TeacherRating"].mean().reset_index()
    fig4 = px.line(bucket_avg, x="ExpBucket", y="TeacherRating", markers=True,
                    title="Avg Teacher Rating by Experience Bracket (diminishing returns check)")
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Course Quality Heatmap")
    if len(f_courses):
        pivot = f_courses.pivot_table(index="CourseCategory", columns="CourseLevel",
                                       values="CourseRating", aggfunc="mean")
        fig = px.imshow(pivot, text_auto=".2f", aspect="auto", color_continuous_scale="RdYlGn",
                         title="Avg Course Rating: Category × Level")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No courses match the current filters.")

    col_a, col_b = st.columns(2)
    with col_a:
        cat_avg = f_courses.groupby("CourseCategory")["CourseRating"].mean().sort_values(ascending=False).reset_index()
        fig2 = px.bar(cat_avg, x="CourseRating", y="CourseCategory", orientation="h",
                      title="Avg Course Rating by Category")
        st.plotly_chart(fig2, use_container_width=True)
    with col_b:
        lvl_avg = f_courses.groupby("CourseLevel")["CourseRating"].mean().reset_index()
        fig3 = px.bar(lvl_avg, x="CourseLevel", y="CourseRating", title="Avg Course Rating by Level")
        st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Expertise-Based Performance")
    expertise_stats = f_teachers.groupby("Expertise").agg(
        NumTeachers=("TeacherID", "count"),
        AvgTeacherRating=("TeacherRating", "mean"),
        AvgCourseRatingTaught=("AvgCourseRatingTaught", "mean"),
        TotalEnrollments=("Enrollments", "sum"),
    ).sort_values("AvgTeacherRating", ascending=False).reset_index()

    fig = px.bar(expertise_stats, x="Expertise", y=["AvgTeacherRating", "AvgCourseRatingTaught"],
                 barmode="group", title="Teacher Rating vs Course Rating by Expertise")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(expertise_stats, use_container_width=True)

    fig2 = px.scatter(expertise_stats, x="AvgTeacherRating", y="AvgCourseRatingTaught",
                       size="TotalEnrollments", text="Expertise",
                       title="Expertise Areas: Teacher Quality vs Course Quality vs Demand (bubble size)")
    fig2.update_traces(textposition="top center")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.caption("EduPro Instructor Performance & Course Quality Evaluation • Built for internal analytics use")
