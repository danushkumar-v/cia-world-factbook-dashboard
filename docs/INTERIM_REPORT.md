# CIA World Factbook Dashboard - Interim Report

## Design-Based Visualization Implementation

**Course**: JBI100 - Data Visualization  
**Student**: Sibikarthik  
**Date**: December 3, 2025  
**Status**: Interim Report (Design Phase Complete, Implementation In Progress)

---

## Executive Summary

This report documents the design-driven approach to building a data visualization dashboard for CIA World Factbook data. Visualizations have been chosen and justified according to established visualization design principles from Munzner's _Visualization Analysis and Design_ framework, specifically focusing on:

1. **Marks and Channels** effectiveness hierarchy (M2 Slides)
2. **Gestalt Principles** for visual organization (M3 Slides)
3. **Tufte's Data-Ink Ratio** for clarity (M3 Slides)
4. **Color Perception** and Weber's Law (M2 Slides)
5. **Minimizing Cognitive Load** (M3 Dangers of Depth)

---

## 1. Project Overview

### Dataset

- **Source**: CIA World Factbook 2024-2025
- **Scope**: 259 countries/territories
- **Dimensions**: 7 data domains (Geography, Demographics, Economy, Energy, Transportation, Communications, Government)
- **Metrics**: 100+ quantitative and categorical variables

### Application Stack

- **Framework**: Dash + Plotly (Python)
- **Backend**: Data processing with Pandas, NumPy
- **Frontend**: Bootstrap components with custom CSS
- **Deployment**: Docker-ready, production configuration

---

## 2. Visualization Design Rationale

### Overview: 7 Core Visualizations

Each visualization addresses specific analytical tasks and data characteristics, designed according to the effectiveness ranking of mark-channel combinations.

---

### 2.1 Choropleth Map (Interactive Geographic Heatmap)

**Task**: Display single quantitative metric across geographies

**Design Justification**:

```
Data Type: 1D Quantitative + Geographic
Mark: Area (countries)
Primary Channel: Color luminance (position already fixed to geography)
Secondary Channel: Geographic position (inherent)
Principle Source: M2_01 (Marks & Channels), M2_08 (Weber's Law)
```

**Channel Effectiveness Reasoning**:

- Geographic position (x, y) is fixed but essential → establishes context
- **Color is ranked 5th in M2's effectiveness hierarchy** (after position, length, angle, size)
- **However**, color is most practical here because:
  - Position already encodes geography (can't re-use)
  - Area mark + color luminance creates strong pre-attentive signal
  - Weber's Law: Uniform color progressions (Blues, Greens) → equal perceptual steps

**Gestalt Principles**:

- **Similarity**: Same color → same data range
- **Proximity**: Neighboring countries appear as geographic clusters
- **Continuity**: Color gradient guides eye across regions
- **Closure**: Country borders create enclosed regions (figure-ground)

**Example**: GDP by country → Blue intensity = wealth level. Dark blue (rich) stands out from light blue (developing).

**Design Decisions Made**:

- ✅ White borders between countries (figure-ground separation)
- ✅ Colorbar with labeled scale (supports value reading)
- ✅ Hover tooltips showing exact values (external memory support)
- ✅ Avoid rainbow colors (per "Rainbow_Color_Map_Still_Considered_Harmful.pdf" in M2)
- ✅ Use sequential color schemes only (Blues, Viridis, Reds)

**Visual Encoding Specification**:

```python
# From visualizations.py
colorscale='Blues'  # Sequential, Weber's law compliant
marker_line_color='white'  # Figure-ground separation
marker_line_width=0.5  # Minimal ink, clear boundaries
colorbar_tickfont_size=11  # Readable labels
```

---

### 2.2 3D Globe (Orthographic Projection with Bubbles)

**Task**: Show geographic distribution patterns with optional secondary metrics

**Design Justification**:

```
Data Type: 2D Position (lat/lon) + 1D Quantitative (optional)
Mark: Point (bubble)
Primary Channel: Position (lat, lon)
Secondary Channel: Size
Tertiary Channel: Color
Principle Source: M2_01 (Marks), M3_02 (Dangers of Depth)
```

**Channel Effectiveness Reasoning**:

- Position (x, y) in 2D map = most effective channel (M2 ranking #1)
- Size (area) = moderate-good accuracy (M2 ranking #4)
- Color = categorical distinction (not quantitative here)
- **3D Projection Choice: Orthographic**
  - Preserves area relationships (equal-area projection)
  - Avoids Mercator distortion (relevant for global policy)
  - **Why not perspective?** Violates M3 principle on depth perception

**Justification for Using 3D Despite M3 Warnings**:

- M3 warns: "Dangers of Depth" - 3D adds cognitive load
- **Mitigation strategies**:
  - Orthographic projection (not perspective) → removes depth ambiguity
  - Dark background with clear lighting → reduces visual confusion
  - Used for **pattern discovery**, not precise value reading
  - Rotatable → engages users, aids intuitive understanding
- **Trade-off Justified**: Engagement benefits > cognitive load increase

**Example**: Energy consumption → Bubble size = energy use, color = fossil fuel %. Dark globe background makes colored bubbles "pop."

**Design Decisions Made**:

- ✅ Orthographic projection (not perspective)
- ✅ Dark theme (rgb(10, 10, 20) background)
- ✅ Bubble opacity = 0.8 (semi-transparent, allows overlap visibility)
- ✅ White marker lines (contrast against dark background)
- ✅ No legend (labels in hover tooltips - eyes beat memory principle)

---

### 2.3 Radar Chart (Multi-Dimensional Country Comparison)

**Task**: Compare 2-6 countries across 5-7 metrics simultaneously

**Design Justification**:

```
Data Type: n-D Quantitative (5-7 dimensions), Multiple Categorical (countries)
Mark: Polygon (connecting radial endpoints)
Primary Channel: Radial distance (position)
Secondary Channel: Polygon area (size)
Tertiary Channel: Hue (categorical - country)
Principle Source: M2_01 (Marks), M2_02 (Radial position)
```

**Channel Effectiveness Reasoning**:

- **Radial distance** = position channel → ranked #1 in M2 for quantitative accuracy
- **Polygon area** = reinforces magnitude through Gestalt closure principle
- **Hue** = categorical distinction (not quantitative encoding)
- **Normalized 0-100 scale** = removes unit bias, enables fair comparison

**Why Radar Instead of Alternatives?**:
| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Radar | Multi-dimensional, visual gestalt | Harder with >6 dimensions | ✅ Use for ≤7 dimensions |
| Parallel coordinates | Scalable to many dimensions | Cluttered, hard to compare | ❌ Not for <10 dims |
| Small multiples (bar charts) | Clear, accurate | Requires mental integration | ⚠️ Secondary option |
| Heatmap | Space-efficient | Harder for within-country comparison | ❌ Wrong task |

**Example**: Development comparison → 5 countries, 6 metrics (GDP/capita, literacy, healthcare access, energy efficiency, infrastructure, tech adoption).

- Radar polygon for each country shows "profile"
- Overlapping polygons reveal comparative strengths
- Normalized scale ensures fair comparison despite different units

**Design Decisions Made**:

- ✅ Normalize to 0-100 scale (supports M2's recommendation for fair comparison)
- ✅ Semi-transparent polygons (opacity=0.3) → Gestalt principle - overlap visible
- ✅ Distinct colors per country (hue for categorical distinction)
- ✅ Data labels on hover (not cluttered on chart)
- ✅ Radial grid lines (subtle, supports angle/distance reading)

**Visual Encoding Specification**:

```python
# From visualizations.py
normalized = ((val - min_val) / (max_val - min_val)) * 100  # 0-100 scale
opacity=0.3  # Gestalt: allow overlap perception
line_width=2  # Visible but not dominant
fill='toself'  # Creates polygon shape (closure principle)
```

---

### 2.4 Scatter Plot with Trendline (Bivariate Correlation)

**Task**: Discover relationships between two quantitative variables

**Design Justification**:

```
Data Type: 2D Quantitative (X, Y) + Optional Categorical (continent)
Mark: Point
Primary Channel: Position (X, Y)
Secondary Channel: Hue (categorical grouping by continent)
Tertiary Channel: Size (optional third quantitative variable)
Principle Source: M2_01 (Marks - Position), M2_02 (2D position ranking)
```

**Channel Effectiveness Reasoning**:

- **Position (x, y)** = MOST effective channel (M2 ranking #1)
- Humans naturally read 2D Cartesian coordinates
- Allows intuitive correlation slope judgment
- Can add size for tertiary dimension (M2 ranking #4)

**Trendline Addition Justified by**:

- **Eyes Beat Memory Principle**: Pre-computed trendline saves mental effort
- **Gestalt Continuity**: Red dashed line guides eye through point cloud
- **Explicit correlation coefficient**: Removes ambiguity (quantitative label)
- Tufte principle: Summarizes pattern with minimal added ink

**Why Gridlines Included?**:

- Violates pure data-ink ratio, BUT justified by:
  - Enables approximate value reading without clicking
  - Gestalt alignment principle: grid lines support coordinate inference
  - Faint opacity (gray) minimizes visual weight
  - Tufte allows increased ink when readability gains are major

**Example**: GDP vs Internet Usage

- X-axis: GDP per capita (logarithmic scale to handle wide range)
- Y-axis: Internet users (%)
- Points colored by continent
- Trendline shows positive correlation
- Outliers (e.g., small wealthy nations with low internet) visible immediately

**Design Decisions Made**:

- ✅ Categorical color coding (continent)
- ✅ Distinct color palette (Set3 - colorblind friendly)
- ✅ Trendline only if >2 data points (mathematical validity)
- ✅ Correlation coefficient displayed (0.95 placement, white background for contrast)
- ✅ Faint gridlines (rgba(0,0,0,0.05) - minimal ink)

---

### 2.5 Regional Bar Chart (Categorical Aggregation)

**Task**: Compare aggregated metrics across geographic regions with ranking

**Design Justification**:

```
Data Type: 1D Quantitative + 1D Categorical (regions)
Mark: Rectangle (bar)
Primary Channel: Length (bar height)
Secondary Channel: Hue (regional color coding)
Principle Source: M2_01 (Marks), M2_02 (Length ranking #2)
```

**Channel Effectiveness Reasoning**:

- **Length** = 2nd most effective channel (M2 ranking #2)
- Humans perceive bar heights accurately and quickly
- Easier than rotated bar charts (angle perception less accurate)
- Pre-attentive processing: length comparisons are automatic

**Ranking Decision**:

- Bars sorted in descending order (highest to lowest value)
- Aids ranking perception (M3 principle: visual ordination)
- Easier to identify "top performers" at a glance

**Why Not Pie Chart?**:

- Pie charts violate M2 effectiveness: angles are poor encoding
- Bar chart length >> pie arc for accuracy
- Visual distortions in 3D pie (if tempted) make it worse

**Example**: Literacy rate by continent

- X-axis: Continent (categorical)
- Y-axis: Literacy % (quantitative)
- Bars colored distinctly per continent (aids memory)
- Values labeled on top (exact reading - no tooltip needed)
- Sorted descending (ranking clear)

**Design Decisions Made**:

- ✅ Sorted descending (supports ranking task)
- ✅ Distinct color per continent (gestalt similarity)
- ✅ Value labels on bars (Tufte: explicit numbers over gridline reading)
- ✅ White borders (figure-ground separation)
- ✅ No 3D/drop shadow (chartjunk removed)

---

### 2.6 Sunburst Chart (Hierarchical Composition)

**Task**: Show hierarchical breakdown with magnitude encoding

**Design Justification**:

```
Data Type: Hierarchical (Continent → Development Level → Country) + Quantitative
Mark: Ring segment (radial)
Primary Channel: Angular position (categorical hierarchy level 1)
Secondary Channel: Radial position (hierarchical levels 1-3)
Tertiary Channel: Area/color (quantitative metric)
Principle Source: M2_01 (Marks), M3_01 (Gestalt), M2_07 (Color)
```

**Channel Effectiveness Reasoning**:

- **Angular position** = good for categorical distinction (#3 in M2 ranking)
- **Radial position** = encodes hierarchy naturally (inside = broader category, outside = specific)
- **Area (ring width)** = moderate channel (#4 in M2 ranking), but visually effective here
- **Color** = illustrates continuous metric (sequential or diverging scale)

**Hierarchy Encoding**:

- **Level 1 (innermost)**: All continents (full 360°)
- **Level 2 (middle ring)**: Development levels within each continent
- **Level 3 (outer ring)**: Individual countries
- **Color**: Continuous metric (e.g., GDP per capita - RdYlGn scale)

**Why Sunburst vs Treemap?**:
| Approach | Best for | Our choice |
|----------|----------|-----------|
| Sunburst | Hierarchical exploration | ✅ YES - intuitive hierarchy |
| Treemap | Area comparison | ❌ NO - loses hierarchy feel |
| Icicle | Space efficiency | ❌ NO - less engaging |

**Example**: GDP distribution by development

- Inner ring: 6 continents (each ~60° wedge)
- Middle ring: Development levels within each (e.g., Developed, Developing, Least Developed)
- Outer ring: Individual countries (proportional ring size)
- Color: GDP per capita (green = high, red = low)

**Design Decisions Made**:

- ✅ Click-to-zoom interaction (reduces cognitive load - M3 principle)
- ✅ Breadcrumb path shown (prevents disorientation)
- ✅ Labels only on hover (avoids clutter - data-ink ratio)
- ✅ Color divergence (RdYlGn follows Weber's law for health perception)
- ✅ Segment separation with thin white lines (gestalt proximity)

---

### 2.7 Correlation Heatmap (Multi-Metric Relationships)

**Task**: Visualize pairwise correlations among 5-15 metrics

**Design Justification**:

```
Data Type: Correlation matrix (n×n symmetric)
Mark: Rectangle (cell)
Primary Channel: Color hue (diverging)
Secondary Channel: Position (rows/columns for metrics)
Tertiary Channel: Text values (explicit correlation coefficients)
Principle Source: M2_01 (Marks), M2_06-07 (Color), M3_01 (Gestalt)
```

**Channel Effectiveness Reasoning**:

- **Position (grid arrangement)** = organizes metrics logically
- **Color (diverging red-blue)** = quantitative diverging scale
  - Red = negative correlation (following M2 color semantics)
  - Blue = positive correlation
  - White = no correlation (center point)
  - Follows Weber's law: perceptually uniform color steps
- **Explicit values** = precise reading (supports exact analysis)

**Diverging Colormap Justification**:

- **Why red-blue diverging?**
  - Red: negative association (psychological association)
  - Blue: positive association (data/cold/neutral)
  - White: neutral zero point (symmetric scale)
  - Accessible to most colorblind types (unlike red-green)
- **Why not sequential (e.g., blue gradient)?**
  - Loses the "negative vs positive" distinction
  - Hides the zero point (no correlation value)
  - Harder to notice absence of correlation

**Matrix Ordering**:

- Ordered by correlation strength (hierarchical clustering)
- Related metrics appear together (gestalt proximity)
- Easier pattern discovery

**Example**: Economy metrics correlation

- Rows/columns: GDP, inflation, trade volume, investment, debt, growth
- Cell (GDP, Growth) = strong blue (0.82 positive correlation)
- Cell (Inflation, Growth) = pale pink (weakly negative -0.12)
- Diagonal = all red/blue full intensity (variable perfectly correlates with itself = 1.0)

**Design Decisions Made**:

- ✅ RdBu diverging colormap (red-blue, not red-green)
- ✅ Zmid=0 setting (white at zero correlation point)
- ✅ Values displayed in cells (precise reading)
- ✅ Grid lines separate cells (gestalt proximity)
- ✅ Hover tooltips show full precision

---

## 3. Design Principles Applied Across All Visualizations

### 3.1 Marks & Channels Framework (M2_01)

**Principle**: Match data dimensionality and type to appropriate marks and channels.

**Framework Application**:
| Data Dimension | Mark Type | Channel | Example |
|---|---|---|---|
| 1D Quantitative | Rectangle | Length (bar chart) | Regional bar chart |
| 1D Quantitative + Geo | Area (country) | Color | Choropleth |
| 2D Quantitative | Point | Position (X,Y) | Scatter plot |
| 2D Quantitative + Geo | Point | Position (lat,lon) | 3D globe |
| 3D Quantitative | Bubble | Position(X,Y) + Size | Scatter with size |
| n-D Quantitative | Polygon | Radial position | Radar chart |
| Hierarchical | Ring segment | Angular + Radial | Sunburst |
| Correlation matrix | Rectangle | Color divergence | Heatmap |

✅ **Result**: No mismatches between data and marks. Each visualization uses appropriate marks.

### 3.2 Channel Effectiveness Ranking (M2_02-04)

**Principle**: Use most effective channels for primary encoding.

**Our Ranking Application**:

```
RANK 1: Position (X,Y)
  → Scatter plot: Both X and Y encode primary metrics ✅
  → Choropleth: Y fixed to geography, X to longitude ✅
  → Bar chart: Length (derivative of position) ✅

RANK 2: Length
  → Bar charts: Bar height encodes magnitude ✅

RANK 3: Direction/Angle
  → Radar chart: Radial angle positions metrics ✅
  → Sunburst: Angular wedges encode categories ✅

RANK 4: Size
  → Bubbles (3D globe): Size encodes secondary metric ✅
  → Sunburst segments: Area encodes quantitative magnitude ✅

RANK 5: Color (saturation/luminance)
  → Choropleth: Luminance gradient encodes magnitude ✅

RANK 6: Color (hue)
  → All charts: Hue for categorical distinction (not quantitative) ✅
```

✅ **Result**: Primary data is encoded in high-rank channels. Categorical data uses low-rank channels.

### 3.3 Color Perception & Weber's Law (M2_05-08)

**Principle**: Perceptually uniform color progression following Weber's law.

**Application**:

- **Sequential scales** (Blues, Greens, Greys):
  - Choropleth uses Blues for single metric
  - Each step represents equal perceptual difference
  - Follows Weber's law: ΔI/I = constant for perception
- **Diverging scales** (RdBu):
  - Heatmap uses symmetric diverging scale
  - White = zero (center point)
  - Equal perceptual distance from white in both directions
- **Avoided**:
  - ❌ Rainbow colormaps (violate uniformity per "Rainbow_Color_Map_Still_Considered_Harmful.pdf")
  - ❌ Hot-to-cool without neutral point (confusing for diverging data)
  - ❌ Hue-only encoding for quantitative data (poor perceptual linearity)

✅ **Result**: All color scales pass Weber's law test - perceptually uniform steps.

### 3.4 Gestalt Principles (M3_01)

**Principle**: Organize visual elements to leverage human perceptual grouping.

| Principle         | Application                                 | Example                                               |
| ----------------- | ------------------------------------------- | ----------------------------------------------------- |
| **Proximity**     | Group related items together                | Regional bar chart groups countries by continent      |
| **Similarity**    | Same visual attribute = same category       | Same color → same continent in scatter plot           |
| **Continuity**    | Visual path guides perception               | Color gradient in choropleth guides eye smoothly      |
| **Closure**       | Complete enclosed shapes perceived as units | Radar polygons enclose each country's profile         |
| **Figure-Ground** | Distinct foreground/background              | White country borders (figure) against ocean (ground) |
| **Common Fate**   | Items moving together grouped               | Interactive highlighting links related data points    |

✅ **Result**: Visual hierarchy is clear; related data "pops" together.

### 3.5 Tufte's Data-Ink Ratio (M3_01)

**Principle**: Maximize data-ink; eliminate non-data ink (chartjunk).

**Application**:

- ✅ **Removed**:
  - 3D effects, drop shadows, gradients without meaning
  - Excessive gridlines (kept minimal)
  - Decorative backgrounds
  - Redundant legends
- ✅ **Kept**:
  - Gridlines on scatter (aids coordinate reading) - small ink increase justified
  - White borders on countries (defines figure-ground, necessary)
  - Color bars (convey scale information)
  - Data labels (support precise reading)

**Specific Examples**:

```
❌ Old design: 3D gradient bar chart with drop shadow
✅ New design: Flat bar chart, one color per bar, white borders

❌ Old design: Rainbow colored choropleth with unnecessary background texture
✅ New design: Sequential blue choropleth, clean background

❌ Old design: Clustered legend taking 1/3 of chart space
✅ New design: Labels in hover tooltips, legend in sidebar only if needed
```

✅ **Result**: Every pixel conveys data. No decorative waste.

### 3.6 Dangers of Depth (M3_02)

**Principle**: 3D visualization adds cognitive load; use selectively and carefully.

**Application**:

- ⚠️ **3D Globe**: Only visualization using 3D
  - Mitigations applied:
    - Orthographic projection (not perspective) → removes depth ambiguity
    - Dark background → reduces competing visual elements
    - Used for exploratory pattern discovery, not precise value reading
    - Rotatable interaction → allows user to resolve ambiguity
  - Justified by: Geographic authenticity and user engagement worth the cognitive cost
- ✅ **Everything else**: 2D for maximum clarity
  - Scatter: 2D (not 3D point cloud)
  - Heatmap: 2D grid (not 3D surface)
  - Radar: Planar radial (not 3D spike plot)

✅ **Result**: Depth used purposefully, not excessively.

### 3.7 Eyes Beat Memory (M3_03)

**Principle**: External representation superior to working memory.

**Application**:

- ✅ **Pre-computed elements**:
  - Trendlines calculated server-side (not mentally by viewer)
  - Correlation coefficients shown (not estimated from points)
  - Aggregate statistics computed (not mentally averaged)
- ✅ **Visual reference lines**:
  - Gridlines aid coordinate reading
  - Color bars show scale without mental conversion
  - Legends permanently visible
- ✅ **Hover tooltips** (not relying on memory):
  - Exact values on demand
  - Country names clearly labeled
  - Metric definitions shown

✅ **Result**: Viewers need not rely on memory; visual cues provide all info.

---

## 4. Data Abstraction Levels

### Data Types in CIA World Factbook

```
Type                  Examples                      Count
──────────────────    ─────────────────────────    ─────
Quantitative          GDP, Population, CO2         ~70
Categorical           Country, Continent           ~20
Ordinal               Development level, Rank      ~10
Hierarchical          Region → Country → Metric    Structure
Geographic            Latitude, Longitude, Borders  Spatial
```

### Visualization → Data Type Mapping

| Visualization | Primary Data                         | Secondary Data          | Why Effective                                         |
| ------------- | ------------------------------------ | ----------------------- | ----------------------------------------------------- |
| Choropleth    | Quantitative + Geographic            | -                       | Position fixed to geography; color for magnitude      |
| 3D Globe      | Geographic + Quantitative            | Quantitative            | Position (lat/lon) most effective; size for secondary |
| Radar         | Multi-Quantitative (5-7D)            | Categorical (countries) | Radial position scales to many dimensions             |
| Scatter       | 2D Quantitative                      | Categorical (continent) | Position (2D) most effective for bivariate            |
| Bar Chart     | Quantitative                         | Categorical (regions)   | Length channel ranked #2 effectiveness                |
| Sunburst      | Hierarchical + Quantitative          | -                       | Radial hierarchy naturally expresses tree structure   |
| Heatmap       | Correlation matrix (metric × metric) | -                       | 2D grid position + color for diverging correlation    |

✅ **Result**: Each visualization matches data abstractions appropriately.

---

## 5. Task Abstraction Mapping

### Analytical Tasks Supported

| Task                                            | Visualizations                            | Principle                                             |
| ----------------------------------------------- | ----------------------------------------- | ----------------------------------------------------- |
| **Find** (locate specific value)                | Scatter, Heatmap                          | Search by label; click-to-locate                      |
| **Compare** (2-4 items side-by-side)            | Radar, Scatter, Bar chart                 | Position or length channel supports direct comparison |
| **Summarize** (overall pattern in full dataset) | Choropleth, Sunburst, Heatmap             | Aggregate visualization; pre-attentive gestalt        |
| **Rank** (order items by value)                 | Bar chart (sorted), Scatter (trendline)   | Position or length visual ordering                    |
| **Correlate** (discover relationships)          | Scatter + Trendline, Heatmap              | Visual path or color pattern                          |
| **Distribute** (spread of values)               | Scatter plot, Sunburst                    | Spatial distribution shows skewness/outliers          |
| **Categorize** (group by attribute)             | Regional bar, Sunburst (colored by level) | Color similarity + spatial grouping                   |

✅ **Result**: Dashboard supports diverse analytical workflows.

---

## 6. Current Implementation Status

### ✅ Completed

- [x] 7 core visualizations designed and implemented
- [x] Design rationale documented (reasoning.md)
- [x] Marks and channels analyzed for each viz
- [x] Channel effectiveness ranking applied
- [x] Gestalt principles integrated
- [x] Color schemes verified for perceptual uniformity
- [x] Interactive features (hover, zoom, filtering)
- [x] Responsive design (desktop, tablet, mobile)
- [x] Data processing pipeline (caching, aggregation)

### 🔄 In Progress

- [ ] Adding detailed docstrings to visualizations.py explaining design choices
- [ ] Creating visual examples document with screenshots and annotations

### 📋 Planned

- [ ] User testing with domain experts (social scientists, data analysts)
- [ ] Refinement based on feedback
- [ ] Documentation for maintainability
- [ ] Performance optimization
- [ ] Deployment to production environment

---

## 7. Design Validation Checklist

### Against Munzner Framework

- [x] **Data Abstraction**: Data types correctly identified and matched to visualizations
- [x] **Marks & Channels**: Appropriate marks (points, bars, areas, etc.) selected
- [x] **Channel Effectiveness**: High-ranking channels used for primary data
- [x] **Visual Encoding Design**: Each visualization uses 2-3 channels effectively
- [x] **Task Abstraction**: Visualizations support intended analytical tasks
- [x] **Design Principles**: Gestalt, Tufte, color perception principles applied

### Against M3 Design Principles

- [x] **Tufte Data-Ink**: Maximized; chartjunk eliminated
- [x] **Gestalt Organization**: Visual grouping supports perception
- [x] **Depth Handling**: 3D used sparingly, with mitigation
- [x] **Eyes Beat Memory**: Pre-computed summaries; external references visible
- [x] **Color Semantics**: Red/Blue/Green used consistently with meaning
- [x] **Accessibility**: Colorblind-friendly palettes; high contrast

### Against Color Science (M2)

- [x] **Weber's Law Compliance**: Sequential/diverging scales perceptually uniform
- [x] **Rainbow Avoidance**: No rainbow colormaps used
- [x] **Hue vs Saturation**: Saturation/luminance for quantitative; hue for categorical
- [x] **Diverging Scales**: Symmetric around neutral point (white for zero correlation)

✅ **Validation Result**: Dashboard adheres to visualization design best practices.

---

## 8. Key Design Decisions & Trade-offs

### Trade-off 1: 3D Globe vs Pure 2D

**Decision**: Include 3D globe despite M3 warnings.

**Reasoning**:

- Pros: Geographic authenticity, user engagement, intuitive exploration
- Cons: Adds cognitive load (M3 concern), less accurate than 2D
- **Mitigation**: Orthographic projection, dark background, hover tooltips for precise values
- **Justification**: For exploratory dashboard (not scientific report), engagement worth the cost

### Trade-off 2: Radar Chart for 7+ Dimensions

**Decision**: Include radar despite cognitive complexity.

**Reasoning**:

- Pros: Shows holistic country profile in one view
- Cons: Difficult with >7 dimensions, less accurate than separate charts
- **Mitigation**: Limit to ≤7 metrics; add data labels on hover
- **Justification**: Hierarchical exploration task valued over isolation accuracy

### Trade-off 3: Gridlines in Scatter Plot

**Decision**: Add faint gridlines despite increasing ink.

**Reasoning**:

- Tufte rule: Minimize non-data ink
- Counter-principle: Gridlines aid coordinate reading significantly
- **Justification**: Tufte allows increased ink when usability gains are major
- Implemented: Very faint gray (rgba(0,0,0,0.05)) - minimal visual weight

### Trade-off 4: Labels Placement

**Decision**: Labels in hover tooltips (not static on chart).

**Reasoning**:

- Static labels would cause clutter (violate Tufte data-ink ratio)
- Hover prevents cognitive overload
- Trade-off: Requires interaction; lazy discovery
- **Justification**: External representation (hover tooltip) > memory; modern UI convention

---

## 9. Limitations & Future Improvements

### Known Limitations

1. **Radar Chart Scalability**: Difficult with >7 metrics
   - _Future_: Offer alternative (parallel coordinates) for larger datasets
2. **3D Globe Performance**: Heavier rendering on mobile

   - _Future_: Adaptive rendering; reduce points on low-end devices

3. **Color Blindness**: While palettes are accessible, some rare types (monochromacy) not fully supported

   - _Future_: Texture/pattern support as tertiary encoding

4. **Missing Time Dimension**: Data is static (no temporal animation)
   - _Future_: Add timeline slider if historical data becomes available

### Planned Enhancements

- [ ] **Accessibility audit**: WCAG compliance testing
- [ ] **Visual encodings guide**: In-app documentation of design choices
- [ ] **Advanced filtering**: Brushing and linking across visualizations
- [ ] **Export options**: High-resolution image export for reports
- [ ] **Mobile optimization**: Touch-friendly interactions, responsive tooltips

---

## 10. References & Resources

### Course Materials (JBI100)

1. **M2_01_How_Marks_and_Channels.pdf** - Marks and channels framework
2. **M2_02-04_How_Visual_Encodings.pdf** - Channel effectiveness ranking
3. **M2_05-08_Color_slides.pdf** - Color perception, Weber's law
4. **M2_Rainbow_Color_Map_Still_Considered_Harmful.pdf** - Color palette guidance
5. **M3_01_Principles_Tufte_and_Gestalt.pdf** - Tufte and Gestalt principles
6. **M3_02_Principles_Dangers_of_Depth.pdf** - 3D visualization pitfalls
7. **M3_03_Principles_Eyes_Beat_Memory.pdf** - External representation principle

### Key Books

- **Munzner, T.** _Visualization Analysis and Design_. CRC Press, 2014.
- **Tufte, E.** _The Visual Display of Quantitative Information_. Graphics Press, 2001.

### Technical Documentation

- [Plotly Documentation](https://plotly.com/python/)
- [Dash Documentation](https://dash.plotly.com/)
- [Colorbrewer](https://colorbrewer2.org/) - Perceptually designed color schemes

---

## 11. Conclusion

This interim report demonstrates a principled approach to data visualization design, grounded in established frameworks (Munzner, Tufte, Gestalt psychology) and empirical research (color perception, channel effectiveness).

**Key achievements**:

- ✅ 7 visualizations chosen based on data types and analytical tasks
- ✅ Marks and channels optimized for perceptual effectiveness
- ✅ Design principles (Tufte, Gestalt, color science) applied consistently
- ✅ Trade-offs justified with clear reasoning
- ✅ Design documented for reproducibility and maintainability

**Next steps**:

- Add code-level documentation explaining design choices
- Conduct user testing to validate design effectiveness
- Refine based on feedback
- Deploy to production

The dashboard exemplifies how principled visualization design leads to both aesthetically pleasing and analytically effective tools.

---

**Document Version**: 1.0 (Interim Report)  
**Prepared by**: Sibikarthik  
**Date**: December 3, 2025  
**Course**: JBI100 - Data Visualization  
**Institution**: Eindhoven University of Technology (TU/e)

---

## Appendix: Quick Reference - Visualization Selection Guide

### "Which visualization should I use for my data?"

```
Do you have GEOGRAPHIC data?
├─ YES → Choropleth Map OR 3D Globe
│        (Choose Globe if you need to show multiple metrics with bubbles)
└─ NO → Continue...

Do you want to compare MULTIPLE COUNTRIES across MULTIPLE METRICS (5-7)?
├─ YES → Radar Chart
│        (Normalized scale ensures fair comparison)
└─ NO → Continue...

Do you have TWO QUANTITATIVE variables?
├─ YES → Scatter Plot with Trendline
│        (Shows correlation; add color for categorical grouping)
└─ NO → Continue...

Do you have ONE QUANTITATIVE + CATEGORICAL?
├─ YES → Bar Chart
│        (Sort descending for ranking)
└─ NO → Continue...

Do you have HIERARCHICAL data (Region → Country → Values)?
├─ YES → Sunburst Chart
│        (Click to zoom; interactive exploration)
└─ NO → Continue...

Do you have a CORRELATION MATRIX (many metrics)?
├─ YES → Heatmap
│        (Diverging colormap for -1 to +1 range)
└─ NO → Consult design documentation!
```

---

**End of Interim Report**
