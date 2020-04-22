import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


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
                     "detectLoops"]


main_page_layout = html.Div(id='main-page', children=[
        html.Div(
            style={'margin': '0'},
            children=[
                html.Header(
                    style={
                        'background-color': 'black',
                        'height': '40px',
                    },
                    children=[
                        html.H1('Batfish Dashboard',
                                style={
                                    'font-weight': 'bold',
                                    'color': 'white',
                                    'position': 'absolute',
                                    'left': '12px',
                                    'margin-top': '5px',
                                    'font-family': 'Arial, Helvetica, sans-serif'})
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
                        style={'margin': '5px'}
                    ),
                ],
                    style=dict(
                        display='table-cell',
                        verticalAlign="middle",
                    )
                ),
                html.Div([
                    html.Button(
                        "Create/Delete Network",
                        id="create-network-button",
                        style={'margin': '5px'}
                    ),
                ],
                    style=dict(
                        display='table-cell',
                        verticalAlign="middle",
                    )
                ),
                html.Div([
                    html.Button(
                        "Create/Delete Snapshot",
                        id="create-snapshot-button",
                        style={'margin': '5px'}
                    ),
                ],
                    style=dict(
                        display='table-cell',
                        verticalAlign="middle",
                    )
                ),
                html.Div([],
                         id='select-network-div',
                         style=dict(
                             display='table-cell',
                             verticalAlign="middle",
                         )
                         ),
                html.Div([],
                         id='select-snapshot-div',
                         style=dict(
                             display='table-cell',
                             verticalAlign="middle",
                         )
                         ),
                html.Div([
                    html.Button(
                        "Ask a Question",
                        id="ask-question-button",
                        style={'margin': '5px'}
                    ),
                ],
                    style=dict(
                        display='table-cell',
                        verticalAlign="middle",
                    )
                ),
                html.Div([
                    html.Button(
                        "Trace Route",
                        id="traceroute-button",
                        style={'margin': '5px'}
                    ),
                ],
                    style=dict(
                        display='table-cell',
                        verticalAlign="middle",
                    )
                ),

                html.Div(
                    style=dict(
                        width="1000px"
                    ),

                    children=[
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(

                                    children=[
                                        dbc.Form(
                                            [
                                                dbc.FormGroup(
                                                    [
                                                        dbc.Input(
                                                            id="batfish_host_input",
                                                            value="",
                                                            placeholder="Enter host"),
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
                            ),
                            id="batfishhost-collapse",
                        ),

                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    children=[]
                                )
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
                               flex="1"),
                    children=[
                        dcc.Tabs(id='graph-type-tabs', value='layer3',
                                 style=dict(width="1000px",
                                            ),
                                 children=[
                                     dcc.Tab(label='Layer 3', value='layer3'),
                                     dcc.Tab(label='OSPF', value='ospf'),
                                     dcc.Tab(label='BGP', value='bgp'),
                                 ]),
                        html.Div(id="placeholder-for-graph", )

                    ]),
            ],
        ),
        ##################### Main Graph #############################


        html.Div(
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
                html.P(id='batfish-network-output', style={"display":"none"})
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
                                        id='config-upload-data',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select Files')
                                        ]),
                                        style={
                                            'width': '760px',
                                            'height': '250px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px'
                                        },
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    ),
                                    html.Div(id='output-data-upload'),
                                ]),
                            ],

                        ),
                        dbc.ModalFooter(
                            children= [
                                    dbc.FormGroup(
                                        [
                                        dbc.Input(
                                            id="create-snapshot-name",
                                            value="",
                                            placeholder="New Snapshot Name"),
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
        # Traceroute Modal
        html.Div(
            children=[
                dbc.Modal(
                    id="traceroute-modal",
                    size="xl",
                    scrollable=True,
                    children=[
                        dbc.ModalHeader("Trace Route"),
                        dbc.ModalBody(

                            children=[
                                html.Div(
                                    id="options",
                                    style= dict(position="relative"),
                                    children=[
                                        html.Div([
                                            html.Label(
                                                style={'margin': '5px',
                                                       'width': '250px'},
                                                children = [
                                                "Select Source",
                                                dcc.Dropdown(
                                                    id="select-enter-location-button",
                                                    placeholder='Select Source',
                                                    options=[],
                                                    value=None
                                                ),
                                            ]),

                                        ],
                                            id='traceroute-source-dropdown-modal',
                                            style=dict(
                                                margin_top="10px",
                                            )
                                        ),
                                        html.Div([
                                            html.Label(
                                                style={'margin': '5px',
                                                       'width': '250px'},
                                                children = [
                                                    "Select Destination",
                                                    dcc.Dropdown(
                                                        id="select-destination-location-button",
                                                        placeholder='Select Destination',
                                                        options=[],
                                                        value=None

                                                    ),

                                            ]),

                                        ],
                                            id='traceroute-destination-dropdown-modal',
                                            style=dict(
                                                margin_top="10px",
                                            )

                                        ),
                                    ],

                                ),
                                html.Div(
                                    style=dict(
                                        display="flex"
                                    ),
                                    children=[
                                        html.Div(id='traceroute-graph',
                                                 style=dict(
                                                     flex="1",
                                                 ),
                                                 ),
                                        html.Div(id="trace-collapse",
                                                 style=dict(
                                                     flex="1"
                                                 ),
                                                 children=[

                                                 ],


                                                 ),
                                    ],
                                ),


                            ],

                        ),

                    ]
                )
            ],
        )

    ]
                               )


######################## 404 Page ########################
noPage = html.Div([
    # CC Header
    html.P(["404 Page not found"])
    ], className="no-page")
