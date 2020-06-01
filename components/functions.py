import base64
import os
import re
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from ttp import ttp


def get_bgp_nodes(batfish_df):
    local_node = set(tuple(zip(batfish_df['Node'], batfish_df['AS_Number'])))
    remote_node = set(
        tuple(zip(batfish_df['Remote_Node'], batfish_df['Remote_AS_Number'])))
    all_nodes = list(local_node) + list(remote_node)
    nodes = [
        {
            'data': {'id': device, 'label': device,
                     'parent': 'AS ' + as_number}, 'classes': 'bgp_node',
        }
        for device, as_number in list(set(all_nodes))
    ]
    return nodes


def get_bgp_edges(batfish_df):
    test_edges = set(tuple(zip(batfish_df['Node'], batfish_df['Remote_Node'])))
    new_edges = []
    for edge in test_edges:
        if edge[::-1] not in new_edges:
            new_edges.append(edge)

    new_edges = list(set(tuple(sub) for sub in new_edges))
    edges = [
        {'data': {'source': source, 'target': target}}
        for source, target in new_edges]
    return edges


def getnodes(batfish_df):
    node_x = [re.sub('\[.*', '', str(x)) for x in batfish_df['Interface']]
    nodes = [{'data': {'id': device, 'label': device}} for device in
             set(node_x)]
    return nodes


def getparents(batfish_df):
    as_numbers = list(batfish_df['AS_Number']) + list(
        batfish_df['Remote_AS_Number'])
    parent_nodes = [
        {
            'data': {'id': 'AS ' + asn, 'label': 'AS ' + asn}, 'classes': 'parent',
        }
        for asn in list(set(as_numbers))
    ]
    return parent_nodes


def getedges(batfish_df):
    test_edges = set(
        tuple(zip(batfish_df['Interface'], batfish_df['Remote_Interface'])))
    new_edges = []
    new_new_edges = []
    for edge in test_edges:
        if edge not in new_edges:
            if edge[::-1] not in new_edges:
                new_edges.append(edge)
                test = []
                for x in edge:
                    x = re.sub('\]', '', str(x))
                    x_test = x.split('[')
                    x_test[1] = re.sub("\..*", ".subints", x_test[1])
                    x_test[1] = re.sub("^Ethernet", "eth", x_test[1])
                    x_test[1] = re.sub("^TenGigabitEthernet", "Ten", x_test[1])
                    x_test[1] = re.sub("^GigabitEthernet", "Ge", x_test[1])
                    x_test[1] = re.sub("^port-channel", "po", x_test[1])
                    x_test[1] = re.sub("^Port-Channel", "po", x_test[1])
                    x_test[1] = re.sub(r"([^-]+-\S{4})(.*)",r"\1", x_test[1])
                    test += x_test
                new_new_edges.append(test)
    new_new_edges = list(set(tuple(sub) for sub in new_new_edges))
    edges = [
        {'data': {'source': source, 'target': target,
                  'source_label': source_int, 'target_label': target_int}}
        for source, source_int, target, target_int in new_new_edges]

    return edges


def create_graph(elements):
    children = [
        cyto.Cytoscape(

            id='cytoscape',

            style={
                'width': '1500px',
                'height': '700px',
            },

            elements=elements,
            stylesheet=[
                {
                    'selector': 'edge',
                    'style': {
                        'source-text-rotation': 'autorotate',
                        'edge-text-rotation': 'autorotate',
                        'target-text-rotation': 'autorotate',
                        'source-label': 'data(source_label)',
                        'target-label': 'data(target_label)',
                        'source-text-offset': '50',
                        'target-text-offset': '50',
                        'text-background-opacity': 1,
                        'text-background-color': '#ffffff',
                        'text-background-shape': 'roundrectangle',
                        'text-border-style': 'solid',
                        'text-border-opacity': 1,
                        'text-border-width': '1px',
                        'text-border-color': 'darkgray',
                        'text-background-padding': '3px',
                        'curve-style': 'bezier'


                    }
                },
                {
                    'selector': 'node',
                    'style': {
                        'label': 'data(id)',
                        'text-outline-color': '#ffffff',
                        'background-image': 'assets/img/Router2.png',
                        'background-fit': 'cover',
                        'width': 100,
                        'height': 100,
                        'text-background-opacity': 1,
                        'text-background-color': '#ffffff',
                        'text-background-shape': 'roundrectangle',
                        'text-border-style': 'solid',
                        'text-border-opacity': 1,
                        'text-border-width': '1px',
                        'text-border-color': 'darkgray',
                        'font-weight': 'bold',
                        'text-background-padding': '5px',



                    }
                },
                {
                    'selector': '.parent',
                    'style': {
                        'background-image': 'none',
                        'background-color': 'ghostwhite',
                        'border-color':'#555555',
                    }
                },

            ],
            layout={'name': 'breadthfirst',
                    'padding': 60,
                    'spacingFactor': 2.5,
                    }
        ),

    ]

    return children


def create_traceroute_graph(elements, stylesheet):
    children = [
        cyto.Cytoscape(

            id='traceroute-cytoscape',

            style={
                'width': '1720px',
                'height': '500px',
            },

            elements=elements,
            stylesheet=stylesheet,
            layout={'name': 'preset',
                    'padding': 60,
                    }
        ),
    ]
    return children


def get_elements(nodes, trace_edges, max_value, node_list):
    start = node_list[0]
    finish = node_list[-1]

    edges = [
        {'data': {'source': source, 'target': target}, 'classes': trace}
        for trace, source, target, in trace_edges]
    nodes = [{'data': {'id': device, 'label': device},
              'position': {'x': position[0] * 200, 'y': position[1] * 200},
              'classes':'Router'}
             for device, position in nodes.items()]
    start_node = [
        {'data': {'id': start, 'label': start},
         'position': {'x': 0, 'y': 0}}]
    finish_node = [{'data': {'id': finish, 'label': finish},
         'position': {'x': (max_value + 1) * 200, 'y': 0}}]
    all_nodes = start_node + finish_node + nodes

    return all_nodes + edges


flow_template = """
start={{ START }} [{{ SRC }}->{{ DST }} {{ PROTOCOL }} length={{ LENGTH }}]
"""


def get_flow_meta_data(flow_data):

    parser = ttp(data=str(flow_data[0]), template=flow_template)
    parser.parse()
    flow_parsed_results = parser.result(format='raw')[0][0]
    flow_meta_data = ""
    for item in flow_parsed_results.items():
        flow_meta_data = flow_meta_data + item[0] + ': ' + item[1] + '\n'
    return flow_meta_data


def get_flow_details(result_flow, direction):
    flow = html.Div(className="main_page_traceroute_flow_details",
                    children=[
                        html.Details(
                            [html.Summary(direction),
                             html.Div(dcc.Textarea(
                                 value=get_flow_meta_data(result_flow),
                                 readOnly=True,
                                 style={'width': '200px', 'height': 120,
                                        'margin-left': '5px'},
                             ))])
                    ])
    return flow

def get_traceroute_details(direction, result, bidir, chaos=False):
    """

    :param direction:
        The direction of the trace:
            String: "forward" or "reverse"
    :param result:
        traceroute pandas dataframe
    :param bidir:
        If the traceroute is bidirectional:
            boolean: true or false
    :return:
        Graph of the trace route and trace route details
    """



    if bidir:
        if direction == "forward":
            traces = result.Forward_Traces[0]
            # children.append(get_flow_details(result.Forward_Flow, "Forward Flow"))
        else:
            traces = result.Reverse_Traces[0]
            if traces == []:
                return [None, None]
            # children.append(get_flow_details(result.Reverse_Flow, "Reverse Flow"))
    else:
        if chaos:
            traces = result.Traces[0]
            # children.append(get_flow_details(result.Flow, "Chaos Flow"))

        else:
            traces = result.Traces[0]
            # children.append(get_flow_details(result.Flow, "Flow"))

    stylesheet = [
        {
            'selector': 'edge',
            'style': {
                'curve-style': 'bezier'
            }
        },
        {
            'selector': 'node',
            'style': {
                'label': 'data(id)',
                'text-outline-color': '#ffffff',
                'background-image': 'assets/img/Router2.png',
                'background-fit': 'cover',
                'width': 50,
                'height': 50,
                'text-background-opacity': 1,
                'text-background-color': '#ffffff',
                'text-background-shape': 'roundrectangle',
                'text-border-style': 'solid',
                'text-border-opacity': 1,
                'text-border-width': '1px',
                'text-border-color': 'darkgray',
                'font-weight': 'bold',
                'text-background-padding': '5px',

            }
        },
    ]

    colors = ["red", "blue", "green", "black", "brown", "cyan",
              "grey", "lime", "purple",
              "violet", "teal", "silver", "orange", "pink", "yellow"]
    trace_count = 0
    trace_tabs_children = []
    node_list = []
    nodes = {}
    trace_edges = []
    for x in traces:
        trace = traces[trace_count]
        hops = trace.dict()['hops']
        count = 0
        step_row_children = []
        x = 0
        y = 0
        first_edge_node_count = 0
        second_edge_node_count = 1
        for hop in hops:
            outside_toast_children = []
            node = hop['node']
            if node not in nodes:

                if node not in nodes:
                    all_x_values = [value[0] for value in nodes.values()]
                    if x in all_x_values:
                        nodes[node] = [x, all_x_values.count(x)]
                    else:
                        node_list.append(node)
                        nodes[node] = [x, y]
            x += 1

            pair = []
            if second_edge_node_count < len(trace):
                first_edge_node = hops[first_edge_node_count]["node"]
                second_edge_node = hops[second_edge_node_count]["node"]

                pair.append('trace_' + str(trace_count))
                pair.append(first_edge_node)
                pair.append(second_edge_node)
                trace_edges.append(tuple(pair))
            first_edge_node_count += 1
            second_edge_node_count += 1

            hop_steps = hop['steps']

            outside_toast_id = "trace_{trace_count}_step_{step_count}".format(
                trace_count=trace_count, step_count=count)
            outside_toast_header = "Step: {step_count} Node: {node}".format(
                step_count=count, node=node)

            for step_detail in hop_steps:
                step_detail_dict = step_detail['detail']
                step_action = step_detail['action']
                inside_toast_content = ""
                inside_toast_header = step_action
                inside_toast_content_html = None
                inside_toast_id = "trace_{trace_count}_step_{step_count}_{step_action}".format(
                    trace_count=trace_count, step_count=count,
                    step_action=step_action)

                for outside_key, outside_value in step_detail_dict.items():
                    inside_toast_children = []
                    inside_value_dict = ""

                    if outside_key == "routes":
                        for inside_key, inside_value in outside_value[0].items():
                            inside_value_dict += "{key} : {value}\n".format(
                                key=inside_key, value=inside_value)
                        inside_toast_content_html = html.Details(
                            [html.Summary(outside_key),
                             html.Div(html.Pre(inside_value_dict))])

                    elif outside_key == "flow":
                        for inside_key, inside_value in outside_value.items():
                            inside_value_dict += "{key} : {value}\n".format(
                                key=inside_key, value=inside_value)
                        inside_toast_content_html = html.Details(
                            [html.Summary(outside_key),
                             html.Div(html.Pre(inside_value_dict))])
                    else:
                        inside_toast_content += "{key} : {value}\n".format(
                            key=outside_key, value=outside_value)

                inside_toast_children.append(html.Pre(inside_toast_content))
                inside_toast_children.append(inside_toast_content_html)
                inside_toast = dbc.Toast(
                    inside_toast_children,
                    id=inside_toast_id,
                    header=inside_toast_header,
                    style={"min-width": "200px",
                           "font-size": "12px"})

                outside_toast_children.append(inside_toast)
            count += 1

            step_toast = dbc.Toast(
                outside_toast_children,
                is_open=True,
                id={
                    'type': 'Step_Toast',
                    'index': outside_toast_id
                },
                header=outside_toast_header,
                style={"min-width": "300px",
                       "font-size": "15px"},

            )

            step_row_children.append(step_toast)
        max_value = max(all_x_values)
        step_row = html.Div(

            dbc.Row(children=step_row_children,

                    style={"display": "flex",
                           "min-width": "100%",
                           "min-height": "300px",
                           "overflowX": "auto",
                           "flex-wrap": "nowrap",
                           'margin-bottom': '20px'}),
            style={
                'whiteSpace': 'nowrap',
                'width': '1690px',
                'height': 'auto',
                'margin-left':"15px"


            },
        )

        tab_style = {
            'borderBottom': '1px solid #d6d6d6',
            'padding': '6px',
            'fontWeight': 'bold',
            "color": colors[0],
            "font-size":"18px"

        }

        tab_selected_style = {
            'borderTop': '1px solid #d6d6d6',
            'borderBottom': '1px solid #d6d6d6',
            'backgroundColor': colors[0],
            'color': 'white',
            'padding': '6px',
            "font-size":"18px"
        }

        trace_tab = dcc.Tab(className='trace-tab',
                            label="Trace " + str(trace_count),
                            children=step_row,
                            style=tab_style,
                            selected_style=tab_selected_style)

        trace_tabs_children.append(trace_tab)


        trace_style = [{
            'selector': 'edge.' + 'trace_' + str(trace_count),
            'style': {
                'target-arrow-color': colors[0],
                'target-arrow-shape': 'triangle',
                'line-color': colors[0]
            }
        }]
        trace_count += 1
        del colors[0]
        stylesheet = stylesheet + trace_style

    return [create_traceroute_graph(
        get_elements(nodes, trace_edges, max_value, node_list), stylesheet),
        trace_tabs_children]

SNAPSHOT_DEVICE_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/configs"
SNAPSHOT_HOST_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/hosts"
SNAPSHOT_IPTABLES_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/iptables"
SNAPSHOT_AWS_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/aws_configs"
SNAPSHOT_MISC_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/batfish"


def save_file(config_type, name, content):
    data = content.encode("utf8").split(b";base64,")[1]
    if config_type == 'device_config':
        directory = SNAPSHOT_DEVICE_CONFIG_UPLOAD_DIRECTORY
    elif config_type == 'host_config':
        directory = SNAPSHOT_HOST_CONFIG_UPLOAD_DIRECTORY
    elif config_type == 'iptable_config':
        directory = SNAPSHOT_IPTABLES_CONFIG_UPLOAD_DIRECTORY
    elif config_type == 'aws_config':
        directory = SNAPSHOT_AWS_CONFIG_UPLOAD_DIRECTORY
    elif config_type == 'misc_config':
        directory = SNAPSHOT_MISC_CONFIG_UPLOAD_DIRECTORY

    with open(os.path.join(directory, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def delete_old_files():
    try:
        for subdir, dirs, files in os.walk(r"assets\snapshot_holder"):
            for file in files:
                filePath = os.path.join(subdir, file)
                os.unlink(filePath)

    except Exception as error:
        print(error)






