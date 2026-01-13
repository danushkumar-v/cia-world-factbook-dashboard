"""
Visualization Components - Clean, Safe, Project-Compatible
Optimized for the CIA World Factbook Dashboard
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Optional


class VisualizationFactory:
    def __init__(self, config):
        self.config = config

    # ------------------------------
    # Helper: Clean metric name
    # ------------------------------
    def _label(self, metric: str) -> str:
        s = metric.replace("_", " ")
        return s.title()

    # ------------------------------
    # 1️⃣ Choropleth (DEFAULT VIEW)
    # ------------------------------
    def create_choropleth_map(
        self,
        df: pd.DataFrame,
        metric: str,
        title: str,
        color_scheme: str = "Viridis",
        projection: str = "natural earth",
    ) -> go.Figure:

        label = self._label(metric)
        df_clean = df.dropna(subset=["Country", metric])

        hover_tmpl = (
            "<b>%{text}</b><br>"
            + label
            + ": %{z:,.2f}<extra></extra>"
        )

        fig = go.Figure(
            data=go.Choropleth(
                locations=df_clean["Country"],
                locationmode="country names",
                z=df_clean[metric],
                text=df_clean["Country"],
                colorscale=color_scheme,
                autocolorscale=False,
                marker_line_color="white",
                colorbar=dict(title=label),
                hovertemplate=hover_tmpl,
            )
        )

        fig.update_geos(
            projection_type=projection,
            showcountries=True,
            showcoastlines=True,
            coastlinecolor="rgba(0,0,0,0.3)",
            landcolor="rgb(240, 240, 240)",
        )

        fig.update_layout(
            title=dict(text=title, x=0.5),
            margin=dict(l=0, r=0, t=40, b=0),
        )

        return fig

    # --------------------------------------------------------
    # 2️⃣ Regional Bar Chart (Comparison)
    # --------------------------------------------------------
    def create_regional_bar_chart(
        self,
        df: pd.DataFrame,
        metric: str,
        agg: str = "mean",
    ) -> go.Figure:

        label = self._label(metric)

        if "Continent" not in df.columns:
            raise ValueError("Dataset missing 'Continent' column")

        df_clean = df.dropna(subset=["Continent", metric])
        df_region = df_clean.groupby("Continent", as_index=False)[metric].agg(agg)
        df_region = df_region.sort_values(metric, ascending=False)

        fig = px.bar(
            df_region,
            x="Continent",
            y=metric,
            title=f"{label} by Continent ({agg.title()})",
            text_auto=".2s",
            labels={"Continent": "Continent", metric: label},
        )

        hover_tmpl = (
            "<b>%{x}</b><br>"
            + label
            + ": %{y:,.2f}<extra></extra>"
        )

        fig.update_traces(hovertemplate=hover_tmpl)

        fig.update_layout(
            xaxis_title="Continent",
            yaxis_title=label,
            margin=dict(l=40, r=20, t=60, b=40),
        )

        return fig

    # --------------------------------------------------------
    # 3️⃣ Sunburst Chart (Hierarchy)
    # --------------------------------------------------------
    def create_sunburst_chart(self, df: pd.DataFrame, metric: str) -> go.Figure:
        label = self._label(metric)

        if "Continent" not in df.columns:
            raise ValueError("Dataset missing 'Continent' column")

        df_clean = df.dropna(subset=["Continent", "Country", metric])

        fig = px.sunburst(
            df_clean,
            path=["Continent", "Country"],
            values=metric,
            color=metric,
            color_continuous_scale="Viridis",
            hover_data={metric: ":,.2f"},
        )

        fig.update_layout(
            title=f"{label} by Continent → Country",
            margin=dict(l=0, r=0, t=60, b=0),
        )

        return fig

    # --------------------------------------------------------
    # 4️⃣ Correlation Matrix (OVERVIEW)
    # --------------------------------------------------------
    def create_heatmap_correlation(
        self,
        df: pd.DataFrame,
        metrics: List[str],
    ) -> go.Figure:
        df_corr = df[metrics].dropna().corr()

        hover_tmpl = (
            "<b>%{x}</b> vs <b>%{y}</b><br>"
            "r = %{z:.2f}<extra></extra>"
        )

        fig = go.Figure(
            data=go.Heatmap(
                z=df_corr.values,
                x=df_corr.columns,
                y=df_corr.columns,
                colorscale="RdBu_r",
                zmin=-1,
                zmax=1,
                colorbar=dict(title="Correlation"),
                hovertemplate=hover_tmpl,
            )
        )

        fig.update_layout(
            title="Correlation Matrix",
            xaxis=dict(tickangle=90),
            yaxis=dict(),
            margin=dict(l=200, r=20, t=90, b=60),
        )

        return fig

    def create_3d_globe(
            self,
            df: pd.DataFrame,
            metric: str,
            title: str,
            color_scheme: str = "Viridis",
    ) -> go.Figure:
        """
        Optional globe-style view using Scattergeo with orthographic projection.

        - If Latitude/Longitude columns exist, uses them.
        - If not, gracefully falls back to the 2D choropleth (no crash).
        """

        label = self._label(metric)

        # If we don't have coordinates, fall back to 2D map
        if "Latitude" not in df.columns or "Longitude" not in df.columns:
            fallback_title = f"{title} (2D map – no coordinates available)"
            return self.create_choropleth_map(
                df=df,
                metric=metric,
                title=fallback_title,
                color_scheme=color_scheme,
                projection="natural earth",
            )

        df_clean = df.dropna(subset=["Latitude", "Longitude", metric])

        if df_clean.empty:
            # No valid rows, also fall back gracefully
            fallback_title = f"{title} (2D map – no valid coordinates)"
            return self.create_choropleth_map(
                df=df,
                metric=metric,
                title=fallback_title,
                color_scheme=color_scheme,
                projection="natural earth",
            )

        # Simple size scaling based on metric
        values = df_clean[metric].astype(float)
        v_min = values.min()
        v_max = values.max()
        # Avoid division by zero
        if v_max > v_min:
            sizes = 6 + 14 * (values - v_min) / (v_max - v_min)
        else:
            sizes = [10.0] * len(values)

        hover_tmpl = (
                "<b>%{text}</b><br>"
                + label
                + ": %{marker.color:,.2f}<extra></extra>"
        )

        fig = go.Figure(
            data=go.Scattergeo(
                lon=df_clean["Longitude"],
                lat=df_clean["Latitude"],
                text=df_clean.get("Country", df_clean.index),
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=values,
                    colorscale=color_scheme,
                    colorbar=dict(title=label),
                    sizemode="area",
                    opacity=0.85,
                ),
                hovertemplate=hover_tmpl,
            )
        )

        fig.update_geos(
            projection_type="orthographic",
            showcoastlines=True,
            showcountries=True,
            landcolor="rgb(240, 240, 240)",
            oceancolor="rgb(225, 240, 255)",
            showocean=True,
        )

        fig.update_layout(
            title=dict(text=title + " (Globe View)", x=0.5),
            margin=dict(l=0, r=0, t=40, b=0),
        )

        return fig

    # --------------------------------------------------------
    # 🔄 Country Comparison – Radar Chart
    # --------------------------------------------------------
    def create_comparison_radar(
        self,
        df: pd.DataFrame,
        countries,
        metrics,
    ) -> go.Figure:
        """
        Radar chart comparing multiple metrics for selected countries.

        - countries: list of country names (or single string)
        - metrics: list of metric column names (or single string)

        If metrics is a single metric, we will still build a valid (but
        slightly degenerate) radar chart.
        """

        # Normalize inputs to lists
        if countries is None:
            countries = []
        if isinstance(countries, str):
            countries = [countries]

        if metrics is None:
            metrics = []
        if isinstance(metrics, str):
            metrics = [metrics]

        # Remove empties
        countries = [c for c in countries if c]
        metrics = [m for m in metrics if m]

        # Fallback: empty figure if nothing selected
        if not countries or not metrics:
            return go.Figure(
                layout=dict(
                    title="Select at least one country and one metric to compare",
                    margin=dict(l=40, r=20, t=60, b=40),
                )
            )

        # Filter data
        cols_needed = ["Country"] + metrics
        for c in cols_needed:
            if c not in df.columns:
                raise ValueError(f"Column '{c}' not found in data.")

        dff = df[df["Country"].isin(countries)][cols_needed].dropna()

        if dff.empty:
            return go.Figure(
                layout=dict(
                    title="No data available for selected countries / metrics",
                    margin=dict(l=40, r=20, t=60, b=40),
                )
            )

        # Melt to long format: Country, Metric, Value
        long_df = dff.melt(
            id_vars="Country",
            value_vars=metrics,
            var_name="Metric",
            value_name="Value",
        )

        # Optional: normalize each metric to [0, 1] for fair comparison
        # so that metrics on very different scales don't dominate.
        norm_df = long_df.copy()
        norm_df["NormValue"] = 0.0

        for m in metrics:
            mask = norm_df["Metric"] == m
            vals = norm_df.loc[mask, "Value"]
            v_min = vals.min()
            v_max = vals.max()
            if v_max > v_min:
                norm_df.loc[mask, "NormValue"] = (vals - v_min) / (v_max - v_min)
            else:
                # All same value → set to 0.5
                norm_df.loc[mask, "NormValue"] = 0.5

        # Build radar (polar) chart
        fig = go.Figure()

        for country in countries:
            c_data = norm_df[norm_df["Country"] == country]

            # Ensure consistent order of metrics around the circle
            c_data = c_data.set_index("Metric").reindex(metrics).reset_index()

            theta = c_data["Metric"].tolist()
            r = c_data["NormValue"].tolist()

            # Close the loop by repeating first point at the end
            if len(theta) > 0:
                theta.append(theta[0])
                r.append(r[0])

            fig.add_trace(
                go.Scatterpolar(
                    r=r,
                    theta=theta,
                    name=country,
                    mode="lines+markers",
                    line=dict(shape="spline"),
                )
            )

        fig.update_layout(
            title="Country Comparison (Normalized Radar Chart)",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickvals=[0, 0.25, 0.5, 0.75, 1.0],
                    ticktext=["0", "0.25", "0.5", "0.75", "1"],
                    title="Normalized value",
                )
            ),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=60, r=60, t=60, b=80),
        )

        return fig

    # --------------------------------------------------------
    # 5️⃣ Detailed Scatter (DETAILS ON DEMAND)
    # --------------------------------------------------------
    # def create_scatter_correlation(
    #     self,
    #     df: pd.DataFrame,
    #     x_metric: str,
    #     y_metric: str,
    #     color_by: Optional[str] = None,
    # ) -> go.Figure:
    #
    #     label_x = self._label(x_metric)
    #     label_y = self._label(y_metric)
    #
    #     cols = [c for c in [x_metric, y_metric, "Country", color_by] if c and c in df.columns]
    #     dff = df[cols].dropna()
    #
    #     fig = px.scatter(
    #         dff,
    #         x=x_metric,
    #         y=y_metric,
    #         color=color_by if color_by and color_by in dff.columns else None,
    #         hover_name="Country" if "Country" in dff.columns else None,
    #         labels={x_metric: label_x, y_metric: label_y},
    #     )
    #
    #     fig.update_layout(
    #         title=f"{label_y} vs {label_x}",
    #         xaxis_title=label_x,
    #         yaxis_title=label_y,
    #         margin=dict(l=50, r=20, t=50, b=50),
    #     )

        # Let Plotly handle %{x} %{y

    def create_scatter_correlation(
            self,
            df: pd.DataFrame,
            x_metric: str,
            y_metric: str,
            color_by: Optional[str] = None,
    ) -> go.Figure:

        label_x = self._label(x_metric)
        label_y = self._label(y_metric)

        cols = [c for c in [x_metric, y_metric, "Country", color_by] if c and c in df.columns]
        dff = df[cols].dropna()

        fig = px.scatter(
            dff,
            x=x_metric,
            y=y_metric,
            color=color_by if color_by and color_by in dff.columns else None,
            hover_name="Country" if "Country" in dff.columns else None,
            labels={x_metric: label_x, y_metric: label_y},
        )

        # Compute Pearson correlation for the title
        try:
            r = dff[x_metric].corr(dff[y_metric])
            corr_text = f" (r = {r:.2f})"
        except Exception:
            corr_text = ""

        fig.update_layout(
            title=f"{label_y} vs {label_x}{corr_text}",
            xaxis_title=label_x,
            yaxis_title=label_y,
            margin=dict(l=50, r=20, t=50, b=50),
        )

        return fig


    # --------------------------------------------------------
    # 6️⃣ Distribution (Statistical Value Idioms)
    # --------------------------------------------------------
    def create_distribution_chart(
        self,
        df: pd.DataFrame,
        metric: str,
        idiom: str = "hist",
        bins: int = 20,
        show_points: bool = False,
        group_by: str = "Continent",
        selected_country: Optional[str] = None,
    ) -> go.Figure:
        """Create a distribution view for a single metric.

        - hist: histogram of values (optionally faceted by group_by)
        - box: box plot by group_by
        - violin: violin plot by group_by (density + summary)
        """

        label = self._label(metric)
        dff = df.dropna(subset=[metric])

        if dff.empty:
            return go.Figure(layout=dict(title="No data available"))

        # Prefer grouping when available
        if group_by not in dff.columns:
            group_by = None

        if idiom == "hist":
            fig = px.histogram(
                dff,
                x=metric,
                nbins=bins,
                color=group_by if group_by else None,
                opacity=0.85,
                hover_data={"Country": True} if "Country" in dff.columns else None,
                labels={metric: label},
                title=f"Distribution of {label}"
                      + (f" by {group_by}" if group_by else ""),
            )
            fig.update_layout(bargap=0.05)

        elif idiom == "box":
            fig = px.box(
                dff,
                x=group_by if group_by else None,
                y=metric,
                points="all" if show_points else False,
                hover_name="Country" if "Country" in dff.columns else None,
                labels={metric: label, group_by: group_by} if group_by else {metric: label},
                title=f"Box plot of {label}" + (f" by {group_by}" if group_by else ""),
            )

        else:  # violin
            fig = px.violin(
                dff,
                x=group_by if group_by else None,
                y=metric,
                box=True,
                points="all" if show_points else False,
                hover_name="Country" if "Country" in dff.columns else None,
                labels={metric: label, group_by: group_by} if group_by else {metric: label},
                title=f"Violin plot of {label}" + (f" by {group_by}" if group_by else ""),
            )

        # Details-on-demand: annotate selected country value
        if selected_country and "Country" in dff.columns and selected_country in set(dff["Country"]):
            row = dff.loc[dff["Country"] == selected_country].iloc[0]
            val = row[metric]
            fig.add_vline(
                x=val,
                line_width=2,
                line_dash="dash",
                annotation_text=selected_country,
                annotation_position="top",
            )

        fig.update_layout(margin=dict(l=50, r=20, t=60, b=50))
        return fig