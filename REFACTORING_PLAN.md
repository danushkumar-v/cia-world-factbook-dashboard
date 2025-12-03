# Code Refactoring Plan: Design Principles-Based Visualization Optimization

**Date**: December 3, 2025  
**Course**: JBI100 - Data Visualization  
**Purpose**: Align code with design principles and improve visualization effectiveness

---

## 📋 Current State Analysis

### Visualizations Currently Used in Codebase

1. **Main Visualization Selector** (`viz-type-selector`):

   - Choropleth Map (default)
   - 3D Globe
   - Sunburst Chart
   - Regional Bar Chart

2. **Comparison Tab**:

   - Radar Chart (when chart_type == 'radar')
   - Falls back to blank when other types selected

3. **Correlation Tab**:

   - Scatter Plot (fixed)

4. **Regional Tab**:
   - Regional Bar Chart (fixed)

---

## 🎯 Design Issues Identified & Recommendations

### Issue 1: Comparison Tab - Missing Visualization Options

**Current State**: Only Radar chart implemented, other selections return empty figure

**Design Problem**:

- When user selects different chart types, they get blank visualization
- Violates principle: Always provide meaningful visualization

**Recommended Fix**:

- Add heatmap option for correlation analysis of selected countries' metrics
- Keep radar as primary (multi-dimensional strength)
- Add scatter plot for 2-metric comparison

---

### Issue 2: Main Visualization - "Rainbow" Color Scheme Included

**Current State**: `color-scheme-selector` includes "Rainbow" option

**Design Problem**:

- Rainbow colormaps violate Weber's law (perceptually non-uniform)
- Course material: "Rainbow_Color_Map_Still_Considered_Harmful.pdf"
- Should not be exposed to users

**Recommended Fix**:

- Remove Rainbow from available options
- Add more perceptually uniform alternatives
- Document why (in code comment)

---

### Issue 3: Regional Tab - Single Visualization

**Current State**: Always shows regional bar chart

**Design Problem**:

- Bar charts good for ranking but sometimes heatmap better for pattern discovery
- Limited analytical flexibility

**Recommended Fix**:

- Add option to switch between:
  - Bar chart (for ranking - length channel)
  - Heatmap (for pattern discovery - color channel)

---

### Issue 4: Comparison Panel - No Heatmap for Multi-Metric Analysis

**Current State**: Only radar chart for multiple metrics

**Design Problem**:

- Radar scales poorly beyond 7 dimensions
- No alternative for 8+ metric comparison

**Recommended Fix**:

- Add heatmap option for correlation between countries across metrics
- More scalable, supports larger datasets

---

### Issue 5: Main Visualization - Sunburst Without Context

**Current State**: Sunburst available but no explanation of hierarchical structure

**Design Problem**:

- Users may not understand 3-level hierarchy (Continent → Development → Country)
- No guidance on when to use

**Recommended Fix**:

- Add docstring explaining hierarchy
- Add info icon in UI

---

## ✅ Refactoring Changes Planned

### Change 1: Remove Rainbow Color Scheme

**File**: `src/components/ui_components.py`  
**Action**: Delete 'Rainbow' option from color scheme dropdown

**Justification** (from design docs):

- Rainbow colormaps violate perceptual uniformity (M2_08)
- Equal data differences perceived as unequal due to luminance irregularities
- Sequential/diverging scales like Blues, Reds are perceptually uniform (Weber's law)

---

### Change 2: Enhance Comparison Tab with Multiple Visualization Options

**File**: `src/callbacks/app_callbacks.py`  
**Action**: Add heatmap and scatter options to radar

**Callback modification**:

```python
# Add support for:
if chart_type == 'radar':
    return viz_factory.create_comparison_radar(...)
elif chart_type == 'heatmap':
    return viz_factory.create_heatmap_correlation(...)
elif chart_type == 'scatter':
    # New: add scatter plot for 2-metric comparison
```

**Justification** (from design docs):

- **Radar**: Best for 5-7 metrics (section 2.3)
- **Heatmap**: Scalable to 15+ metrics (section 2.7)
- **Scatter**: Optimal for 2 metrics (section 2.4, position channel most effective)

---

### Change 3: Add Comparison Chart Type Selector

**File**: `src/components/ui_components.py`  
**Action**: Create `comparison-chart-type` dropdown in comparison panel

**Options**:

- 🕷️ Radar Chart (default) - Multi-dimensional profiles
- 🔥 Correlation Heatmap - Metric relationships
- 📍 Scatter Plot - Bivariate comparison

**Justification**:

- Gives users flexibility based on analysis task (M1_06: Task Abstraction)
- Each has distinct strength (documented in reasoning.md)

---

### Change 4: Add Regional Chart Type Selector

**File**: `src/components/ui_components.py`  
**Action**: Create `regional-chart-type` dropdown in regional panel

**Options**:

- 📊 Bar Chart (default) - Ranking
- 🔥 Heatmap - Pattern discovery (continents vs metrics)

**Justification** (from design docs, section 2.5):

- **Bar Chart**: Length channel (ranked #2 in M2_02-04)
  - Best for ranking tasks
  - Clear magnitude comparison
- **Heatmap**: Color + position channels
  - Better for pattern discovery across multiple dimensions
  - Scalable to many metrics

---

### Change 5: Update UI Components Documentation

**File**: `src/components/ui_components.py`  
**Action**: Add design principle comments explaining visualization choices

**Comment**: Add before each visualization selector explaining:

- Which principle it addresses
- When to use this visualization
- Task it supports best

---

## 📝 Implementation Order

1. **Phase 1 - Quick Fixes**:

   - Remove Rainbow colormap ✓
   - Add comments explaining choices

2. **Phase 2 - Add Visualization Flexibility**:

   - Add comparison chart type selector
   - Add regional chart type selector
   - Update callbacks to support new types

3. **Phase 3 - Enhance User Experience**:
   - Add info icons/tooltips explaining visualization choices
   - Add design principle references in comments

---

## 🔄 Callback Logic Changes

### Comparison Chart Callback (Current):

```python
def update_comparison_chart(n_clicks, countries, metrics, chart_type):
    if chart_type == 'radar':
        return viz_factory.create_comparison_radar(...)
    return go.Figure()  # PROBLEM: Returns blank
```

### Comparison Chart Callback (Proposed):

```python
def update_comparison_chart(n_clicks, countries, metrics, chart_type):
    """Update comparison chart with multiple visualization options.

    DESIGN PRINCIPLES (JBI100):
    - Radar (M2_01): Multi-dimensional profile (5-7 metrics) - Position channel
    - Heatmap (M2_01): Correlation patterns (8+ metrics) - Color + Position
    - Scatter (M2_02-04): Bivariate comparison (2 metrics) - Position #1 ranked
    """
    if chart_type == 'radar':
        return viz_factory.create_comparison_radar(merged_data, countries, metrics)
    elif chart_type == 'heatmap':
        # Filter to selected countries, correlate across metrics
        df_filtered = merged_data[merged_data['Country'].isin(countries)]
        return viz_factory.create_heatmap_correlation(df_filtered, metrics)
    elif chart_type == 'scatter' and len(metrics) >= 2:
        # First 2 metrics
        return viz_factory.create_scatter_correlation(
            merged_data[merged_data['Country'].isin(countries)],
            metrics[0], metrics[1],
            color_by='Country'
        )
    return go.Figure()
```

---

## 🎯 Design Principle Mapping

### For Each Visualization Choice in Code:

**Main Visualization Selector**:

- Choropleth: Geographic distribution (M2_02-04: position + color)
- 3D Globe: Geographic multi-metric (M3_02: orthographic projection)
- Sunburst: Hierarchical composition (M2_01: radial hierarchy)
- Regional Bar: Ranking/aggregation (M2_02-04: length channel #2)

**Comparison Tab**:

- Radar: Multi-dimensional (M2_01: radial position)
- Heatmap: Correlation matrix (M2_01: grid + color divergence)
- Scatter: 2D bivariate (M2_02-04: position #1 ranked)

**Regional Tab**:

- Bar: Ranking (M2_02-04: length)
- Heatmap: Pattern (M2_01: color + position grid)

**Color Schemes**:

- Blues/Reds/Greens: Sequential (M2_08: Weber's law)
- Viridis/Plasma/Inferno: Perceptually uniform (M2_08)
- ❌ Rainbow: REMOVED (violates M2_08 uniformity)

---

## 📊 Summary of Changes

| Component     | Current              | Proposed                  | Principle                       |
| ------------- | -------------------- | ------------------------- | ------------------------------- |
| Color schemes | 7 (includes Rainbow) | 6 (remove Rainbow)        | M2_08: Weber's law              |
| Main viz      | 4 types              | 4 types (unchanged)       | M2_01 marks/channels            |
| Comparison    | 1 type + blank       | 3 types                   | M2_02-04: channel effectiveness |
| Regional      | 1 type               | 2 types                   | M2_02-04: task flexibility      |
| Callbacks     | Limited              | Enhanced with design docs | M1_06: task abstraction         |

---

## 🔍 Validation Criteria

After changes, verify:

- ✅ No Rainbow colormap option in UI
- ✅ All chart type selections return meaningful visualizations
- ✅ Comparison tab supports ≥3 visualization types
- ✅ Regional tab supports ≥2 visualization types
- ✅ All code changes have design principle comments
- ✅ Documentation explains when to use each visualization

---

**Next Steps**: Execute planned changes in order of priority.
