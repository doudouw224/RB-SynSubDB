import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.colors as colors

# Brain region name mapping (English to English with abbreviations)
brain_region_names = {
    "Anterior cortex": "Anterior Cortex (AC)",
    "Posterior cortex": "Posterior Cortex (PC)",
    "Hippocampus": "Hippocampus (HIP)",
    "Striatum": "Striatum (ST)",
    "Olfactory bulb": "Olfactory Bulb (OB)",
    "Cerebellum": "Cerebellum (CB)"
}

def create_brain_map_tab(df_mean, group_names, group_colors):
    """
    Create a tab for protein expression levels in different brain regions
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4("Protein Expression in Different Brain Regions", className="card-title text-center mb-4"),
                dbc.Row(
                    [
                        dbc.Label("Select Protein", html_for="gene-select", width="auto"),
                        dbc.Col(
                            dcc.Dropdown(
                                id="gene-select",
                                options=[{"label": gene, "value": gene} for gene in df_mean["GENE NAME"].unique()],
                                placeholder="Enter or select a protein",
                                searchable=True,
                                clearable=True,
                                style={"width": "100%"}
                            ),
                            className="me-2",
                        ),
                    ],
                    align="center",
                    className="mb-3",
                ),
                html.Div(id="brain-map-visualization", className="mt-3"),
            ]
        ),
        className="mt-3",
    )

def register_brain_map_callbacks(app, df_mean, group_names, group_colors):
    """
    Register callbacks related to protein expression levels in different brain regions
    """
    @app.callback(
        Output("brain-map-visualization", "children"),
        [Input("gene-select", "value")]
    )
    def update_brain_map(selected_gene):
        if not selected_gene:
            # Display default prompt message
            return html.Div([
                html.P("Please select a protein to view its expression levels in different brain regions", className="text-center mt-3")
            ])
        
        # Get expression data for the selected protein
        gene_data = df_mean[df_mean["GENE NAME"] == selected_gene].iloc[0]
        
        # Calculate the range of expression values
        min_value = min([gene_data[region] for region in group_names])
        max_value = max([gene_data[region] for region in group_names])
        
        # Create bar chart
        fig = go.Figure()
        for group in group_names:
            fig.add_trace(go.Bar(
                x=[brain_region_names.get(group, group)],
                y=[gene_data[group]],
                name=group,
                marker_color=group_colors[group],
                hovertemplate='<b>%{x}</b><br>Expression Level: %{y:.2f}'
            ))
        fig.update_layout(
            title={
                'text': f"Expression Levels of {selected_gene} in Brain Regions",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            yaxis_title="Expression Level",
            xaxis_title="Brain Region",
            height=400,
            margin={"t": 80, "b": 70, "l": 70, "r": 30},
            legend_title="Brain Region",
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Roboto"
            )
        )
        return html.Div([
            html.H5(f"Expression Distribution of {selected_gene} in Brain Regions", className="text-center mb-3"),
            dcc.Graph(figure=fig),
            html.Div([
                html.P(f"Expression Range: {min_value:.2f} - {max_value:.2f}", className="text-center mt-2 small text-muted"),
                html.P("Click on the legend to hide/show specific brain region data", 
                       className="text-center mt-1 small font-italic text-info")
            ])
        ], className="bar-chart-container")
    
    return app

# Add SVG path parsing function

# Add SVG path parsing function
def parse_svg_paths(svg_path_data_list):
    """Parse SVG path data"""
    from svgpathtools import parse_path, Line, CubicBezier, QuadraticBezier
    
    all_segments = []
    all_vertex_labels = []
    all_segment_labels = []
    vertex_counter = 1

    for svg_path_data in svg_path_data_list:
        path = parse_path(svg_path_data)
        segments = []
        vertex_labels = []
        segment_labels = []

        for segment in path:
            if hasattr(segment, 'start') and hasattr(segment, 'end'):
                start_point = (segment.start.real, 2 * 600 - segment.start.imag)  # y-coordinate flip
                end_point = (segment.end.real, 2 * 600 - segment.end.imag)       # y-coordinate flip

                if isinstance(segment, Line):
                    segments.append(('line', start_point, end_point))
                    vertex_counter += 2
                elif isinstance(segment, CubicBezier):
                    control1 = (segment.control1.real, 2 * 600 - segment.control1.imag)  # y-coordinate flip
                    control2 = (segment.control2.real, 2 * 600 - segment.control2.imag)  # y-coordinate flip
                    segments.append(('cubicbezier', start_point, control1, control2, end_point))
                    vertex_counter += 2
                elif isinstance(segment, QuadraticBezier):
                    control = (segment.control.real, 2 * 600 - segment.control.imag)  # y-coordinate flip
                    segments.append(('quadraticbezier', start_point, control, end_point))
                    vertex_counter += 2

        seen = set()
        unique_vertex_labels = []
        for label, point in vertex_labels:
            if point not in seen:
                seen.add(point)
                unique_vertex_labels.append((label, point))
            
        all_segments.append(segments)
        all_vertex_labels.append(unique_vertex_labels)
        all_segment_labels.append(segment_labels)
    
    return all_segments, all_vertex_labels, all_segment_labels
    
# Add Bezier curve calculation function
def calculate_bezier_points(start, control1, control2, end, num_points=50):
    """Calculate points on a cubic Bezier curve"""
    import numpy as np
    t_values = np.linspace(0, 1, num_points)
    points = [
        (
            start.real * (1 - t)**3 + 3 * control1.real * t * (1 - t)**2 + 3 * control2.real * t**2 * (1 - t) + end.real * t**3,
            start.imag * (1 - t)**3 + 3 * control1.imag * t * (1 - t)**2 + 3 * control2.imag * t**2 * (1 - t) + end.imag * t**3
        ) for t in t_values
    ]
    return points
    
# Add quadratic Bezier curve calculation function
def calculate_quadratic_points(start, control, end, num_points=50):
    """Calculate points on a quadratic Bezier curve"""
    import numpy as np
    t_values = np.linspace(0, 1, num_points)
    points = [
        (
            start.real * (1 - t)**2 + 2 * control.real * t * (1 - t) + end.real * t**2,  # x-coordinate remains unchanged
            start.imag * (1 - t)**2 + 2 * control.imag * t * (1 - t) + end.imag * t**2  # y-coordinate
        ) for t in t_values
    ]
    return points