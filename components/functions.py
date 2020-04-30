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
                     'parent': 'AS ' + as_number},
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
            'data': {'id': 'AS ' + asn, 'label': 'AS ' + asn},
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
                'width': '1000px',
                'height': '500px',
            },

            elements=elements,
            stylesheet=[
                {
                    'selector': 'edge',
                    'style': {
                        # The default curve style does not work with certain arrows
                        'source-text-rotation': 'autorotate',
                        'edge-text-rotation': 'autorotate',
                        'target-text-rotation': 'autorotate',
                        'source-label': 'data(source_label)',
                        'target-label': 'data(target_label)',
                        'source-text-offset': '50',
                        'target-text-offset': '50',
                        'text-background-opacity': 1,
                        'text-background-color': '#ffffff',
                        'text-background-shape': 'rectangle',
                        'text-border-style': 'solid',
                        'text-border-opacity': 1,
                        'text-border-width': '1px',
                        'text-border-color': 'darkgray',
                        'curve-style': 'bezier'

                    }
                },
                {
                    'selector': 'node',
                    'style': {
                        # The default curve style does not work with certain arrows
                        'label': 'data(id)',
                        'text-outline-color': '#ffffff'

                    }
                },

            ],
            layout={'name': 'breadthfirst'
                    }
        ),

    ]

    return children

def create_traceroute_graph(elements, stylesheet):
    children = [
        cyto.Cytoscape(

            id='traceroute-cytoscape',

            style={
                'width': '700px',
                'height': '500px',
            },

            elements=elements,
            stylesheet=stylesheet,
            layout={'name': 'preset'
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
    nodes = [{'data': {'id': device, 'label': device},'position': {'x': position[0] * 200, 'y': position[1] * 200}, 'classes':'Router'} for device, position in
             nodes.items()]
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
    flow = html.Details(
        [html.Summary(direction),
         html.Div(dcc.Textarea(
             value=get_flow_meta_data(result_flow),
             readOnly=True,
             style={'width': '200px', 'height': 120, 'margin-left': '5px'},
         ))])
    return flow

trace_template = """
{{ STEP }}. node: {{ NODE }}
  RECEIVED({{ RECEIVED }})
  FORWARDED(ARP IP: {{ ARP_IP }}, Output Interface: {{ OUT_INT }}, Routes: [{{ ROUTING_PROTOCOL }} (Network: {{ ROUTE }}, Next Hop IP:{{ NEXT_HOP }})])
  TRANSMITTED({{ TRANSMITTED }})
  ACCEPTED({{ ACCEPTED }})
"""
def get_traceroute_details(direction, result, bidir):


    nodes = {}
    node_list = []
    count = 0
    trace_edges = []
    children = []
    if bidir:
        if direction == "forward":
            traces = result.Forward_Traces[0]
            children.append(get_flow_details(result.Forward_Flow, "Forward Flow"))
        else:
            traces = result.Reverse_Traces[0]
            children.append(get_flow_details(result.Reverse_Flow, "Reverse Flow"))
    else:
        traces = result.Traces[0]
        children.append(get_flow_details(result.Flow, "Flow"))



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
                'text-outline-color': '#ffffff'
            }
        },
    ]

    colors = ["red", "blue", "green", "black", "yellow", "brown", "cyan",
              "grey", "lime", "purple",
              "violet", "teal", "silver", "orange", "pink"]
    while count < len(traces):
        step_list = []
        parent_list = []
        step_dict = {}
        first_edge_node_count = 0
        second_edge_node_count = 1
        if bidir:
            if direction == "forward":
                trace = result.Forward_Traces[0][count]
            else:
                trace = result.Reverse_Traces[0][count]
        else:
            trace = result.Traces[0][count]

        parser = ttp(data=str(trace), template=trace_template)
        parser.parse()
        parsed_results = parser.result(format='raw')[0][0]

        # for node in parsed_results:
        #     nodes.append(str(node["NODE"]))

        x = 0
        y = 0
        for node in parsed_results:
            node = node["NODE"]

            if node not in nodes:

                if x in [value for values in nodes.values() for value in
                         values]:
                    nodes[node] = [x, y + 1]
                else:
                    node_list.append(node)
                    nodes[node] = [x, y]
            x += 1

        max_value = max(
            [value for values in nodes.values() for value in values])

        while second_edge_node_count < len(trace):
            pair = []
            trace_number = 'Trace ' + str(count)
            first_edge_node = parsed_results[first_edge_node_count]["NODE"]
            second_edge_node = parsed_results[second_edge_node_count]["NODE"]
            pair.append('trace_' + str(count))
            pair.append(first_edge_node)
            pair.append(second_edge_node)
            trace_edges.append(tuple(pair))
            first_edge_node_count += 1
            second_edge_node_count += 1
        top_sum = html.Summary(trace_number, style=dict(color=colors[0]))
        for data in parsed_results:
            contents = ""
            for item in data.items():
                contents = contents + item[0] + ': ' + item[1] + '\n'
            step_dict['Step ' + str(data['STEP'])] = contents
            steps = html.Details([html.Summary('Step ' + str(data['STEP']),
                                               className="trace_steps"),
                                  html.Div(dcc.Textarea(
                                      value=contents,
                                      readOnly=True,
                                      style={'width': '200px', 'height': 120,
                                             'margin-left': '5px'},
                                  ))])
            step_list.append(steps)

        parent_list.append(top_sum)
        for data in step_list:
            parent_list.append(data)
        top_tree = html.Details(parent_list)
        children.append(top_tree)
        trace_style = [{
            'selector': 'edge.' + 'trace_' + str(count),
            'style': {
                'target-arrow-color': colors[0],
                'target-arrow-shape': 'triangle',
                'line-color': colors[0]
            }
        }]
        count += 1
        del colors[0]
        stylesheet = stylesheet + trace_style

    return [create_traceroute_graph(get_elements(nodes, trace_edges, max_value, node_list),
                                   stylesheet), children]

SNAPSHOT_DEVICE_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/configs"
SNAPSHOT_HOST_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/configs"
SNAPSHOT_IPTABLES_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/configs"
SNAPSHOT_AWS_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/configs"
SNAPSHOT_MISC_CONFIG_UPLOAD_DIRECTORY = "assets/snapshot_holder/configs"

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
        for subdir, dirs, files in os.walk("assets\snapshot_holder"):
            for file in files:
                filePath = os.path.join(subdir, file)
                os.unlink(filePath)

    except Exception as error:
        print(error)



################## Need to figure out dynamic callbacks. Pattern matching not working#########
def collapsible_traces(trace, step_dict, count):
    card = []
    for step, contents in step_dict.items():
        card_body = [dbc.CardHeader(
                            html.H2(
                                dbc.Button(
                                    step,
                                    color="link",
                                    id=step,
                                ),
                            ),
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                dcc.Textarea(
                                        value=contents,
                                        readOnly=True,
                                        style={'width': '100%', 'height': 120},
                                        ),),
                            id=step + "_contents",
                        )]
        card = card + card_body

    return dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H2(
                                html.Button(
                                    trace,
                                    id={
                                        'type': 'Trace_Button',
                                        'index': count
                                    },
                                )
                            )
                        ),
                        dbc.Collapse(

                            dbc.Card(card),
                            id={
                               'type': 'Trace',
                               'index': count
                           },
                        ),
                    ]
                )



