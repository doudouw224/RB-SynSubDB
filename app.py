import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, dash_table
import pandas as pd
import plotly.graph_objects as go
from sklearn.impute import KNNImputer
import numpy as np
import brain_map
from brain_map import create_brain_map_tab, register_brain_map_callbacks, brain_region_names

# 1. Data Loading and Preprocessing
try:
    df_raw = pd.read_csv('data.txt', sep='\t')
    df_knn = pd.read_csv('dataKNN.csv')  # Load KNN processed data
except FileNotFoundError as e:
    print(f"Error: {e}, please ensure data files are in the same directory as app.py.")
    exit()

df = df_raw.copy()
gene_names = df['GENE NAME'].tolist()
groups_cols = {
    "Anterior cortex": df.columns[1:4].tolist(),
    "Posterior cortex": df.columns[4:7].tolist(),
    "Hippocampus": df.columns[7:10].tolist(),
    "Striatum": df.columns[10:13].tolist(),
    "Olfactory bulb": df.columns[13:16].tolist(),
    "Cerebellum": df.columns[16:19].tolist()
}
group_names = list(groups_cols.keys())
group_colors = {
    "Anterior cortex": '#e41a1c',
    "Posterior cortex": '#377eb8',
    "Hippocampus": '#4daf4a',
    "Striatum": '#984ea3',
    "Olfactory bulb": '#ff7f00',
    "Cerebellum": '#ffff33'
}

# Missing Value Processing (KNN imputation)
imputer = KNNImputer(n_neighbors=2)  # Use KNN algorithm with 2 neighbors
for group, cols in groups_cols.items():
    df[cols] = df[cols].replace(['NA', ''], np.nan)  # Replace various types of missing values
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')  # Ensure all columns are numeric
    df[cols] = pd.DataFrame(imputer.fit_transform(df[cols]), columns=cols, index=df.index)

# Export processed data to new CSV file
output_file = 'dataKNN.csv'  # Define output filename
df.to_csv(output_file, index=False)  # Export data to current directory without index

# Calculate mean values for each group
df_mean = pd.DataFrame({'GENE NAME': df['GENE NAME']})
for group, cols in groups_cols.items():
    df_mean[group] = df[cols].mean(axis=1)

# 2. Initialize Dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.title = "RB-SynSubDB"  

# 3. Define layout
app.layout = html.Div([
    # Add gradient header
    html.Div(
        html.H1("RB-SynSubDB - Rat Brain Subregional Proteomics Database", className="text-center py-3 mb-0"),
        className="gradient-header"
    ),
    dbc.Tabs(
        [
            dbc.Tab(label="HOME", tab_id="home"),
            dbc.Tab(label="Protein Expression", tab_id="brain_map"),
            dbc.Tab(label="KNN Data", tab_id="knn_list"),
            dbc.Tab(label="ABOUT", tab_id="about"),
        ],
        id="tabs",
        active_tab="home",
    ),
    html.Div(id="content")
])

# HOME page layout
home_tab_content = html.Div(
    [
        html.Div(
            html.Iframe(
                srcDoc=open('assets/neuron_network_bg.svg', 'r', encoding='utf-8').read(),
                style={"width": "100%", "height": "100%", "border": "none"}
            ),
            className="home-bg"
        ),

        dbc.Card(
            dbc.CardBody(
                [
                    html.H2("Welcome to RB-SynSubDB", className="card-title text-center mb-4"),
                    html.Div(
                        [
                            html.Img(src="/assets/brain_regions.svg", style={"width": "100%", "maxWidth": "500px", "margin": "0 auto 20px auto", "display": "block"}),
                            html.P(
                                "RB-SynSubDB is a freely available electronic database containing detailed proteomics information of rat brain subregions.",
                                className="card-text lead text-center mb-3",
                            ),
                            html.P(
                                "The database provides protein expression data for six major subregions of the rat brain (Anterior Cortex, Posterior Cortex, Hippocampus, Striatum, Olfactory Bulb, and Cerebellum), offering important references for neuroscience research.",
                                className="card-text",
                            ),
                            html.P(
                                "For more information about this database, please refer to the ABOUT page.",
                                className="card-text mt-3",
                            ),
                            dbc.Button("Learn More", id="learn-more-btn", color="primary", className="mt-3"),
                        ],
                        className="text-center",
                    ),
                ]
            ),
            className="home-content mt-3",
        )
    ],
    className="home-container",
)

# LIST page layout
list_tab_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Protein Expression Data List", className="card-title text-center mb-4"),
            dbc.Card(
                dbc.CardBody([
                    html.H5("Gene Search", className="card-subtitle mb-3 text-muted"),
                    dbc.Row(
                        [
                            dbc.Label("Enter Gene Name", html_for="gene-name-input", width="auto", className="ms-2 fw-bold"),
                            dbc.Col(
                                dbc.Input(type="text", id="gene-name-input", placeholder="Please enter gene name", className="border-primary"),
                                className="me-2",
                            ),
                            dbc.Col(
                                dbc.Button("Search", id="search-button", color="primary", className="px-4"),
                                width="auto",
                            ),
                        ],
                        align="center",
                        className="mb-3 g-2",
                    ),
                    html.Div(id='search-plot-container', className='plot-container mt-3'),
                ]),
                className="mb-4 border-light",
            ),
            html.H5("Raw Data Table", className="mt-4 mb-3 text-center"),
            html.P("The table below shows the original expression data of all genes in each brain region. Click column headers to sort or use the filter function to find specific data.", 
                   className="text-muted mb-3 small"),
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df_raw.columns],
                data=df_raw.to_dict('records'),
                page_current=0,
                page_size=15,
                page_action='native',
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                column_selectable="single",
                row_selectable="single",
                selected_columns=[],
                selected_rows=[],
                style_cell={'textAlign': 'left', 'padding': '8px', 'font-family': 'sans-serif'},
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #ddd',
                    'textAlign': 'center'
                },
                style_data={
                    'border': '1px solid #ddd'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    }
                ],
                tooltip_delay=0,
                tooltip_duration=None,
            ),
            html.Div([
                html.P("点击表格中的行可查看该基因在各脑区的表达水平可视化图表", 
                       className="text-info small mt-2 text-center font-italic"),
                html.Div(id='row-click-plot-container', className='plot-container mt-3'),
            ]),
        ]
    ),
    className="mt-3",
)

# ABOUT page layout
about_tab_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("About RB-SynSubDB", className="card-title text-center mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Database Overview", className="mt-3 mb-3"),
                    html.P("RB-SynSubDB is a specialized database focused on synaptosomal proteomics in rat brain subregions, designed to provide high-quality reference data for neuroscience research.", className="text-justify"),
                    html.P("Synaptosomes are subcellular structures from neuronal presynaptic terminals, enriched with neurotransmission and synaptic plasticity related proteins. This database employs advanced synaptosomal proteomics technology to systematically analyze synaptosomal protein expression profiles across six major rat brain subregions (Anterior Cortex, Posterior Cortex, Hippocampus, Striatum, Olfactory Bulb, and Cerebellum).", className="text-justify"),
                    html.P("The data collection process utilizes differential centrifugation for synaptosome isolation, combined with high-throughput mass spectrometry for protein identification and quantification, ensuring data reliability and reproducibility. These data are valuable for understanding region-specific synaptic functions and molecular mechanisms of related neurological disorders.", className="text-justify"),
                ], md=12),
            ]),
            html.Hr(),
            html.H5("Citation", className="mt-4 mb-3"),
            html.Div([
                html.P("If you use the RB-SynSubDB database in your research, please cite it appropriately.", className="mb-3"),
            ]),
        ]
    ),
    className="mt-3",
)

brain_map_tab_content = create_brain_map_tab(df_mean, group_names, group_colors)

# KNN data page layout
knn_list_tab_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Protein Expression Data after KNN Processing", className="card-title text-center mb-4"),
            dbc.Card(
                dbc.CardBody([
                    html.H5("Protein Search", className="card-subtitle mb-3 text-muted"),
                    dbc.Row(
                        [
                            dbc.Label("Select Protein", html_for="knn-protein-select", width="auto", className="ms-2 fw-bold"),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="knn-protein-select",
                                    options=[{"label": gene, "value": gene} for gene in df_knn["GENE NAME"].unique()],
                                    placeholder="Enter or select a protein",
                                    searchable=True,
                                    clearable=True,
                                    style={"width": "100%"}
                                ),
                                className="me-2",
                            ),
                        ],
                        align="center",
                        className="mb-3 g-2",
                    ),
                    html.Div(id='knn-protein-details', className='mt-3'),
                ]),
                className="mb-4 border-light",
            ),
            html.H5("Data Table after KNN Processing", className="mt-4 mb-3 text-center"),
            html.P("The table below shows protein expression data in brain regions after KNN algorithm processing, with missing values filled.", 
                   className="text-muted mb-3 small"),
            dash_table.DataTable(
                id='knn-data-table',
                columns=[{"name": i, "id": i} for i in df_knn.columns],
                data=df_knn.to_dict('records'),
                page_current=0,
                page_size=15,
                page_action='native',
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                column_selectable="single",
                row_selectable="single",
                selected_columns=[],
                selected_rows=[],
                style_cell={'textAlign': 'left', 'padding': '8px', 'font-family': 'sans-serif'},
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #ddd',
                    'textAlign': 'center'
                },
                style_data={
                    'border': '1px solid #ddd'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    }
                ],
                tooltip_delay=0,
                tooltip_duration=None,
            ),
            html.Div([
                html.P("Click on the rows in the table to see a graph visualizing the expression level of the protein in each brain region", 
                       className="text-info small mt-2 text-center font-italic"),
                html.Div(id='knn-row-click-plot-container', className='plot-container mt-3'),
            ]),
        ]
    ),
    className="mt-3",
)


# Tab content switch callback
@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def render_tab_content(active_tab):
    if active_tab == "home":
        return home_tab_content
    elif active_tab == "brain_map":
        return brain_map_tab_content
    elif active_tab == "knn_list":
        return knn_list_tab_content
    elif active_tab == "about":
        return about_tab_content
    else:
        return html.P("Content loading error, please refresh the page and try again.")

# Learn more button callback, redirect to About page
@app.callback(
    Output("tabs", "active_tab"),
    [Input("learn-more-btn", "n_clicks")],
    [State("tabs", "active_tab")]
)
def switch_to_about(n_clicks, current_tab):
    if n_clicks and n_clicks > 0:
        return "about"
    return current_tab

# Search button callback, update search result chart
@app.callback(
    Output('search-plot-container', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('gene-name-input', 'value')]
)
def update_search_plot(n_clicks, search_value):
    if n_clicks is None:
        return ''
    if not search_value:
        return html.P("Please enter a gene name to search", style={'color': '#dc3545', 'textAlign': 'center', 'padding': '10px'})

    filtered_gene_names = [gene for gene in gene_names if search_value.lower() in gene.lower()]  # Fuzzy search
    if not filtered_gene_names:
        return html.P(f"No gene names found containing '{search_value}'", style={'color': '#dc3545', 'textAlign': 'center', 'padding': '10px'})

    plots = []
    for gene_name in filtered_gene_names:
        gene_mean_data = df_mean[df_mean['GENE NAME'] == gene_name].iloc[0]
        fig = go.Figure()
        for group in group_names:
            fig.add_trace(go.Bar(
                x=[group],
                y=[gene_mean_data[group]],
                name=group,
                marker_color=group_colors[group],
                hovertemplate='%{y:.2f}'
            ))
        fig.update_layout(
            title={
                'text': f"<b>{gene_name}</b> Expression Levels in Brain Regions",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            yaxis_title="Expression Level",
            xaxis_title="Brain Region",
            margin={"t": 80, "b": 70, "l": 70, "r": 30},
            legend_title="Brain Region"
        )
        plots.append(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig)]), className="mb-4"))

    return plots  # Return chart list

# Data table row click callback, update row click chart
@app.callback(
    [Output('row-click-plot-container', 'children'),
     Output('data-table', 'style_data_conditional')],
    [Input('data-table', 'derived_virtual_data'),
     Input('data-table', 'derived_virtual_selected_rows')]
)
def update_row_click_plot(rows, selected_rows_indices):
    # Base style conditions (odd row background color)
    style_data_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f9f9f9'
        }
    ]
    
    if selected_rows_indices is None or not selected_rows_indices:
        return '', style_data_conditional

    if len(selected_rows_indices) > 1:
        return html.P("Please select a single row to view details", style={'color': '#dc3545', 'textAlign': 'center', 'padding': '10px'}), style_data_conditional

    selected_row_index = selected_rows_indices[0]
    selected_row_data = rows[selected_row_index]
    gene_name = selected_row_data['GENE NAME']
    gene_mean_data = df_mean[df_mean['GENE NAME'] == gene_name].iloc[0]
    
    # Add selected row style
    style_data_conditional.append({
        'if': {'row_index': selected_row_index},
        'backgroundColor': 'rgba(52, 152, 219, 0.2)',
        'border': '1px solid #3498db'
    })
    
    # Calculate expression value range for color mapping (consistent with brain region map)
    min_value = min([gene_mean_data[region] for region in group_names])
    max_value = max([gene_mean_data[region] for region in group_names])

    # Create bar chart
    fig = go.Figure()
    for group in group_names:
        fig.add_trace(go.Bar(
            x=[brain_region_names.get(group, group)],
            y=[gene_mean_data[group]],
            name=group,
            marker_color=group_colors[group],
            hovertemplate='<b>%{x}</b><br>Expression Level: %{y:.2f}'
        ))
    fig.update_layout(
        title={
            'text': f"<b>{gene_name}</b> Expression Levels in Brain Regions",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title="Expression Level",
        xaxis_title="Brain Region",
        margin={"t": 80, "b": 70, "l": 70, "r": 30},
        legend_title="脑区",
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto"
        )
    )
    
    # Create complete visualization card
    visualization_card = dbc.Card(
        dbc.CardBody([
            html.H5(f"{gene_name} Expression Distribution in Brain Regions", className="text-center mb-3"),
            dcc.Graph(figure=fig),
            html.Div([
                html.P(f"Data Range: {min_value:.2f} - {max_value:.2f}", 
                       className="text-center mt-2 mb-0 small text-muted"),
                html.P("Click on the legend to hide/show specific brain region data", 
                       className="text-center mt-1 small font-italic text-info")
            ])
        ]), 
        className="mt-3 shadow-sm"
    )
    
    return visualization_card, style_data_conditional

# KNN protein selection callback, update protein details
@app.callback(
    Output('knn-protein-details', 'children'),
    [Input('knn-protein-select', 'value')]
)
def update_knn_protein_details(selected_protein):
    if not selected_protein:
        return ''
    
    # Get selected protein data
    protein_data = df_knn[df_knn['GENE NAME'] == selected_protein].iloc[0].to_dict()
    
    # Create expression data for each brain region
    region_data = {}
    for group, cols in groups_cols.items():
        region_data[group] = [protein_data[col] for col in cols]
    
    # Create tables and charts
    tables = []
    for group, values in region_data.items():
        table = dbc.Table(
            [
                html.Thead(html.Tr([html.Th(brain_region_names.get(group, group), colSpan=3, className="text-center bg-light")])),
                html.Tbody([
                    html.Tr([
                        html.Th("Sample 1", className="text-center"),
                        html.Th("Sample 2", className="text-center"),
                        html.Th("Sample 3", className="text-center"),
                    ]),
                    html.Tr([
                        html.Td(f"{value:.2f}", className="text-center") for value in values
                    ])
                ])
            ],
            bordered=True,
            hover=True,
            responsive=True,
            className="mb-4",
            style={"fontSize": "0.9rem"}
        )
        tables.append(dbc.Col(table, md=4, className="mb-3"))
    
    # 计算平均值用于图表
    gene_mean_data = df_mean[df_mean['GENE NAME'] == selected_protein].iloc[0]
    
    # Create bar chart
    fig = go.Figure()
    for group in group_names:
        fig.add_trace(go.Bar(
            x=[brain_region_names.get(group, group)],
            y=[gene_mean_data[group]],
            name=group,
            marker_color=group_colors[group],
            hovertemplate='<b>%{x}</b><br>Expression Level: %{y:.2f}'
        ))
    fig.update_layout(
        title={
            'text': f"<b>{selected_protein}</b> Average Expression Levels in Brain Regions",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title="Expression Level",
        xaxis_title="Brain Region",
        margin={"t": 80, "b": 70, "l": 70, "r": 30},
        legend_title="脑区",
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto"
        )
    )
    
    return html.Div([
        html.H5(f"{selected_protein} Detailed Data", className="text-center mb-4"),
        dbc.Row(tables),
        html.Hr(),
        html.H5(f"{selected_protein} Expression Level Visualization", className="text-center mb-3 mt-4"),
        dcc.Graph(figure=fig)
    ])

@app.callback(
    [Output('knn-row-click-plot-container', 'children'),
     Output('knn-data-table', 'style_data_conditional')],
    [Input('knn-data-table', 'derived_virtual_data'),
     Input('knn-data-table', 'derived_virtual_selected_rows')]
)
def update_knn_row_click_plot(rows, selected_rows_indices):
    # Base style conditions (odd row background color)
    style_data_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f9f9f9'
        }
    ]
    
    if selected_rows_indices is None or not selected_rows_indices:
        return '', style_data_conditional

    if len(selected_rows_indices) > 1:
        return html.P("Please select a single row to view details", style={'color': '#dc3545', 'textAlign': 'center', 'padding': '10px'}), style_data_conditional

    selected_row_index = selected_rows_indices[0]
    selected_row_data = rows[selected_row_index]
    gene_name = selected_row_data['GENE NAME']
    gene_mean_data = df_mean[df_mean['GENE NAME'] == gene_name].iloc[0]
    
    # Add selected row style
    style_data_conditional.append({
        'if': {'row_index': selected_row_index},
        'backgroundColor': 'rgba(52, 152, 219, 0.2)',
        'border': '1px solid #3498db'
    })
    
    min_value = min([gene_mean_data[region] for region in group_names])
    max_value = max([gene_mean_data[region] for region in group_names])

    # Create bar chart
    fig = go.Figure()
    for group in group_names:
        fig.add_trace(go.Bar(
            x=[brain_region_names.get(group, group)],
            y=[gene_mean_data[group]],
            name=group,
            marker_color=group_colors[group],
            hovertemplate='<b>%{x}</b><br>Expression Level: %{y:.2f}'
        ))
    fig.update_layout(
        title={
            'text': f"<b>{gene_name}</b> Expression Levels in Brain Regions",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title="Expression Level",
        xaxis_title="Brain Region",
        margin={"t": 80, "b": 70, "l": 70, "r": 30},
        legend_title="脑区",
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto"
        )
    )
    
    # Create complete visualization card
    visualization_card = dbc.Card(
        dbc.CardBody([
            html.H5(f"{gene_name} Expression Distribution in Brain Regions", className="text-center mb-3"),
            dcc.Graph(figure=fig),
            html.Div([
                html.P(f"Data Range: {min_value:.2f} - {max_value:.2f}", 
                       className="text-center mt-2 mb-0 small text-muted"),
                html.P("Click on the legend to hide/show specific brain region data", 
                       className="text-center mt-1 small font-italic text-info")
            ])
        ]), 
        className="mt-3 shadow-sm"
    )
    
    return visualization_card, style_data_conditional

app = register_brain_map_callbacks(app, df_mean, group_names, group_colors)

if __name__ == '__main__':
    app.run_server(debug=True)
knn_tab_label = "LIST"