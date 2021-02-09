import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd


# -------------------------------------------------------------------------------------
# Import the cleaned data (importing csv into pandas)
df = pd.read_csv("Books_clean.csv")
df = df[df['pred_rating']>= 7 ]



df['Star Rating'] = df['pred_rating'].apply(lambda x:
                                       '⭐⭐⭐⭐⭐' if x >= 10 else (
                                          '⭐⭐⭐⭐' if x >= 9 and x < 10 else (
                                              '⭐⭐⭐' if x >= 8 and x < 9 else (
                                                   '⭐⭐' if x >= 7 and x < 8 else (
                                                       '⭐' if x <= 7 else '')))))

# Creating an ID column name gives us more interactive capabilities

#print(df.columns)

# -------------------------------------------------------------------------------------
# App layout
app = dash.Dash(__name__, prevent_initial_callbacks=True) # this was introduced in Dash version 1.12.0
server = app.server
# Sorting operators (https://dash.plotly.com/datatable/filtering)
app.layout = html.Div([
html.H1("Books Recommender Based Collaborative Filtering", style={'text-align': 'center'}),
html.Br(),
html.H4("Instructions : Please enter sign '=' followed by your User ID to see the most recommended books for you ", style={'text-align': 'left'}),
html.H4("               Use the filtering options availble in the App to explore the books with the ratings availble ", style={'text-align': 'left'}),
html.H4("               Use the operator signs '=','<','>' with text of number fields to explore the data availble", style={'text-align': 'left'}),
html.Br(),
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True,}
            if i == "User_id" or i == "ISBN" or i =="Book_title"
            else {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True, }
            for i in df.columns

                     ],
        data=df.to_dict('records'),  # the contents of the table
        editable=False,              # allow editing of data inside all cells
        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        sort_mode="multi",         # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
        row_deletable=False,         # choose if user can delete a row (True) or not (False)
        selected_columns=[],        # ids of columns that user selects
        selected_rows=[],           # indices of rows that user selects
        page_action="native",       # all data is passed to the table up-front or not ('none')
        page_current=0,             # page number that user is on
        page_size=10,                # number of rows visible per page
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'minWidth': 100, 'maxWidth': 100, 'width': 100
        },



        style_cell_conditional=[    # align text columns to left. By default they are aligned to right
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Book_title', 'pred_rating']
        ],
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),

    html.Br(),
    html.Br(),
    html.Div(id='bar-container'),
    html.Div(id='choromap-container')

])


# -------------------------------------------------------------------------------------
# Create bar chart
@app.callback(
    Output(component_id='bar-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
     Input(component_id='datatable-interactivity', component_property='selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
     Input(component_id='datatable-interactivity', component_property='active_cell'),
     Input(component_id='datatable-interactivity', component_property='selected_cells')]
)
def update_bar(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows,
               order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):
    print('***************************************************************************')
    print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    print('---------------------------------------------')
    print("Indices of selected rows if part of table after filtering:{}".format(slctd_row_indices))
    print("Names of selected rows if part of table after filtering: {}".format(slct_rows_names))
    print("Indices of selected rows regardless of filtering results: {}".format(slctd_rows))
    print('---------------------------------------------')
    print("Indices of all rows pre or post filtering: {}".format(order_of_rows_indices))
    print("Names of all rows pre or post filtering: {}".format(order_of_rows_names))
    print("---------------------------------------------")
    print("Complete data of active cell: {}".format(actv_cell))
    print("Complete data of all selected cells: {}".format(slctd_cell))

    dff = pd.DataFrame(all_rows_data)

    # used to highlight selected countries on bar chart
    colors = ['#7FDBFF' if i in slctd_row_indices else '#0074D9'
              for i in range(len(dff))]

    if "User_id" in dff and "Book_title" in dff:
        return [
            dcc.Graph(id='bar-chart',
                      figure=px.bar(
                          data_frame=dff,
                          x="Book_title",
                          y='pred_rating',
                          labels={"Book Title": "Rating"}
                      ).update_layout(showlegend=False, xaxis={'categoryorder': 'total ascending'})
                      .update_traces(marker_color=colors, hovertemplate="<b>%{y}%</b><extra></extra>")
                      )
        ]


# -------------------------------------------------------------------------------------



# -------------------------------------------------------------------------------------
# Highlight selected column
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# -------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run_server(debug=True)