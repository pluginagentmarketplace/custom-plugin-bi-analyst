---
name: data-visualization
description: Master data visualization principles including chart selection, dashboard design, color theory, and data storytelling
sasmp_version: "1.3.0"
bonded_agent: 02-data-visualization
bond_type: PRIMARY_BOND
parameters:
  task:
    type: string
    required: true
    enum: [chart_selection, dashboard_design, color_palette, storytelling, accessibility]
  data_type:
    type: string
    enum: [time_series, categorical, geospatial, hierarchical, correlation]
  audience:
    type: string
    enum: [executive, analyst, operational]
    default: analyst
retry_config:
  max_retries: 3
  backoff_ms: [1000, 2000, 4000]
---

# Data Visualization Skill

Master the art and science of effective data visualization, from chart selection to dashboard design and data storytelling.

## Quick Start (5 minutes)

```
1. Match your data relationship to the right chart type
2. Apply the 5-second rule: key insight visible immediately
3. Use color purposefully (not decoratively)
4. Follow accessibility guidelines (WCAG 2.1)
```

## Core Concepts

### The Visual Hierarchy

```
WHAT IS MOST IMPORTANT?
         │
    ┌────┴────┐
    ▼         ▼
  SIZE      POSITION
    │         │
    └────┬────┘
         │
    ┌────┴────┐
    ▼         ▼
  COLOR     CONTRAST
    │         │
    └────┬────┘
         │
    DETAIL/ANNOTATION
```

### Chart Selection Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                    CHART SELECTION GUIDE                     │
├────────────────────┬────────────────────────────────────────┤
│ SHOWING            │ RECOMMENDED CHART                      │
├────────────────────┼────────────────────────────────────────┤
│ Change over time   │ Line (continuous), Bar (discrete)      │
│ Comparison         │ Bar (horizontal if many items)         │
│ Part-to-whole      │ Stacked Bar, Treemap (NOT pie >5 items)│
│ Distribution       │ Histogram, Box Plot, Violin            │
│ Correlation        │ Scatter, Bubble                        │
│ Geographic         │ Choropleth, Symbol Map                 │
│ Ranking            │ Horizontal Bar (sorted)                │
│ Flow/Process       │ Sankey, Funnel                         │
│ Hierarchy          │ Treemap, Sunburst                      │
└────────────────────┴────────────────────────────────────────┘
```

### The Data-Ink Ratio

```
Edward Tufte's Principle:

                    Data-Ink
Data-Ink Ratio = ─────────────
                  Total Ink

MAXIMIZE data-ink. MINIMIZE chart junk.

Chart Junk (avoid):          Data-Ink (maximize):
• 3D effects                 • Axes and labels
• Decorative images          • Data points/bars
• Gradient fills             • Trend lines
• Excessive gridlines        • Annotations
• Drop shadows               • Reference lines
```

## Code Examples

### Color Palette Definitions (CSS Variables)
```css
/* Sequential Palette (for ordered data) */
:root {
  --seq-1: #f7fbff;
  --seq-2: #c6dbef;
  --seq-3: #6baed6;
  --seq-4: #2171b5;
  --seq-5: #084594;
}

/* Diverging Palette (for data with midpoint) */
:root {
  --div-neg-2: #d73027;
  --div-neg-1: #fc8d59;
  --div-neutral: #ffffbf;
  --div-pos-1: #91cf60;
  --div-pos-2: #1a9850;
}

/* Categorical Palette (max 7 distinct) */
:root {
  --cat-1: #1f77b4;
  --cat-2: #ff7f0e;
  --cat-3: #2ca02c;
  --cat-4: #d62728;
  --cat-5: #9467bd;
  --cat-6: #8c564b;
  --cat-7: #e377c2;
}

/* Semantic Colors */
:root {
  --positive: #22c55e;
  --negative: #ef4444;
  --neutral: #6b7280;
  --warning: #f59e0b;
}
```

### Dashboard Layout (Grid System)
```css
/* 12-column responsive grid */
.dashboard {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-gap: 16px;
  padding: 24px;
}

/* KPI Cards - Top Row */
.kpi-card {
  grid-column: span 3;  /* 4 cards across */
}

/* Primary Chart - Full Width */
.primary-chart {
  grid-column: span 12;
}

/* Secondary Charts - Half Width */
.secondary-chart {
  grid-column: span 6;
}

/* Responsive Breakpoints */
@media (max-width: 1024px) {
  .kpi-card { grid-column: span 6; }
  .secondary-chart { grid-column: span 12; }
}

@media (max-width: 640px) {
  .kpi-card { grid-column: span 12; }
}
```

### Chart Configuration (JSON)
```json
{
  "chart": {
    "type": "line",
    "title": "Monthly Revenue Trend",
    "subtitle": "Last 12 months vs prior year"
  },
  "data": {
    "source": "revenue_monthly",
    "x": "month",
    "y": ["current_year", "prior_year"]
  },
  "axes": {
    "x": {
      "label": "Month",
      "format": "MMM YYYY"
    },
    "y": {
      "label": "Revenue ($)",
      "format": "$,.0f",
      "min": 0
    }
  },
  "colors": {
    "current_year": "#2563eb",
    "prior_year": "#9ca3af"
  },
  "annotations": [
    {
      "type": "line",
      "value": 1000000,
      "label": "Target",
      "style": "dashed"
    }
  ],
  "legend": {
    "position": "top",
    "alignment": "right"
  },
  "accessibility": {
    "alt_text": "Line chart showing monthly revenue for current and prior year",
    "keyboard_navigable": true
  }
}
```

## Best Practices

### Dashboard Design Patterns

#### F-Pattern (Executive Dashboards)
```
┌─────────────────────────────────────────┐
│  [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]    │  ← Eyes start here
├─────────────────────────────────────────┤
│  [Primary Chart - Revenue Trend]        │  ← Scan left to right
├────────────────────┬────────────────────┤
│  [Top Products]    │  [Top Regions]     │  ← Drop down
├────────────────────┴────────────────────┤
│  [Detail Table]                         │  ← Scan for details
└─────────────────────────────────────────┘
```

#### Z-Pattern (Narrative Dashboards)
```
1 ─────────────────────────────────> 2
                                     │
                                     ▼
3 <───────────────────────────────── 4
│
▼
5 ─────────────────────────────> [CTA]
```

### Color Usage Rules

```
✓ DO:
• Use color to encode data (meaningful)
• Limit palette to 7 colors maximum
• Ensure 4.5:1 contrast ratio (WCAG AA)
• Use colorblind-safe palettes
• Keep semantic consistency (red=bad, green=good)

✗ DON'T:
• Use color as decoration
• Use red-green as only differentiator
• Use rainbow gradients
• Use highly saturated colors for large areas
• Change color meanings mid-dashboard
```

### Accessibility Checklist
```
□ Alt text for all charts
□ Color contrast meets WCAG 2.1 AA (4.5:1)
□ Color is not the only visual encoding
□ Keyboard navigation works
□ Screen reader compatibility
□ Font size minimum 12px
□ Pattern/texture for colorblind users
□ Captions for interactive elements
```

## Common Patterns

### KPI Card Design
```
┌─────────────────────────────┐
│  Revenue                    │  ← Label
│  $1.2M                      │  ← Value (large)
│  ▲ 12.5% vs LY             │  ← Comparison
│  ▔▔▔▔▔▔▁▁▁▂▃▅█            │  ← Sparkline
└─────────────────────────────┘

Components:
• Metric name (clear, concise)
• Current value (prominent)
• Comparison (vs target, prior period)
• Trend indicator (arrow + %)
• Sparkline (optional context)
```

### Data Storytelling Structure
```
1. HOOK: Lead with the insight
   "Revenue dropped 15% in Q3"

2. CONTEXT: Establish baseline
   "We typically grow 5% per quarter"

3. TENSION: Show the problem
   "Top 3 products all underperformed"

4. RESOLUTION: Present the insight
   "Supply chain issues caused stockouts"

5. CALL TO ACTION: Drive decision
   "Approve 2nd supplier contract"
```

### Annotation Types
```typescript
const annotationTypes = {
  reference_line: {
    use_case: "Target, benchmark, threshold",
    example: "Target: $1M"
  },
  trend_line: {
    use_case: "Show direction/pattern",
    example: "Linear regression"
  },
  callout: {
    use_case: "Highlight specific point",
    example: "Peak: Dec 2024"
  },
  range_band: {
    use_case: "Show acceptable range",
    example: "Budget ± 10%"
  },
  event_marker: {
    use_case: "Mark significant event",
    example: "Product launch: Mar 1"
  }
};
```

## Retry Logic

```typescript
const renderChart = async (config: ChartConfig) => {
  const retryConfig = {
    maxRetries: 3,
    backoffMs: [1000, 2000, 4000]
  };

  for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
    try {
      return await chartLibrary.render(config);
    } catch (error) {
      if (attempt === retryConfig.maxRetries) throw error;
      console.warn(`Render attempt ${attempt + 1} failed, retrying...`);
      await sleep(retryConfig.backoffMs[attempt]);
    }
  }
};
```

## Logging Hooks

```typescript
const vizHooks = {
  onChartRender: (chartId, duration) => {
    console.log(`[VIZ] Chart ${chartId} rendered in ${duration}ms`);
    metrics.histogram('chart.render_time', duration);
  },

  onInteraction: (chartId, event) => {
    console.log(`[VIZ] Interaction on ${chartId}: ${event.type}`);
    analytics.track('chart_interaction', { chartId, event });
  },

  onError: (chartId, error) => {
    console.error(`[VIZ] Error on ${chartId}: ${error.message}`);
    metrics.increment('chart.errors');
  }
};
```

## Unit Test Template

```typescript
describe('Data Visualization Skill', () => {
  describe('Chart Selection', () => {
    it('should recommend line chart for time series', () => {
      const result = selectChart({
        dataType: 'time_series',
        comparison: 'trend'
      });
      expect(result.primary).toBe('line');
    });

    it('should warn against pie chart for >5 categories', () => {
      const result = selectChart({
        dataType: 'categorical',
        categories: 8
      });
      expect(result.warnings).toContain('TOO_MANY_CATEGORIES');
    });
  });

  describe('Accessibility', () => {
    it('should validate color contrast', () => {
      const isValid = validateContrast('#2563eb', '#ffffff');
      expect(isValid).toBe(true);
    });

    it('should require alt text', () => {
      const config = { type: 'bar' };
      const errors = validateAccessibility(config);
      expect(errors).toContain('MISSING_ALT_TEXT');
    });
  });
});
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Chart looks cluttered | Too many data points | Aggregate or use sampling |
| Colors look washed out | Low saturation | Increase saturation for key elements |
| Hard to read on mobile | Fixed dimensions | Use responsive breakpoints |
| Colorblind users can't read | Red-green only encoding | Add patterns or secondary encoding |
| Legend confusing | Too many series | Limit to 5-7 or use direct labels |

## Resources

- **Edward Tufte**: The Visual Display of Quantitative Information
- **Stephen Few**: Information Dashboard Design
- **Cole Nussbaumer**: Storytelling with Data
- **WCAG 2.1**: Web Content Accessibility Guidelines
- **IBCS**: International Business Communication Standards

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01 | Initial release |
| 2.0.0 | 2025-01 | Production-grade with accessibility |
