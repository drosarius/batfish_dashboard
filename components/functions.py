import base64
import os
import re
import dash_cytoscape as cyto





def get_bgp_nodes(batfish_df):
    local_node = set(tuple(zip(batfish_df['Node'], batfish_df['AS_Number'])))
    remote_node = set(
        tuple(zip(batfish_df['Remote_Node'], batfish_df['Remote_AS_Number'])))
    all_nodes = list(local_node) + list(remote_node)
    nodes = [
        {
            'data': {'id': device, 'label': device,
                     'parent': as_number},
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
            'data': {'id': device, 'label': device},
        }
        for device in list(set(as_numbers))
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
                    x_test[1] = re.sub("^port-channel", "po", x_test[1])
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
                # 'border': '1px solid black',
                'border-radius': '5px',
                'resize': 'both',
                'overflow': 'auto',
                'background-color': '#e0f8ff',
                'border-style': 'inset'
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
                # "margin-top": "30px",
                "margin-left": "5px",
                'width': '700px',
                'height': '500px',
                'border-radius': '5px',
                'resize': 'both',
                'overflow': 'auto',
                'background-color': '#e0f8ff',
                'border-style': 'inset'
            },

            elements=elements,
            stylesheet=stylesheet,
            layout={'name': 'breadthfirst'
                    }
        ),
    ]
    return children

SNAPSHOT_UPLOAD_DIRECTORY = "assets/snapshot_holder/configs"

def save_file(name, content):
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(SNAPSHOT_UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def delete_old_files():
    try:
        for subdir, dirs, files in os.walk(SNAPSHOT_UPLOAD_DIRECTORY):
            for file in files:
                filePath = os.path.join(subdir, file)
                os.unlink(filePath)

    except Exception as error:
        print(error)
