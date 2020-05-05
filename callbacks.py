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
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id != "create_network_submit_button":
        raise PreventUpdate
    batfish = Batfish(batfish_host)
    batfish.set_network(network_name)


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
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id != "delete_network_submit_button":
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
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id != "set_batfish_host_submit_button":
        raise PreventUpdate
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

@app.callback([Output('output-data-upload', 'children'),
               Output('create-snapshot-name', 'invalid')],
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
        device_html_list = html.Ul(
            [html.Li(x) for x in device_config_filenames])
    if host_config_filenames is not None:
        host_html_list = html.Ul(
            [html.Li(x) for x in host_config_filenames])
    if iptables_config_filenames is not None:
        iptable_html_list = html.Ul(
            [html.Li(x) for x in iptables_config_filenames])
    if aws_config_filenames is not None:
        aws_html_list = html.Ul(
            [html.Li(x) for x in aws_config_filenames])
    if misc_config_filenames is not None:
        misc_html_list = html.Ul(
            [html.Li(x) for x in misc_config_filenames])

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
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not batfish_network:
        raise PreventUpdate

    if button_id == "create_snapshot_submit_button":
        if snapshot_name == "":
            return all_children, True
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
        device_html_list = None
        host_html_list = None
        iptable_html_list = None
        aws_html_list = None
        misc_html_list = None

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
        return all_children, False
    return all_children, False



@app.callback(
    Output("delete_snapshot_hidden", "children"),
    [Input("modal-select-network-button", "value"),
     Input("delete_snapshot_submit_button", "n_clicks"),
     Input("delete_snapshot_dropdown", "value")],
    [State("batfish_host_input", "value")]
)
def delete_snapshot(batfish_network,submit, delete_snapshot, batfish_host):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if not submit:
        raise PreventUpdate
    if button_id == "delete_snapshot_submit_button":
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

                            dcc.Dropdown(
                                id="traceroute_src_interface",
                                placeholder='Select Source',
                                options=interfaces,

                            )




                            ]),
                        ),
                        dbc.Col(
                            dbc.InputGroup(
                            [

                                html.Div(
                                    id="traceroute_dst_type_dropdown_div",
                                    children=[
                                        dcc.Dropdown(
                                            id="traceroute_dst_type_dropdown",
                                            options=[{'label': 'IP','value': 'IP'},
                                                    {'label': 'Interface','value': 'Interface'}],
                                            value="Interface",

                                        )
                                    ],

                                ),

                                html.Div(
                                    id="traceroute_dst_input",
                                    children=[
                                        dcc.Dropdown(
                                            id="traceroute_dst",
                                            placeholder='Select Destination',
                                            options=interfaces,

                                        )
                                    ],

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
                                dbc.Button("Trace!",
                                           id="main_page_traceroute_submit",
                                           disabled=True)),
                        ),




                    ]),
                    dbc.Row(id="traceroute-alter-node"),

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

            html.Fieldset(
                id="chaos_traceroute_fieldset"),




        ],

    ),




############################ Trace Route ####################################
@app.callback(
    [Output("main_page_forward_traceroute_graph", "children"),
     Output("main_page_forward_traceroute_collapse", "children"),
     Output("main_page_reverse_traceroute_graph", "children"),
     Output("main_page_reverse_traceroute_collapse", "children"),
     ],
    [
        Input("traceroute_src_interface", "value"),
        Input("traceroute_dst", "value"),
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


    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id != "main_page_traceroute_submit":
        raise PreventUpdate
    batfish = Batfish(host_value)
    batfish.set_network(network_value)
    result = batfish.traceroute(source, destination, bidir, snapshot_value)
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

    return forward_flow_graph, forward_flow_traces, reverse_flow_graph, reverse_flow_traces,

#Fail nodes and interfaces

@app.callback(
    [Output('traceroute-alter-node', 'children'),
     Output('chaos_traceroute_fieldset', 'children'),
     Output('traceroute_failure_switch', 'disabled'),
     Output('traceroute_failure_switch', 'on')],
    [Input('traceroute-cytoscape', 'tapNodeData'),
     Input('traceroute-cytoscape', 'elements')],
    [State("batfish_host_input", "value"),
     State("select-network-button", "value"),
     State("select-snapshot-button", "value")]
)
def get_chaos_form(node_data, graph_elements, batfish_host, batfish_network, original_snapshot):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if node_data == None:
        raise PreventUpdate

    if node_data:
        node = node_data["id"]
        traceroute_nodes = []
        try:
            for traceroute_node in graph_elements:
                traceroute_nodes.append(traceroute_node['data']['label'])
        except KeyError:
            pass


        batfish = Batfish(batfish_host)
        batfish.set_network(batfish_network)
        batfish.set_snapshot(original_snapshot)

        batfish_df = batfish.get_info("nodeProperties")
        batfish_df = batfish_df.set_index('Node')


        nodes_dict = [{'label': node,
                       'value': node}
                      for node in set(traceroute_nodes)]

        interfaces = batfish_df.loc[node].at['Interfaces']

        interfaces_dict = [{'label': '',
                       'value': ''}]

        interfaces_dict += [{'label': interface,
                       'value': interface}
                      for interface in interfaces]

        form_children = [
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupAddon("Deactivate Node", addon_type="prepend"),
                        dbc.Select(
                            id="traceroute_deactivate_node",
                            options=nodes_dict,
                            value=node,
                        ),

                    ]),
            ),

            dbc.Col(
                id="traceroute_deactivate_interface_col",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("Deactivate Interface",
                                                addon_type="prepend"),
                            dbc.Select(
                                id="traceroute_deactivate_interface",
                                options=interfaces_dict,
                                value='',
                            ),

                        ]),
                ],

            ),
            dbc.Col(
                html.Div(
                    dbc.Button("Chaos!", id="chaos_traceroute_submit")),
            ),
            dbc.Col(
                width=1,
                children=[
                    html.Div(
                        className="traceroute_failure_switch_div",
                        children=[
                            daq.PowerButton(
                                id='traceroute_failure_switch',
                                on=True,
                                label="Turn Off Chaos?",
                                labelPosition="top",
                            ),

                        ]),
                ],

            ),
        ]

        fieldset_children = [html.Legend("Chaos Trace Route"),
                 html.Div(id="chaos_traceroute_graph"),
                 html.Div(id="chaos_traceroute_collapse"),

                 ]

        return form_children, fieldset_children, False, True

@app.callback(
    Output('traceroute_deactivate_interface', 'options'),
    [Input('traceroute_deactivate_node', 'value')],
    [State("batfish_host_input", "value"),
     State("select-network-button", "value"),
     State("select-snapshot-button", "value")]
)
def display_interfaces_for_node(deactivated_node, batfish_host,
                       batfish_network, original_snapshot):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]


    if button_id != "traceroute_deactivate_node":
        raise PreventUpdate

    batfish = Batfish(batfish_host)
    batfish.set_network(batfish_network)
    batfish.set_snapshot(original_snapshot)

    batfish_df = batfish.get_info("nodeProperties")
    batfish_df = batfish_df.set_index('Node')


    interfaces = batfish_df.loc[deactivated_node].at['Interfaces']

    interfaces_dict = [{'label': '',
                        'value': ''}]

    interfaces_dict += [{'label': interface,
                         'value': interface}
                        for interface in interfaces]
    options = interfaces_dict
    return options

@app.callback(
    [Output("chaos_traceroute_graph", "children"),
     Output("chaos_traceroute_collapse", "children"),
     ],
    [
        Input("traceroute_src_interface", "value"),
        Input("traceroute_dst", "value"),
        Input("chaos_traceroute_submit", "n_clicks"),
        Input('traceroute_deactivate_node', 'value'),
        Input('traceroute_deactivate_interface', 'value')

    ],
    [State("batfish_host_input", "value"),
     State("select-network-button", "value"),
     State("select-snapshot-button", "value")],
)
def set_chaos_trace_graph(source,
                           destination,
                           submit,
                           deactivated_node,
                           deactivated_interface,
                           host_value,
                           network_value,
                           snapshot_value):


    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    deactivated_nodes = []
    deactivated_interfaces = []

    if button_id != "chaos_traceroute_submit":
        raise PreventUpdate
    batfish = Batfish(host_value)
    batfish.set_network(network_value)
    reference_snapshot = snapshot_value + "_FAIL"
    bidir = False
    deactivated_nodes.append(deactivated_node)
    deactivated_interfaces.append(deactivated_interface)
    batfish.network_failure(snapshot_value, reference_snapshot, deactivated_nodes, deactivated_interfaces)
    result = batfish.traceroute(source, destination, bidir, reference_snapshot)
    chaos_flow_details = get_traceroute_details('forward', result, False, True)
    chaos_flow_graph = chaos_flow_details[0]
    chaos_flow_traces = chaos_flow_details[1]

    return chaos_flow_graph, chaos_flow_traces


@app.callback(
    Output('main_page_traceroute_bidir_switch', 'on'),
    [Input("traceroute_failure_switch", "on")],
)
def display_interfaces_for_node(chaos_switch):
    if chaos_switch:
        return False


@app.callback(
    [Output('traceroute-alter-node', 'children'),
     Output('chaos_traceroute_fieldset', 'children')],
    [Input("traceroute_failure_switch", "on")],
)
def display_interfaces_for_node(chaos_switch):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]


    if button_id != "traceroute_failure_switch":
        raise PreventUpdate

    children = []
    fieldset_children = []
    if not chaos_switch:
        return children, fieldset_children



@app.callback(
    Output('traceroute_dst_input', 'children'),
    [Input("traceroute_dst_type_dropdown", "value")],
    [State("batfish_host_input", "value"),
     State("select-network-button", "value"),
     State("select-snapshot-button", "value")],
)
def set_dst_type_input(dst_type, host_value, network_value, snapshot_value):

    if not dst_type:
        raise PreventUpdate

    batfish = Batfish(host_value)
    batfish.set_network(network_value)
    batfish.set_snapshot(snapshot_value)

    if dst_type == 'Interface':
        batfish_df = batfish.get_layer3_edges()
        options = [str(x) for x in batfish_df["Interface"]]
        interfaces = [{'label': interface,
                       'value': interface}
                      for interface in options]

        children = dcc.Dropdown(
                                id="traceroute_dst",
                                placeholder='Select Destination',
                                options=interfaces,

                            )
    else:

        children = dcc.Input(id="traceroute_dst", type="text", placeholder="Input IP Address", className="traceroute_dst_ip_input",
                             style= dict(borderTopLeftRadius = "0px",
                                         borderBottomLeftRadius = "0px",
                                         height="34px")),

    return children


@app.callback(
    Output('main_page_traceroute_submit', 'disabled'),
    [Input("traceroute_src_interface", "value"),
     Input("traceroute_dst", "value")],
)
def set_dst_type_input(src, dst):


    if src == None or dst == None:
      return True
    return False



