import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_daq as daq


batfish_questions = ["ipOwners",
                     "nodeProperties",
                     "routes",
                     "layer3Edges",
                     "interfaceProperties",
                     "namedStructures",
                     "definedStructures",
                     "referencedStructures",
                     "unusedStructures",
                     "undefinedReferences",
                     "switchedVlanProperties",
                     "bgpProcessConfiguration",
                     "bgpPeerConfiguration",
                     "bgpSessionCompatibility",
                     "bgpSessionStatus",
                     "bgpEdges",
                     "ospfInterfaceConfiguration",
                     "ospfProcessConfiguration",
                     "ospfSessionCompatibility",
                     "ospfEdges",
                     "ospfAreaConfiguration",
                     "loopbackMultipathConsistency",
                     "filterLineReachability",
                     "initIssues",
                     "fileParseStatus",
                     "parseWarning",
                     "vxlanVniProperties",
                     "vxlanEdges",
                     "evpnL3VniProperties",
                     "detectLoops",
                     "ipsecSessionStatus"]


main_page_graph_tab_selected = dict(
    padding='10px 20px',
    backgroundColor='#555555',
    color='#fff',
    borderBottom='none',
    borderTop='none',
    fontWeight='bold',

)

main_page_layout = html.Div(id='main-page', children=[
        html.Div(
            id='title-bar-div',
            children=[
                html.Header(
                    id='title-bar',
                    children=[
                        html.H1('Batfish Dashboard',
                                id='title-bar-text',
                                )
                    ]
                )
            ]
        ),
        html.Br(),
        html.Div(
            style={
                'position': 'relative',
                'left': '7px'},
            children=[

                html.Div([
                    html.Button(
                        "Set Batfish Host",
                        id="set-batfish-host-button",
                        className="main_page_button",
                    ),
                ],
                    className="main_page_button_div",
                ),
                html.Div([
                    html.Button(
                        "Create/Delete Network",
                        id="create-network-button",
                        className="main_page_button",
                    ),
                ],
                    className="main_page_button_div",
                ),
                html.Div([
                    html.Button(
                        "Create/Delete Snapshot",
                        id="create-snapshot-button",
                        className="main_page_button",
                    ),
                ],
                    className="main_page_button_div",
                ),
                html.Div([],
                         className="main_page_button_div",
                         id='select-network-div',
                         ),
                html.Div([],
                         className="main_page_button_div",
                         id='select-snapshot-div',
                         ),
                html.Div([
                    html.Button(

                        "Ask a Question",
                        id="ask-question-button",
                        className="main_page_button",
                    ),
                ],
                    className="main_page_button_div",
                ),
                html.Div([
                    html.Button(
                        "Chaos Monkey",
                        id="chaos-monkey-button",
                        className="main_page_button",
                    ),
                ],
                    className="main_page_button_div",
                ),

                html.Div(
                    style=dict(
                        width="1000px"
                    ),

                    children=[
                        dbc.Collapse(

                            dbc.Card(
                            className='main_page_card',
                            children=[
                                dbc.CardBody(
                                    children=[
                                        dbc.Form(
                                            [
                                                dbc.FormGroup(
                                                    [
                                                        dbc.Input(
                                                            id="batfish_host_input",
                                                            value="",
                                                            placeholder="Enter host",
                                                            ),

                                                    ],
                                                    className="mr-3",
                                                ),
                                                dbc.Button("Submit",
                                                           id="set_batfish_host_submit_button",
                                                           color="dark",
                                                           outline=True,
                                                           size="sm",
                                                           style=dict(
                                                               height="25px",
                                                           ))

                                            ],
                                            inline=True,
                                        )
                                    ]
                                )
                            ],

                            ),
                            id="batfishhost-collapse",
                        ),

                        dbc.Collapse(
                            dbc.Card(
                            className='main_page_card',
                                children=[
                                dbc.CardBody(
                                    children=[]
                                )
                                ],

                            ),
                            id="create-network-collapse",

                        ),
                    ],
                ),

                dcc.Store(id='memory-output'),
            ],

        ),
        html.Div(
            style={
                'position': 'relative',
                'left': '10px',
                'display': 'flex'},
            children=[
                html.Div(
                    style=dict(width="1000px",
                               flex="1",
                               ),
                    children=[
                        dcc.Tabs(id='graph-type-tabs', value='layer3',
                                 children=[
                                     dcc.Tab(selected_style=main_page_graph_tab_selected, className='main-page-graph-tab', label='Layer 3', value='layer3'),
                                     dcc.Tab(selected_style=main_page_graph_tab_selected,className='main-page-graph-tab', label='OSPF', value='ospf'),
                                     dcc.Tab(selected_style=main_page_graph_tab_selected,className='main-page-graph-tab', label='BGP', value='bgp'),
                                     dcc.Tab(selected_style=main_page_graph_tab_selected,className='main-page-graph-tab', label='Trace Route', value='traceroute'),
                                 ]),
                        html.Div(id="placeholder-for-graph", ),
                        html.Div(id="main-page-traceroute", )

                    ]),
            ],
        ),


        html.Div(
            id="graph_layout_options",
            style={
                'position': 'relative',
                'left': '10px',
                'display': 'flex'},
            children=[
                html.Div(
                    dcc.Dropdown(
                        id='dropdown-update-layout',
                        value=None,
                        clearable=False,
                        style=dict(
                            flex='1',
                            verticalAlign="middle",
                            width="200px"),
                        placeholder='Choose Graph Layout',
                        options=[
                            {'label': name.capitalize(), 'value': name}
                            for name in
                            ['grid', 'random', 'circle', 'cose', 'concentric',
                             'breadthfirst']
                        ]
                    )
                ),
                html.Div(id='breadthfirst-roots',
                         children=[]),


            ]),
        html.Div(
            style={
                'position': 'relative',
                'left': '10px'},
            children=[
                html.P(id='cytoscape-mouseoverNodeData-output'),
                html.P(id='cytoscape-mouseoverEdgeData-output'),
                html.P(id='batfish-host-output'),
                html.P(id='batfish-network-output', style={"display":"none"}),
                html.P(id='num_of_traces', style={"display":"none"}),
            ]
        ),


        # Create Snapshot Modal
        html.Div(
            children=[
                dbc.Modal(
                    id="create_snapshot_modal",
                    size="lg",
                    children=[
                        dbc.ModalHeader("Create Snapshot!"),
                        dbc.ModalBody(
                            children=[
                                html.Div(
                                    style= dict(
                                        display="flex"
                                    )
                                ),
                                html.Div([],
                                         id='select-network-snapshot-modal',
                                         style=dict(
                                             flex="1"
                                         )
                                         ),
                                html.Div([],
                                         id='delete-snapshot-dropdown-div',
                                         style=dict(
                                            flex="1"
                                         )
                                         ),

                                html.Div([
                                    dcc.Upload(
                                        className='Snapshot_Upload',
                                        id='device-configs-upload-data',
                                        children=html.Div(
                                            className='inside_drag_and_drop',
                                            children= [
                                            html.P(
                                                className="upload_p",
                                                children=[
                                                    html.H3("Device Configurations"),
                                                    'Drag and Drop or ',
                                                    html.A('Select Files')
                                                ],
                                            ),
                                        ]),
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    ),
                                    dcc.Upload(
                                        className='Snapshot_Upload',
                                        id='host-configs-upload-data',
                                        children=html.Div(
                                            className='inside_drag_and_drop',
                                            children=[
                                                html.P(
                                                    className="upload_p",
                                                    children=[
                                                        html.H3(
                                                            "Host Configurations"),
                                                        'Drag and Drop or ',
                                                        html.A('Select Files')
                                                    ],
                                                ),
                                            ]),
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    ),
                                    dcc.Upload(
                                        className='Snapshot_Upload',
                                        id='iptables-configs-upload-data',
                                        children=html.Div(
                                            className='inside_drag_and_drop',
                                            children=[
                                                html.P(
                                                    className="upload_p",
                                                    children=[
                                                        html.H3(
                                                            "IP Table Configurations"),
                                                        'Drag and Drop or ',
                                                        html.A('Select Files')
                                                    ],
                                                ),
                                            ]),
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    ),
                                    dcc.Upload(
                                        className='Snapshot_Upload',
                                        id='aws-configs-upload-data',
                                        children=html.Div(
                                            className='inside_drag_and_drop',
                                            children=[
                                                html.P(
                                                    className="upload_p",
                                                    children=[
                                                        html.H3(
                                                            "AWS Configurations"),
                                                        'Drag and Drop or ',
                                                        html.A('Select Files')
                                                    ],
                                                ),
                                            ]),
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    ),
                                    dcc.Upload(
                                        className='Snapshot_Upload',
                                        id='misc-configs-upload-data',
                                        children=html.Div(
                                            className='inside_drag_and_drop',
                                            children=[
                                                html.P(
                                                    className="upload_p",
                                                    children=[
                                                        html.H3(
                                                            "Miscellaneous Configurations"),
                                                        'Drag and Drop or ',
                                                        html.A('Select Files')
                                                    ],
                                                ),
                                            ]),
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    ),


                                    html.Div(id='output-data-upload'),
                                ]),
                            ],

                        ),
                        dbc.ModalFooter(
                            children= [
                                html.A("How to format your configurations!", href="https://pybatfish.readthedocs.io/en/latest/formats.html"),
                                    dbc.FormGroup(
                                        [
                                        dbc.Input(
                                            id="create-snapshot-name",
                                            value="",
                                            placeholder="New Snapshot Name"),
                                        dbc.FormFeedback(
                                            "Please enter a name for the snapshot",
                                            valid=False,
                                        ),
                                        ],
                                            className="mr-3",
                                    ),
                            dbc.Button("Submit",
                                       id="create_snapshot_submit_button",
                                       color="dark",
                                       outline=True,

                                       style=dict(
                                           height="25px",
                                       )),
                            ],

                        ),
                    ]
                )
            ],
        ),
        # Ask a Question Modal
        html.Div(
            children=[
                dbc.Modal(
                    id="ask-a-question-modal",
                    size="xl",
                    scrollable=True,
                    children=[
                        dbc.ModalHeader("Ask a Question!"),
                        dbc.ModalBody(

                            children=[
                                html.Div([
                                    dcc.Dropdown(
                                        id="select-question-button",
                                        placeholder='Select Question',
                                        style={'margin': '5px',
                                               'width': '150px'},
                                        options=[
                                            {'label': question,
                                             'value': question}
                                            for question in batfish_questions
                                        ],
                                        value=None

                                    ),
                                ],
                                    id='ask-a-question-dropdown-modal',
                                    style=dict(
                                        position="relative",
                                        height="100px",
                                        margin_top="10px",
                                    )

                                ),
                                html.Div(id='ask-a-question-table'),
                            ],

                        ),

                    ]
                )
            ],
        ),

    ]
                               )


######################## 404 Page ########################
noPage = html.Div([
    # CC Header
    html.P(["404 Page not found"])
    ], className="no-page")
