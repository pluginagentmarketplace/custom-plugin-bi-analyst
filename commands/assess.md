---
name: assess
description: Assess Your BI Skills
allowed-tools: Read
---

# /assess - Assess Your BI Skills

Evaluate your current Business Intelligence skills, identify gaps, and get personalized recommendations for improvement.

## Assessment Types

### 1. Quick Assessment (10 minutes)
- 20 questions across core BI skills
- Instant proficiency overview
- Identifies strongest and weakest areas
- Quick recommendations

### 2. Comprehensive Assessment (30 minutes)
- 50+ questions covering all BI domains
- Detailed skill breakdown
- Personalized learning path
- Role readiness evaluation

### 3. Tool-Specific Assessment (15 minutes)
- Deep dive into specific tool (Power BI, Tableau, SQL)
- Skill level certification
- Advanced topic identification
- Resource recommendations

### 4. Role Readiness Assessment (20 minutes)
- Evaluate readiness for target role
- Gap analysis vs. requirements
- Timeline to readiness
- Priority learning areas

## Skill Categories Assessed

### SQL & Data Querying
**Topics Covered:**
- Basic SELECT statements
- JOINs and subqueries
- Aggregations and GROUP BY
- Window functions
- CTEs and recursive queries
- Performance optimization

**Sample Question:**
```sql
-- What does this query return?
SELECT department,
       employee_name,
       salary,
       AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees
WHERE hire_date > '2023-01-01'
```

### Data Visualization
**Topics Covered:**
- Chart type selection
- Color theory and accessibility
- Dashboard layout principles
- Interactivity design
- Storytelling with data
- Mobile optimization

**Sample Question:**
```
Which chart type is most appropriate for showing:
"Sales performance of 5 products over 12 months"

A) Pie chart
B) Line chart
C) Scatter plot
D) Treemap

Answer: B) Line chart - best for trends over time
```

### Power BI
**Topics Covered:**
- Data modeling
- DAX formulas
- Power Query transformations
- Report design
- Service administration
- Security implementation

**Sample Question:**
```dax
// What does this DAX measure calculate?
Total Sales LY =
CALCULATE(
    SUM(Sales[Amount]),
    SAMEPERIODLASTYEAR(Calendar[Date])
)
```

### Tableau
**Topics Covered:**
- Calculated fields
- LOD expressions
- Dashboard actions
- Parameters
- Server publishing
- Performance optimization

**Sample Question:**
```
// What does this LOD expression compute?
{ FIXED [Customer ID] : MIN([Order Date]) }

A) First order date for each customer
B) Minimum order date overall
C) Customer with earliest order
D) Number of orders per customer

Answer: A) First order date for each customer
```

### Data Modeling
**Topics Covered:**
- Dimensional modeling
- Star schema design
- Fact and dimension tables
- Slowly changing dimensions
- Data normalization
- Relationship types

**Sample Question:**
```
In a star schema, which is TRUE about fact tables?

A) They contain descriptive attributes
B) They store measurements and metrics
C) They should be denormalized
D) They have few rows

Answer: B) They store measurements and metrics
```

### Business Acumen
**Topics Covered:**
- KPI definition and measurement
- Business metrics understanding
- Stakeholder communication
- Requirements gathering
- ROI analysis
- Industry knowledge

**Sample Question:**
```
A stakeholder requests "a report showing how we're doing"
What is your FIRST response?

A) Build a general dashboard immediately
B) Ask clarifying questions about specific metrics
C) Show them existing reports
D) Suggest standard KPIs

Answer: B) Ask clarifying questions about specific metrics
```

## Proficiency Levels

### Level 1: Beginner
- Basic understanding of concepts
- Can complete simple tasks with guidance
- Learning fundamentals
- 0-1 years experience

### Level 2: Intermediate
- Solid grasp of core concepts
- Works independently on standard tasks
- Some advanced knowledge
- 1-3 years experience

### Level 3: Advanced
- Deep expertise in multiple areas
- Handles complex scenarios
- Mentors others
- 3-6 years experience

### Level 4: Expert
- Mastery across domains
- Sets standards and best practices
- Strategic thinking
- 6+ years experience

## Assessment Results Example

```
BI Skills Assessment Results
════════════════════════════════════════

Overall Score: 72/100 (Advanced)

Skill Breakdown:
┌─────────────────────┬───────┬─────────────┐
│ Skill Area          │ Score │ Level       │
├─────────────────────┼───────┼─────────────┤
│ SQL & Data Querying │ 85%   │ Expert      │
│ Data Visualization  │ 78%   │ Advanced    │
│ Power BI            │ 70%   │ Advanced    │
│ Tableau             │ 55%   │ Intermediate│
│ Data Modeling       │ 75%   │ Advanced    │
│ Business Acumen     │ 68%   │ Advanced    │
└─────────────────────┴───────┴─────────────┘

Strengths:
✓ Strong SQL query writing skills
✓ Good understanding of visualization principles
✓ Solid data modeling foundation

Areas for Improvement:
! Tableau LOD expressions need work
! Business requirement gathering skills
! Advanced DAX calculations

Recommended Learning Path:
1. Tableau Advanced (4 weeks)
2. DAX Patterns (3 weeks)
3. Stakeholder Management (2 weeks)

Role Readiness:
├── BI Analyst: Ready ✓
├── Senior BI Analyst: 85% ready
├── Analytics Engineer: 70% ready
└── BI Manager: 60% ready
```

## Personalized Recommendations

Based on your assessment, you receive:

### Immediate Actions (This Week)
- Specific skills to practice
- Quick wins to address gaps
- Resources to review

### Short-term Plan (1-3 Months)
- Structured learning path
- Project suggestions
- Certification recommendations

### Long-term Goals (3-12 Months)
- Career target alignment
- Advanced skill development
- Leadership preparation

## Progress Tracking

### Retake Assessment
- Recommended every 4-6 weeks
- Track improvement over time
- Adjust learning plan based on progress

### Skill Growth Chart
```
Your SQL Progress:
Jan: ████████░░░░░░░░ 50%
Feb: ██████████░░░░░░ 65%
Mar: ████████████░░░░ 78%
Apr: ██████████████░░ 85%
```

## Assessment Tips

1. **Be Honest** - Choose what you actually know, not what you hope to know
2. **Take Your Time** - Don't rush through questions
3. **Skip Unknown Topics** - It's okay to not know everything
4. **Review Results Carefully** - Understand why answers are correct
5. **Act on Feedback** - Use recommendations immediately
6. **Retake Regularly** - Track your progress over time

## Using Results with Agents

After assessment, leverage specialized agents:

- **Low SQL Score?** → Use SQL Analytics Agent
- **Visualization Gaps?** → Use Data Visualization Agent
- **Power BI Needs Work?** → Use Excel & Power BI Agent
- **Tableau Improvement?** → Use Tableau Agent

## Related Commands

- `/learn` - Start learning based on assessment gaps
- `/roadmap` - See where your skills fit in career paths
- `/role` - Understand role requirements vs. your skills

---

**Ready to assess? Type `/assess` and evaluate your BI skills!**
