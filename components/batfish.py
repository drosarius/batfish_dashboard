import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

pd.options.display.float_format = '{:,}'.format



class Batfish():

    def __init__(self, batfish_host):
        self.batfish_host = batfish_host
        bf_session.host = batfish_host
        load_questions()

    def delete_network(self, network):
        bf_delete_network(network)

    def delete_snapshot(self, snapshot):
        bf_delete_snapshot(snapshot)

    def set_snapshot(self, snapshot):
        bf_set_snapshot(snapshot)

    def set_network(self, network):
        bf_set_network(network)

    def get_existing_networks(self):
        return bf_list_networks()

    def get_existing_snapshots(self):
        try:
            snapshotlist = bf_list_snapshots()
        except ValueError:
            snapshotlist = ["None"]
        return snapshotlist

    def init_snapshot(self,snapshot_name, overwrite=True):
        snapshot_dir = "assets/snapshot_holder/"
        bf_init_snapshot(snapshot_dir, name=str(snapshot_name),
                         overwrite=overwrite)

    def get_info(self, command):
        execute = 'bfq.' + command + '().answer().frame()'
        result = eval(execute)
        return result

    def get_layer3_edges(self):
        result = bfq.layer3Edges().answer().frame()
        return result

    def get_ospf_edges(self):
        result = bfq.ospfEdges().answer().frame()
        return result

    def get_bgp_edges(self):
        result = bfq.bgpEdges().answer().frame()
        return result

    def traceroute(self, src, dst, src_ip=None, dst_ip=None, bidir=False):
        if bidir:
            result = bfq.bidirectionalTraceroute(startLocation=src, headers=HeaderConstraints(dstIps=dst)).answer().frame()
        else:
            result = bfq.traceroute(startLocation=src, headers=HeaderConstraints(dstIps=dst)).answer().frame()
        return result


