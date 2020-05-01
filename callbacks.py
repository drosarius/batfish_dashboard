import json
import time
import dash_daq as daq
import dash
import dash_table
import dash_html_components as html
import pandas as pd
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
from components.batfish import Batfish
from components.functions import get_bgp_edges, get_bgp_nodes, getnodes, \
    getparents, getedges, create_traceroute_graph, create_graph, save_file, \
    delete_old_files, get_elements, get_flow_meta_data, \
    get_traceroute_details
from app import app
import dash_bootstrap_components as dbc



@app.callback(
    Output('cytoscape-mouseoverNodeData-output', 'children'),
    [Input('cytoscape', 'mouseoverNodeData')])
def displayTapNodeData(data):
    if data:
        return "You recently hovered over the device: " + data['label']

@app.callback(
    Output('cytoscape-mouseoverEdgeData-output', 'children'),
    [Input('cytoscape', 'mouseoverEdgeData')])
def displayTapEdgeData(data):
    if data:
        try:
            return "You recently hovered over the edge between: " + data[
                'source'] + ' ' + data['source_label'] + " and " + data[
                       'target'] + ' ' + data['target_label']
        except KeyError:
            return "You recently hovered over the edge between: " + data[
                'source'] + ' ' + " and " + data['target']

@app.callback(
    Output("batfishhost-collapse", "is_open"),
    [Input("set-batfish-host-button", "n_clicks"),
     Input("set_batfish_host_submit_button", "n_clicks")
     ],
    [State("batfishhost-collapse", "is_open")],
)
def batfish_host_toggle_collapse(n, submit_button, is_open):
    if n:
        return not is_open
    if submit_button:
        return not is_open
    return is_open

@app.callback(
    Output("batfish-network-output", "children"),
    [Input("create-network-form", "value"),
     Input("create_network_submit_button", "n_clicks")],
    [State("batfish_host_input", "value")],
)
def create_network(network_name,submit,batfish_host):
    if not submit:
        raise PreventUpdate
    batfish = Batfish(batfish_host)
    batfish.set_network(network_name)
    return 0

@app.callback(
    Output("create-network-collapse", "is_open"),
    [Input("create-network-button", "n_clicks"),
     Input("create_network_submit_button", "n_clicks")],
    [State("create-network-collapse", "is_open")],
)
def create_network_toggle_collapse(n, submit_button, is_open):
    if n:
        return not is_open
    if submit_button:
        return not is_open
    return is_open

@app.callback(
    Output("batfish-host-output", "children"),
    [Input("batfish_host_input", "value")]
)
def set_batfish_host(value):
    if not value:
        raise PreventUpdate
    return value


###################### Delete Network ###############################
@app.callback(Output('delete-success', 'children'),
                   [Input('delete_network_submit_button', 'n_clicks'),
                    Input('delete_network_dropdown', 'value')],
                   [State("batfish_host_input", "value")], )
def delete_network(submit, delete_network, batfish_host):
    if not submit:
        raise PreventUpdate
    batfish = Batfish(batfish_host)
    batfish.delete_network(delete_network)



@app.callback(

    [Output("select-network-snapshot-modal", "children"),
     Output("select-network-div", "children"),
     Output("create-network-collapse", "children")],
    [Input("set_batfish_host_submit_button", "n_clicks"),
     Input("batfish_host_input", "value")]
)
def get_batfish_networks(n, value):
    if n:
        batfish = Batfish(value)
        options = [{'label': network, 'value': network} for network in
                   batfish.get_existing_networks()]
        dropdown1 = dcc.Dropdown(
            id="select-network-button",
            placeholder='Select a Network',
            className="main_page_dropdown",
            options=options,
            value=None
        )
        dropdown2 = dcc.Dropdown(
            id="modal-select-network-button",
            placeholder='Select a Network',
            style={'margin': '5px',
                   'width': '150px',
                   },
            options=options,
            value=None
        )
        create_delete_network_children = [

            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Input(
                                id="create-network-form",
                                value="",
                                placeholder="New Network Name"),
                        ],
                        className="mr-3",
                    ),
                    dbc.Button("Submit",
                               id="create_network_submit_button",
                               color="dark",
                               outline=True,
                               size="sm",
                               ),
                    dcc.Dropdown(
                        id="delete_network_dropdown",
                        placeholder='Select a Network',
                        options=options,
                        value=None
                    ),
                    dbc.Button("Delete",
                               id="delete_network_submit_button",
                               color="dark",
                               outline=True,
                               size="sm",
                               ),
                    html.H1(id="delete-success", style={"display":"none"})

                ],
                inline=True,
            )
        ]
        return dropdown2, dropdown1, create_delete_network_children

@app.callback(
    Output("memory-output", "data"),
    [Input("select-network-button", "value")]
)
def test(value):
    return value

@app.callback(
    Output("select-snapshot-div", "children"),
    [Input("batfish_host_input", "value"),
     Input("select-network-button", "value")]
)
def set_batfish_snapshot(host_value, network_value):
    if not network_value:
        raise PreventUpdate
    batfish = Batfish(host_value)
    batfish.set_network(network_value)
    options = [{'label': snapshot, 'value': snapshot} for snapshot in
               batfish.get_existing_snapshots()]
    dropdown = dcc.Dropdown(
        id="select-snapshot-button",
        placeholder='Select Snapshot',
        className="main_page_dropdown",
        options=options,
        value=None

    ),
    return dropdown

@app.callback(
    Output("hidden_div", "children"),
    [Input("select-network-button", "value")]
)
def set_hidden_div(value):
    return value

@app.callback(Output('cytoscape', 'layout'),
                   [Input('dropdown-update-layout', 'value'),
                    Input('select-graph-roots', 'value')])
def update_layout(layout, value):
    if not layout:
        raise PreventUpdate
    if value:
        return {
            'name': layout,
            'animate': True,
            'roots': value
        }
    return {
        'name': layout,
        'animate': True
    }

@app.callback(Output('breadthfirst-roots', 'children'),
                   [Input('dropdown-update-layout', 'value'),
                    Input('cytoscape', 'elements')])
def add_dropdown_for_breadfirst_roots(layout, nodes):

    if layout != 'breadthfirst':
        dropdown = dcc.Dropdown(
            id="select-graph-roots",
            placeholder='Select Graph Roots',
            style={'margin': '5px',
                   'width': '150px',
                   'display': 'none'},

        ),
        return dropdown
    else:
        json_data = json.loads(str(nodes).replace("\'", "\""))
        node_list = []
        while True:
            try:
                for devices in json_data:
                    node_list.append(devices['data']['label'])
            except KeyError:
                break
        options = [{'label': node, 'value': node} for node in node_list]
        dropdown = dcc.Dropdown(
            id="select-graph-roots",
            placeholder='Select Graph Roots',
            style=dict(
                flex='1',
                verticalAlign="middle",
                width="200px"),
            options=options,
            value=None,
            multi=True,

        ),
        return dropdown

@app.callback(Output('create_snapshot_modal', 'is_open'),
                   [Input('create-snapshot-button', 'n_clicks')],
                   [State("create_snapshot_modal", "is_open")], )
def create_snapshot_modal(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(Output('output-data-upload', 'children'),
               [Input('device-configs-upload-data', 'contents'),
                Input('host-configs-upload-data', 'contents'),
                Input('iptables-configs-upload-data', 'contents'),
                Input('aws-configs-upload-data', 'contents'),
                Input('misc-configs-upload-data', 'contents'),
                Input('modal-select-network-button', 'value'),
                Input('create_snapshot_submit_button', 'n_clicks'),
                Input('create-snapshot-name', 'value')],
               [State("device-configs-upload-data", "filename"),
                State("host-configs-upload-data", "filename"),
                State("iptables-configs-upload-data", "filename"),
                State("aws-configs-upload-data", "filename"),
                State("misc-configs-upload-data", "filename"),
                State("batfish_host_input", "value")], )
def create_snapshot_modal(device_configs_upload_content,
                          host_configs_upload_content,
                          iptables_configs_upload_content,
                          aws_configs_upload_content,
                          misc_configs_upload_content,
                          batfish_network,
                          submit,snapshot_name,
                          device_config_filenames,
                          host_config_filenames,
                          iptables_config_filenames,
                          aws_config_filenames,
                          misc_config_filenames,
                          batfish_host):
    device_html_list = None
    host_html_list = None
    iptable_html_list = None
    aws_html_list = None
    misc_html_list = None

    if device_config_filenames is not None:
        device_html_list = html.Ul([html.Li(x) for x in device_config_filenames])
    if host_config_filenames is not None:
        host_html_list = html.Ul([html.Li(x) for x in device_config_filenames])
    if iptables_config_filenames is not None:
        iptable_html_list = html.Ul([html.Li(x) for x in device_config_filenames])
    if aws_config_filenames is not None:
        aws_html_list = html.Ul([html.Li(x) for x in device_config_filenames])
    if misc_config_filenames is not None:
        misc_html_list = html.Ul([html.Li(x) for x in device_config_filenames])

    all_children = html.Div([
        html.Ul(
            children=[
                html.Li(['Device Configs', device_html_list]),
                html.Li(['Host Configs', host_html_list]),
                html.Li(['IP Table Configs', iptable_html_list]),
                html.Li(['AWS Configs', aws_html_list]),
                html.Li(['Misc Configs', misc_html_list]),
            ],
                )
    ])


    if not submit:
        return all_children
    if submit:
        if device_config_filenames is not None:
            for name, data in zip(device_config_filenames,
                                  device_configs_upload_content):
                save_file("device_config", name, data)
        if host_config_filenames is not None:
            for name, data in zip(host_config_filenames,
                                  host_configs_upload_content):
                save_file("host_config", name, data)
        if iptables_config_filenames is not None:
            for name, data in zip(iptables_config_filenames,
                                  iptables_configs_upload_content):
                save_file("iptable_config", name, data)
        if aws_config_filenames is not None:
            for name, data in zip(aws_config_filenames,
                                  aws_configs_upload_content):
                save_file("aws_config", name, data)
        if misc_config_filenames is not None:
            for name, data in zip(misc_config_filenames,
                                  misc_configs_upload_content):
                save_file("misc_config", name, data)
        batfish = Batfish(batfish_host)
        batfish.set_network(batfish_network)
        batfish.init_snapshot(snapshot_name)
        delete_old_files()
        children = []
        return children




@app.callback(
    Output("delete_snapshot_hidden", "children"),
    [Input("modal-select-network-button", "value"),
     Input("delete_snapshot_submit_button", "n_clicks"),
     Input("delete_snapshot_dropdown", "value")],
    [State("batfish_host_input", "value")]
)
def delete_snapshot(batfish_network,submit, delete_snapshot, batfish_host):
    if not submit:
        raise PreventUpdate
    batfish = Batfish(batfish_host)
    batfish.set_network(batfish_network)
    batfish.delete_snapshot(delete_snapshot)



@app.callback(
    Output("delete-snapshot-dropdown-div", "children"),
    [Input("modal-select-network-button", "value")],
    [State("batfish_host_input", "value")]
)
def delete_snapshot_div(network_value, host_value):
    if not network_value:
        raise PreventUpdate
    batfish = Batfish(host_value)
    batfish.set_network(network_value)
    options = [{'label': snapshot, 'value': snapshot} for snapshot in
               batfish.get_existing_snapshots()]
    children = [
        dbc.Form(
            [
                dcc.Dropdown(
                    id="delete_snapshot_dropdown",
                    placeholder='Delete Snapshot',
                    style={'margin': '5px',
                           'width': '150px',
                           },
                    options=options,
                    value=None

                ),
                dbc.Button("Delete",
                           id="delete_snapshot_submit_button",
                           color="dark",
                           outline=True,
                           size="sm",
                           style=dict(
                               margin="5px",
                               height="25px",
                           )),
                html.P(id='delete_snapshot_hidden', style={"display": "none"})
            ],
            inline=True,
        ),

    ]
    return children


################### Ask a Question ##################################
@app.callback(Output('ask-a-question-modal', 'is_open'),
                   [Input('ask-question-button', 'n_clicks')],
                   [State("ask-a-question-modal", "is_open")], )
def open_ask_a_question_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(Output('ask-a-question-table', 'children'),
                   [Input('select-question-button', 'value')],
                   [State("batfish_host_input", "value"),
                    State("select-network-button", "value"),
                    State("select-snapshot-button", "value")], )
def ask_a_question_modal_table(question, host_value, network_value,
                          snapshot_value):
    if question is None:
        raise PreventUpdate
    batfish = Batfish(host_value)
    batfish.set_network(network_value)
    batfish.set_snapshot(snapshot_value)
    batfish_df = batfish.get_info(question)
    batfish_df.to_csv('test.csv', index=False)
    new_df = pd.read_csv('test.csv')
    children = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i, "deletable": True} for i in
                 batfish_df.columns],
        data=new_df.to_dict('records'),
        filter_action="native",
        export_format="csv",
        style_cell={'fontSize': 12, 'font-family': 'sans-serif'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }

    )
    return children

@app.callback(
    Output("placeholder-for-graph", "children"),
    [
        Input("graph-type-tabs", "value"),
    ],
)
def set_update_graph(value):
    if not value:
        raise PreventUpdate
    return html.Div(id='graph-type-tabs-content')

@app.callback(
    Output("graph-type-tabs-content", "children"),
    [
        Input("graph-type-tabs", "value"),
        Input("select-snapshot-button", "value")
    ],
    [State("batfish_host_input", "value"),
     State("select-network-button", "value")],
)
def set_update_graph(graph_type, snapshot_value, host_value, network_value,):
    if not snapshot_value:
        raise PreventUpdate
    time.sleep(.05)
    batfish = Batfish(host_value)
    batfish.set_network(network_value)
    batfish.set_snapshot(snapshot_value)
    if graph_type == "layer3":
        batfish_df = batfish.get_layer3_edges()
        batfish_df.to_csv('batfish_df.csv', index=False)
        new_df = pd.read_csv('batfish_df.csv')
        new_batfish_df = new_df[
            new_df['Interface'].str.match('.*Vlan.*') == False]
        return create_graph(
            getnodes(new_batfish_df) + getedges(new_batfish_df))
    if graph_type == "ospf":
        batfish_df = batfish.get_ospf_edges()
        batfish_df.to_csv('batfish_df.csv', index=False)
        new_df = pd.read_csv('batfish_df.csv')
        new_batfish_df = new_df[
            new_df['Interface'].str.match('.*Vlan.*') == False]
        return create_graph(
            getnodes(new_batfish_df) + getedges(new_batfish_df))
    if graph_type == "bgp":
        batfish_df = batfish.get_bgp_edges()
        return create_graph(getparents(batfish_df) + get_bgp_nodes(
            batfish_df) + get_bgp_edges(batfish_df))

    if graph_type == "traceroute":
        batfish_df = batfish.get_layer3_edges()
        options = [str(x) for x in batfish_df["Interface"]]
        interfaces = [{'label': interface,
                       'value': interface}
                      for interface in options]

        return html.Div(

        children=[

        dbc.Card(
            dbc.CardBody(
                children=[
                    dbc.Row([
                        dbc.Col(
                            dbc.InputGroup(
                            [
                            dbc.InputGroupAddon("Source", addon_type="prepend"),
                                dbc.Select(
                                    id="main_page_traceroute_src",
                                    options=interfaces
                                ),

                            ]),
                        ),
                        dbc.Col(
                            dbc.InputGroup(
                            [
                                dbc.InputGroupAddon("Destination", addon_type="prepend"),
                                dbc.Select(
                                    id="main_page_traceroute_dst",
                                    options=interfaces
                                ),

                            ]),
                        ),
                        dbc.Col(
                                width=1,
                                children=[
                                    html.Div(
                                        className="bidir_switch",
                                        children=[
                                            daq.BooleanSwitch(
                                                id='main_page_traceroute_bidir_switch',
                                                on=False,
                                                label="Bidir",
                                                labelPosition="left",
                                            ),

                                        ]),
                                ],

                        ),
                        dbc.Col(
                            html.Div(
                                dbc.Button("Trace!", id="main_page_traceroute_submit")),
                        )

                    ]),
                ],
            ),
        ),
            html.Fieldset(
                            [html.Legend("Forward Trace Route"),
                              html.Div(
                                  id="main_page_forward_traceroute_graph"),
                              html.Div(
                               id="main_page_forward_traceroute_collapse"),

                          ]),

            html.Fieldset(
                [html.Legend("Reverse Trace Route"),
                 html.Div(id="main_page_reverse_traceroute_graph"),
                 html.Div(id="main_page_reverse_traceroute_collapse"),

                 ]),




        ],

    ),




############################ Trace Route ####################################
@app.callback(
    [Output("main_page_forward_traceroute_graph", "children"),
     Output("main_page_forward_traceroute_collapse", "children"),
     Output("main_page_reverse_traceroute_graph", "children"),
     Output("main_page_reverse_traceroute_collapse", "children")
     ],
    [

        Input("main_page_traceroute_src", "value"),
        Input("main_page_traceroute_dst", "value"),
        Input("main_page_traceroute_submit", "n_clicks"),
        Input("main_page_traceroute_bidir_switch", "on"),


    ],
    [State("batfish_host_input", "value"),
     State("select-network-button", "value"),
     State("select-snapshot-button", "value")],
)
def set_update_trace_graph(source,
                           destination,
                           submit,
                           bidir,
                           host_value,
                           network_value,
                           snapshot_value):
    if not submit:
        raise PreventUpdate
    batfish = Batfish(host_value)
    batfish.set_network(network_value)
    batfish.set_snapshot(snapshot_value)
    result = batfish.traceroute(source, destination, bidir)
    reverse_flow_graph = []
    reverse_flow_traces = []

    if bidir:
        forward_flow_details = get_traceroute_details('forward', result, True)
        forward_flow_graph = forward_flow_details[0]
        forward_flow_traces = forward_flow_details[1]
        reverse_flow_details = get_traceroute_details('reverse', result, True)
        reverse_flow_graph = reverse_flow_details[0]
        reverse_flow_traces = reverse_flow_details[1]
    else:
        forward_flow_details = get_traceroute_details('forward', result, False)
        forward_flow_graph = forward_flow_details[0]
        forward_flow_traces = forward_flow_details[1]

    return forward_flow_graph, forward_flow_traces, reverse_flow_graph, reverse_flow_traces

