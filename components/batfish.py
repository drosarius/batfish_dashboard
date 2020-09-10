import pandas as pd
from pybatfish.client.commands import bf_session
from pybatfish.client.commands import bf_delete_network
from pybatfish.client.commands import bf_delete_snapshot
from pybatfish.client.commands import bf_set_snapshot
from pybatfish.client.commands import bf_set_network
from pybatfish.client.commands import bf_list_networks
from pybatfish.client.commands import bf_list_snapshots
from pybatfish.client.commands import bf_init_snapshot
from pybatfish.client.commands import bf_fork_snapshot
from pybatfish.client.extended import bf_get_snapshot_input_object_text
from pybatfish.question import bfq
from pybatfish.question import load_questions, list_questions
from pybatfish.datamodel import HeaderConstraints, Interface

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

    @property
    def get_existing_networks(self):
        return bf_list_networks()

    @property
    def get_layer3_edges(self):
        result = bfq.layer3Edges().answer().frame()
        return result

    @property
    def get_interfaces(self):
        result = bfq.ipOwners().answer().frame()
        return result

    @property
    def get_ospf_edges(self):
        result = bfq.ospfEdges().answer().frame()
        return result

    @property
    def get_bgp_edges(self):
        result = bfq.bgpEdges().answer().frame()
        return result

    def get_existing_snapshots(self):
        try:
            snapshotlist = bf_list_snapshots()
        except ValueError:
            snapshotlist = ["None"]
        return snapshotlist

    def init_snapshot(self, snapshot_name, overwrite=True):
        snapshot_dir = "assets/snapshot_holder/"
        bf_init_snapshot(snapshot_dir, name=str(snapshot_name),
                         overwrite=overwrite)

    def get_info(self, command):
        execute = 'bfq.' + command + '().answer().frame()'
        result = eval(execute)
        return result



    def traceroute(self, src, dstIps, bidir,snapshot,
                   srcPorts=None,
                   dstPorts =None,
                   applications=None,
                   ipProtocols=None,
                   ):
        headers = HeaderConstraints(dstIps =dstIps,
                                    srcPorts=srcPorts,
                                    dstPorts =dstPorts,
                                    applications=applications,
                                    ipProtocols=ipProtocols)
        if bidir:
            result = bfq.bidirectionalTraceroute(startLocation=src,
                                                 headers=headers)\
                .answer(snapshot=snapshot)\
                .frame()
        else:

            result = bfq.traceroute(startLocation=src,
                                    headers=headers)\
                .answer(snapshot=snapshot)\
                .frame()
        return result

    def get_configuration(self, file_name, snapshot):
        return bf_get_snapshot_input_object_text(file_name, snapshot=snapshot)

    def network_failure(self,
                        base_snapshot,
                        reference_snapshot,
                        deactivate_node,
                        deactivated_int,
                        overwrite=True):
        if not deactivated_int:
            bf_fork_snapshot(base_snapshot,
                             reference_snapshot,
                             deactivate_nodes=deactivate_node,
                             overwrite=overwrite)
        else:
            bf_fork_snapshot(base_snapshot,
                             reference_snapshot,
                             deactivate_interfaces=[
                                 Interface(deactivate_node[0],
                                           deactivated_int[0])
                             ],
                             overwrite=overwrite)



    def compare_acls(self,orginal_acl, refactored_acl, original_paltform, refactored_platform):
        original_snapshot = bf_session.init_snapshot_from_text(orginal_acl,
                                           platform=original_paltform,
                                           snapshot_name="original",
                                           overwrite=True)
        refactored_snapshot = bf_session.init_snapshot_from_text(refactored_acl,
                                           platform=refactored_platform,
                                           snapshot_name="refactored",
                                           overwrite=True)
        result = bfq.compareFilters().answer(snapshot=refactored_snapshot, reference_snapshot=original_snapshot).frame()
        result.rename(
            columns={'Line_Content': 'Refactored ACL Line', 'Reference_Line_Content': 'Original ACL Line'},
            inplace=True)
        return result


    def get_question_description(self, question):
        execute = 'bfq.' + question + '().get_long_description()'
        result = eval(execute)
        return result

    @property
    def list_questions(self):
        return list_questions()