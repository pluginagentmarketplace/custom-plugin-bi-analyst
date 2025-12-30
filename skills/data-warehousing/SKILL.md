---
name: data-warehousing
description: Master dimensional data modeling including star schema design, slowly changing dimensions, fact tables, and data warehouse architecture
sasmp_version: "1.3.0"
bonded_agent: 06-data-modeling
bond_type: PRIMARY_BOND
parameters:
  task:
    type: string
    required: true
    enum: [star_schema, dimension, fact_table, scd, grain_definition]
  platform:
    type: string
    enum: [snowflake, bigquery, redshift, synapse, databricks]
    default: snowflake
  methodology:
    type: string
    enum: [kimball, inmon, data_vault]
    default: kimball
retry_config:
  max_retries: 3
  backoff_ms: [1000, 2000, 4000]
---

# Data Warehousing Skill

Master dimensional data modeling for business intelligence, including star schema design, slowly changing dimensions, and modern data warehouse patterns.

## Quick Start (5 minutes)

```
DIMENSIONAL MODELING BASICS

1. Identify the business process (e.g., Sales)
2. Declare the grain (one row = one order line)
3. Choose dimensions (Who, What, When, Where)
4. Identify facts (measures: quantity, amount, cost)
```

## Core Concepts

### Star Schema Structure

```
                    ┌─────────────┐
                    │  Dim_Date   │
                    └──────┬──────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────┴──────┐     ┌──────┴──────┐     ┌──────┴──────┐
│Dim_Customer │     │ Fact_Sales  │     │ Dim_Product │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  Dim_Store  │
                    └─────────────┘

STAR = One fact table surrounded by dimensions
       Dimensions join directly to fact (no chains)
```

### Fact Table Types

```
┌──────────────────────────────────────────────────────────┐
│                   FACT TABLE TYPES                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  TRANSACTION FACT                                        │
│  • One row per event/transaction                         │
│  • Most common type                                      │
│  • Example: Order line, click, payment                   │
│  • Measures: Quantity, Amount, Count                     │
│                                                          │
│  PERIODIC SNAPSHOT                                       │
│  • One row per time period per entity                    │
│  • Point-in-time state                                   │
│  • Example: Daily account balance, Monthly inventory     │
│  • Measures: Balance, Quantity on Hand                   │
│                                                          │
│  ACCUMULATING SNAPSHOT                                   │
│  • One row per entity lifecycle                          │
│  • Multiple date columns (milestones)                    │
│  • Example: Order fulfillment, Loan processing           │
│  • Measures: Days in stage, Count                        │
│                                                          │
│  FACTLESS FACT                                           │
│  • Records events without measures                       │
│  • Just dimension keys                                   │
│  • Example: Student attendance, Product promotions       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Slowly Changing Dimension Types

```
SCD TYPE 0: Retain Original
┌────────────────────────────────────────────────────┐
│ Never update. Keep original value forever.         │
│ Use for: Birth date, Original signup source       │
└────────────────────────────────────────────────────┘

SCD TYPE 1: Overwrite
┌────────────────────────────────────────────────────┐
│ Update in place. No history preserved.            │
│ Use for: Error corrections, Non-critical data     │
│                                                    │
│ Before: | ID | Name    | Address     |            │
│         | 1  | John    | 123 Main St |            │
│                                                    │
│ After:  | ID | Name    | Address     |            │
│         | 1  | John    | 456 Oak Ave |            │
└────────────────────────────────────────────────────┘

SCD TYPE 2: Add New Row
┌────────────────────────────────────────────────────┐
│ Insert new row. Expire old row. Full history.     │
│ Use for: Critical tracking (address, segment)     │
│                                                    │
│ | Key | ID | Address    | Start   | End     |Curr │
│ | 1   | A  | 123 Main   | 2020-01 | 2024-06 | N   │
│ | 2   | A  | 456 Oak    | 2024-06 | 9999-12 | Y   │
└────────────────────────────────────────────────────┘

SCD TYPE 3: Add Column
┌────────────────────────────────────────────────────┐
│ Keep current and previous value in columns.       │
│ Use for: When only one prior value needed         │
│                                                    │
│ | ID | Current_Address | Previous_Address |       │
│ | 1  | 456 Oak Ave     | 123 Main St      |       │
└────────────────────────────────────────────────────┘

SCD TYPE 6: Hybrid (1+2+3)
┌────────────────────────────────────────────────────┐
│ Combination: History + current column             │
│ Use for: Maximum query flexibility                │
│                                                    │
│ | Key | ID | Addr    | Curr_Addr | Start | End  | │
│ | 1   | A  | 123 Main| 456 Oak   | 2020  | 2024 | │
│ | 2   | A  | 456 Oak | 456 Oak   | 2024  | 9999 | │
└────────────────────────────────────────────────────┘
```

## Code Examples

### Dimension Table Template
```sql
CREATE TABLE dim_customer (
    -- Surrogate Key (Primary Key)
    customer_key        INT IDENTITY(1,1) PRIMARY KEY,

    -- Natural Key (Business Key)
    customer_id         VARCHAR(50) NOT NULL,

    -- Descriptive Attributes
    customer_name       VARCHAR(200) NOT NULL,
    email               VARCHAR(200),
    phone               VARCHAR(50),

    -- Hierarchy Attributes
    segment             VARCHAR(50),
    tier                VARCHAR(20),

    -- Geographic Hierarchy
    address             VARCHAR(500),
    city                VARCHAR(100),
    state               VARCHAR(50),
    postal_code         VARCHAR(20),
    country             VARCHAR(100),
    region              VARCHAR(50),

    -- SCD Type 2 Tracking
    effective_start_date    DATE NOT NULL,
    effective_end_date      DATE DEFAULT '9999-12-31',
    is_current              BIT DEFAULT 1,
    version_number          INT DEFAULT 1,

    -- Audit Columns
    created_at          DATETIME DEFAULT GETDATE(),
    updated_at          DATETIME,
    source_system       VARCHAR(50),
    etl_batch_id        BIGINT
);

-- Indexes
CREATE UNIQUE INDEX idx_customer_natural ON dim_customer(customer_id, effective_end_date);
CREATE INDEX idx_customer_current ON dim_customer(customer_id) WHERE is_current = 1;
CREATE INDEX idx_customer_segment ON dim_customer(segment);
```

### Fact Table Template
```sql
CREATE TABLE fact_sales (
    -- Surrogate Key
    sales_key           BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Dimension Foreign Keys
    date_key            INT NOT NULL,
    customer_key        INT NOT NULL,
    product_key         INT NOT NULL,
    store_key           INT NOT NULL,
    promotion_key       INT,

    -- Degenerate Dimensions (no separate table needed)
    order_number        VARCHAR(50) NOT NULL,
    order_line_number   INT NOT NULL,

    -- Additive Measures (can SUM across all dimensions)
    quantity            INT NOT NULL,
    unit_price          DECIMAL(10,2) NOT NULL,
    discount_amount     DECIMAL(10,2) DEFAULT 0,
    sales_amount        DECIMAL(12,2) NOT NULL,
    cost_amount         DECIMAL(12,2),
    profit_amount       DECIMAL(12,2),
    tax_amount          DECIMAL(10,2),

    -- Non-Additive Measures (cannot SUM directly)
    unit_cost           DECIMAL(10,2),
    discount_percent    DECIMAL(5,2),
    margin_percent      DECIMAL(5,2),

    -- Audit Columns
    created_at          DATETIME DEFAULT GETDATE(),
    source_system       VARCHAR(50),
    etl_batch_id        BIGINT,

    -- Foreign Key Constraints
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
);

-- Indexes for common query patterns
CREATE INDEX idx_sales_date ON fact_sales(date_key);
CREATE INDEX idx_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_sales_product ON fact_sales(product_key);
CREATE INDEX idx_sales_composite ON fact_sales(date_key, product_key, customer_key);

-- Partitioning (for large tables)
-- CREATE TABLE fact_sales PARTITION BY RANGE (date_key);
```

### Date Dimension Generator
```sql
-- Generate comprehensive date dimension
WITH date_spine AS (
    SELECT
        DATEADD(DAY, n, '2020-01-01') AS date_value
    FROM (
        SELECT TOP 3650 ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS n
        FROM sys.objects a CROSS JOIN sys.objects b
    ) numbers
)
INSERT INTO dim_date (
    date_key,
    date_value,
    year,
    quarter,
    month,
    month_name,
    week,
    day_of_week,
    day_name,
    day_of_month,
    day_of_year,
    is_weekend,
    is_holiday,
    fiscal_year,
    fiscal_quarter
)
SELECT
    CONVERT(INT, FORMAT(date_value, 'yyyyMMdd')) AS date_key,
    date_value,
    YEAR(date_value) AS year,
    DATEPART(QUARTER, date_value) AS quarter,
    MONTH(date_value) AS month,
    DATENAME(MONTH, date_value) AS month_name,
    DATEPART(WEEK, date_value) AS week,
    DATEPART(WEEKDAY, date_value) AS day_of_week,
    DATENAME(WEEKDAY, date_value) AS day_name,
    DAY(date_value) AS day_of_month,
    DATEPART(DAYOFYEAR, date_value) AS day_of_year,
    CASE WHEN DATEPART(WEEKDAY, date_value) IN (1, 7) THEN 1 ELSE 0 END AS is_weekend,
    0 AS is_holiday,  -- Update with actual holidays
    CASE WHEN MONTH(date_value) >= 4 THEN YEAR(date_value) ELSE YEAR(date_value) - 1 END AS fiscal_year,
    CASE
        WHEN MONTH(date_value) IN (4,5,6) THEN 1
        WHEN MONTH(date_value) IN (7,8,9) THEN 2
        WHEN MONTH(date_value) IN (10,11,12) THEN 3
        ELSE 4
    END AS fiscal_quarter
FROM date_spine;
```

## Best Practices

### Naming Conventions
```yaml
tables:
  dimensions: dim_{entity}
  facts: fact_{business_process}
  bridges: bridge_{relationship}
  aggregates: agg_{fact}_{grain}

columns:
  surrogate_key: "{table}_key"
  natural_key: "{entity}_id"
  foreign_key: "{dimension}_key"
  measures: "{name}_amount", "{name}_count", "{name}_qty"
  dates: "{name}_date", "created_at", "updated_at"
  flags: "is_{condition}", "has_{feature}"

examples:
  - dim_customer.customer_key
  - dim_customer.customer_id
  - fact_sales.customer_key
  - fact_sales.sales_amount
  - dim_date.is_weekend
```

### Grain Definition Template
```markdown
## Fact Table: fact_order_line
### Grain Statement
One row represents one line item on one customer order.

### Grain Components
- One order line item
- On one order
- For one product
- Sold to one customer
- At one store location
- On one specific date

### Test Query
SELECT order_number, line_number, COUNT(*)
FROM fact_order_line
GROUP BY order_number, line_number
HAVING COUNT(*) > 1;
-- Should return 0 rows
```

### Conformed Dimensions
```
Conformed = Same dimension used across multiple facts

BENEFITS:
• Consistent reporting
• Drill-across queries
• Single version of truth

REQUIREMENTS:
• Same surrogate keys
• Same attributes
• Same hierarchies
• Same business rules

EXAMPLES:
• dim_date: Used by sales, inventory, finance
• dim_customer: Used by sales, support, marketing
• dim_product: Used by sales, inventory, returns
```

## Common Patterns

### Bridge Table for Many-to-Many
```sql
-- Customer can have multiple accounts
-- Account can have multiple customers

CREATE TABLE bridge_customer_account (
    bridge_key          INT IDENTITY PRIMARY KEY,
    customer_key        INT NOT NULL,
    account_key         INT NOT NULL,
    relationship_type   VARCHAR(50),  -- Primary, Secondary, Authorized
    weight_factor       DECIMAL(5,4), -- For allocation (sum to 1.0)
    effective_start     DATE,
    effective_end       DATE,

    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (account_key) REFERENCES dim_account(account_key)
);

-- Usage in query
SELECT
    c.customer_name,
    SUM(f.balance * b.weight_factor) AS allocated_balance
FROM fact_account f
JOIN bridge_customer_account b ON f.account_key = b.account_key
JOIN dim_customer c ON b.customer_key = c.customer_key
WHERE c.customer_id = 'CUST001'
GROUP BY c.customer_name;
```

### Aggregate Fact Table
```sql
-- Pre-aggregate for performance
CREATE TABLE agg_sales_monthly_product (
    date_key_month      INT NOT NULL,  -- Monthly grain
    product_key         INT NOT NULL,
    total_quantity      INT,
    total_sales_amount  DECIMAL(15,2),
    total_cost_amount   DECIMAL(15,2),
    order_count         INT,
    customer_count      INT,
    row_count           INT,  -- For drill-through verification

    PRIMARY KEY (date_key_month, product_key)
);

-- Refresh aggregate
INSERT INTO agg_sales_monthly_product
SELECT
    (YEAR(d.date_value) * 100 + MONTH(d.date_value)) AS date_key_month,
    f.product_key,
    SUM(f.quantity),
    SUM(f.sales_amount),
    SUM(f.cost_amount),
    COUNT(DISTINCT f.order_number),
    COUNT(DISTINCT f.customer_key),
    COUNT(*)
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY (YEAR(d.date_value) * 100 + MONTH(d.date_value)), f.product_key;
```

## Retry Logic

```typescript
const executeETL = async (job: ETLJob) => {
  const retryConfig = {
    maxRetries: 3,
    backoffMs: [60000, 180000, 300000]  // 1min, 3min, 5min
  };

  for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
    try {
      return await dataWarehouse.runJob(job);
    } catch (error) {
      if (attempt === retryConfig.maxRetries) throw error;
      if (error.code === 'DEADLOCK') {
        await sleep(retryConfig.backoffMs[attempt]);
        continue;
      }
      throw error;
    }
  }
};
```

## Logging Hooks

```typescript
const dwHooks = {
  onDimensionLoad: (dimName, rowCount, duration) => {
    console.log(`[DW] Loaded ${dimName}: ${rowCount} rows in ${duration}s`);
  },

  onFactLoad: (factName, rowCount, duration) => {
    console.log(`[DW] Loaded ${factName}: ${rowCount} rows in ${duration}s`);
  },

  onSCDProcess: (dimName, inserts, updates) => {
    console.log(`[DW] SCD on ${dimName}: ${inserts} inserts, ${updates} updates`);
  }
};
```

## Unit Test Template

```typescript
describe('Data Warehousing Skill', () => {
  describe('Grain Validation', () => {
    it('should have unique grain in fact table', async () => {
      const duplicates = await db.query(`
        SELECT order_number, line_number, COUNT(*)
        FROM fact_sales
        GROUP BY order_number, line_number
        HAVING COUNT(*) > 1
      `);
      expect(duplicates.rowCount).toBe(0);
    });
  });

  describe('Referential Integrity', () => {
    it('should have no orphan facts', async () => {
      const orphans = await db.query(`
        SELECT COUNT(*)
        FROM fact_sales f
        LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
        WHERE c.customer_key IS NULL
      `);
      expect(orphans.rows[0].count).toBe(0);
    });
  });

  describe('SCD Type 2', () => {
    it('should have only one current record per entity', async () => {
      const duplicateCurrent = await db.query(`
        SELECT customer_id, COUNT(*)
        FROM dim_customer
        WHERE is_current = 1
        GROUP BY customer_id
        HAVING COUNT(*) > 1
      `);
      expect(duplicateCurrent.rowCount).toBe(0);
    });
  });
});
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Duplicate facts | Grain violation | Review ETL, add unique constraint |
| Missing dimension rows | Late-arriving data | Add "Unknown" row, fix SCD logic |
| Slow queries | Missing indexes | Add indexes on FK and filter columns |
| Wrong totals | Measure additivity | Check semi/non-additive handling |
| History gaps | SCD implementation | Verify date continuity |

## Resources

- **Kimball Group**: The Data Warehouse Toolkit
- **Ralph Kimball**: Dimensional Modeling Manifesto
- **DAMA DMBOK**: Data Management Body of Knowledge
- **Snowflake/BigQuery/Databricks**: Platform documentation

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01 | Initial release |
| 2.0.0 | 2025-01 | Production-grade with SCD patterns |
