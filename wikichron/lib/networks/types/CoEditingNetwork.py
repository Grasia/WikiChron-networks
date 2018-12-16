"""

 Author: Youssef El Faqir El Rhazoui
 Date: 13/12/2018
 Distributed under the terms of the GPLv3 license.

"""

from datetime import datetime
from .NetworkType import BaseNetwork

class CoEditingNetwork(BaseNetwork):
    """
    This network is based on the editors cooperation, this means, the nodes
    are user from a wiki, and a edge will link two nodes if they edit the same
    page. As well, this network has the following args:

        - Node:
            * contributor_id: id user on the wiki
            * label: the user name with id contributor_id on the wiki
            * num_edits: the number of edit in the whole wiki
            * first_edit: this is a datetime object with the first edition
            * last_edit: this is a datetime object with the last edition

        - Edge:
            * source: contributor_id
            * target: contributor_id
            * weight: the number of cooperation in different pages on the wiki,
                      differents editions on the same page computes only once.

    """

    def __init__(self):
        super().__init__(is_directed=False)
        self.oldest_user = 0
        self.newest_user = 0


    def generate_from_pandas(self, data):
        user_per_page = {}
        mapper_v = {}
        mapper_e = {}
        count = 0

        for index, r in data.iterrows():
            t = int(r['timestamp'].to_pydatetime().strftime('%s'))

            if r['contributor_name'] == 'Anonymous':
                continue

            if not self.oldest_user:
                self.oldest_user = t

            self.newest_user = t

            # Nodes
            if not r['contributor_id'] in mapper_v:
                self.add_vertex(count)
                mapper_v[r['contributor_id']] = count
                self.vs[count]['contributor_id'] = r['contributor_id']
                self.vs[count]['label'] = r['contributor_name']
                self.vs[count]['num_edits'] = 0
                self.vs[count]['first_edit'] = t
                count += 1

            self.vs[mapper_v[r['contributor_id']]]['num_edits'] += 1
            self.vs[mapper_v[r['contributor_id']]]['last_edit'] = r['timestamp']

            # A page gets serveral contributors
            if not r['page_id'] in user_per_page:
                user_per_page[r['page_id']] = \
                                {r['contributor_id']: {r['timestamp']}}
            else:
                if r['contributor_id'] in user_per_page[r['page_id']]:
                    user_per_page[r['page_id']][r['contributor_id']]\
                                .add(r['timestamp'])
                else:
                    user_per_page[r['page_id']][r['contributor_id']] = \
                            {r['timestamp']}

        count = 0
        # Edges
        for k, p in user_per_page.items():
            aux = {}
            for k_i, v_i in p.items():
                for k_j, v_j in aux.items():
                    if f'{k_i}{k_j}' in mapper_e:
                        self.es[mapper_e[f'{k_i}{k_j}']]['weight'] += 1
                        self.es[mapper_e[f'{k_i}{k_j}']]['s_pg'][k] = v_i
                        self.es[mapper_e[f'{k_i}{k_j}']]['t_pg'][k] = v_j
                        continue
                    if f'{k_j}{k_i}' in mapper_e:
                        self.es[mapper_e[f'{k_j}{k_i}']]['weight'] += 1
                        self.es[mapper_e[f'{k_j}{k_i}']]['s_pg'][k] = v_j
                        self.es[mapper_e[f'{k_j}{k_i}']]['t_pg'][k] = v_i
                        continue

                    self.add_edge(mapper_v[k_i], mapper_v[k_j])
                    mapper_e[f'{k_i}{k_j}'] = count
                    count += 1
                    self.es[mapper_e[f'{k_i}{k_j}']]['weight'] = 1
                    self.es[mapper_e[f'{k_i}{k_j}']]['id'] = f'{k_i}{k_j}'
                    self.es[mapper_e[f'{k_i}{k_j}']]['source'] = k_i
                    self.es[mapper_e[f'{k_i}{k_j}']]['target'] = k_j
                    self.es[mapper_e[f'{k_i}{k_j}']]['s_pg'] = {k: v_i}
                    self.es[mapper_e[f'{k_i}{k_j}']]['t_pg'] = {k: v_j}

                aux[k_i] = v_i
        return


    def to_cytoscape_dict(self):
        di_net = {}
        network = []
        min_v = float('Inf')
        max_v = -1
        for node in self.vs:

            if min_v > node['num_edits']:
                min_v = node['num_edits']
            if max_v < node['num_edits']:
                max_v = node['num_edits']

            network.append({
                'data': {
                    'id': node['contributor_id'],
                    'label': node['label'],
                    'num_edits': node['num_edits'],
                    'first_edit': node['first_edit'],
                    'last_edit': node['last_edit']
                }
            })

        di_net['user_max_edits'] = max_v
        di_net['user_min_edits'] = min_v
        min_v = float('Inf')
        max_v = -1
        for edge in self.es:

            if min_v > edge['weight']:
                min_v = edge['weight']
            if max_v < edge['weight']:
                max_v = edge['weight']

            network.append({
                'data': {
                    'id': edge['id'],
                    'source': edge['source'],
                    'target': edge['target'],
                    'weight': edge['weight']
                }
            })

        di_net['oldest_user'] = self.oldest_user
        di_net['newest_user'] = self.newest_user
        di_net['edge_max_weight'] = max_v
        di_net['edge_min_weight'] = min_v
        di_net['network'] = network

        return di_net
