"""

 Author: Youssef El Faqir El Rhazoui
 Date: 13/Dec/2018
 Distributed under the terms of the GPLv3 license.

"""

import pandas as pd
import numpy
import math
from datetime import datetime

from .BaseNetwork import BaseNetwork

class CoEditingNetwork(BaseNetwork):
    """
    This network is based on the editors cooperation, this means, the nodes
    are user from a wiki, and a edge will link two nodes if they edit the same
    page. As well, this network has the following args:

        - Node:
            * id: user id on the wiki
            * label: the user name with id contributor_id on the wiki
            * num_edits: the number of edit in the whole wiki
            * first_edit: this is a datetime object with the first edition
            * last_edit: this is a datetime object with the last edition
            * birth: int(first_edit)

        - Edge:
            * source: contributor_id
            * target: contributor_id
            * weight: the number of cooperation in different pages on the wiki,
                      differents editions on the same page computes only once.

    """

    #aprox 1 month = 30 days
    TIME_DIV = 60 * 60 * 24 * 30
    TIME_BOUND = 24 * 15
    NAME = 'Co-Editing'
    CODE = 'co_editing_network'

    #only metrics for the ranking
    AVAILABLE_METRICS = {
        'Article Edits': 'num_edits',
        'Betweenness': 'betweenness',
        'Page Rank': 'page_rank'
    }

    SECONDARY_METRICS = {
        'Longevity': {
            'key': 'birth',
            'max': 'max_birth',
            'min': 'min_birth'
        },
        'Talk Edits': {
            'key': 'talk_edits',
            'max': 'max_talk_edits',
            'min': 'min_talk_edits'
        }
    }

    USER_INFO = {
        'User ID': 'id',
        'User Name': 'label',
        'Cluster': 'cluster',
        'First Edit': 'first_edit',
        'Last Edit': 'last_edit',
        'Talk Pages Edit': 'talk_edits',
    }


    def __init__(self, is_directed = False, graph = {}):
        super().__init__(is_directed = is_directed, graph = graph)


    def generate_from_pandas(self, df):
        user_per_page = {}
        mapper_v = {}
        mapper_e = {}
        count = 0

        dff = self.remove_non_article_data(df)

        for _, r in dff.iterrows():
            if r['contributor_name'] == 'Anonymous':
                continue

            # Nodes
            if not r['contributor_id'] in mapper_v:
                self.graph.add_vertex(count)
                mapper_v[r['contributor_id']] = count
                self.graph.vs[count]['id'] = r['contributor_id']
                self.graph.vs[count]['label'] = r['contributor_name']
                self.graph.vs[count]['num_edits'] = 0
                self.graph.vs[count]['first_edit'] = r['timestamp']
                self.graph.vs[count]['birth'] = int(datetime.strptime(
                    str(r['timestamp']), "%Y-%m-%d %H:%M:%S").strftime('%s'))
                count += 1

            self.graph.vs[mapper_v[r['contributor_id']]]['num_edits'] += 1
            self.graph.vs[mapper_v[r['contributor_id']]]['last_edit'] = r['timestamp']

            # A page gets serveral contributors
            if not r['page_id'] in user_per_page:
                user_per_page[r['page_id']] = \
                                {r['contributor_id']: [r['timestamp']]}
            else:
                if r['contributor_id'] in user_per_page[r['page_id']]:
                    user_per_page[r['page_id']][r['contributor_id']]\
                                .append(r['timestamp'])
                else:
                    user_per_page[r['page_id']][r['contributor_id']] = \
                            [r['timestamp']]
        count = 0
        # Edges
        for _, p in user_per_page.items():
            aux = {}
            for k_i, v_i in p.items():
                for k_j, v_j in aux.items():
                    if f'{k_i}{k_j}' in mapper_e:
                        self.graph.es[mapper_e[f'{k_i}{k_j}']]['weight'] += 1
                        self.graph.es[mapper_e[f'{k_i}{k_j}']]['w_time'] += \
                            self.calculate_w_time(v_i[-1], v_j[-1])
                        continue
                    if f'{k_j}{k_i}' in mapper_e:
                        self.graph.es[mapper_e[f'{k_j}{k_i}']]['weight'] += 1
                        self.graph.es[mapper_e[f'{k_j}{k_i}']]['w_time'] += \
                            self.calculate_w_time(v_j[-1], v_i[-1])
                        continue

                    self.graph.add_edge(mapper_v[k_i], mapper_v[k_j])
                    mapper_e[f'{k_i}{k_j}'] = count
                    count += 1
                    self.graph.es[mapper_e[f'{k_i}{k_j}']]['weight'] = 1
                    self.graph.es[mapper_e[f'{k_i}{k_j}']]['w_time'] = \
                            self.calculate_w_time(v_i[-1], v_j[-1])
                    self.graph.es[mapper_e[f'{k_i}{k_j}']]['id'] = f'{k_i}{k_j}'
                    self.graph.es[mapper_e[f'{k_i}{k_j}']]['source'] = k_i
                    self.graph.es[mapper_e[f'{k_i}{k_j}']]['target'] = k_j

                aux[k_i] = v_i

        for e in self.graph.es:
            e['w_time'] = e['w_time'] / e['weight']

        return


    def get_metric_dataframe(self, metric):
        if self.AVAILABLE_METRICS[metric] in self.graph.vs.attributes()\
            and 'label' in self.graph.vs.attributes():

            df = pd.DataFrame({
                    'User': self.graph.vs['label'],
                    metric: self.graph.vs[self.AVAILABLE_METRICS[metric]]
                    })
            return df

        return pd.DataFrame()


    @classmethod
    def get_available_metrics(cls) -> dict:
        return cls.AVAILABLE_METRICS


    @classmethod
    def get_user_info(cls) -> dict:
        return cls.USER_INFO

    
    @classmethod
    def get_secondary_metrics(cls) -> dict:
        return cls.SECONDARY_METRICS


    def add_graph_attrs(self):
        self.graph['num_nodes'] = self.graph.vcount()
        self.graph['num_edges'] = self.graph.ecount()
        if 'num_edits' in self.graph.vs.attributes():
            self.graph['max_node_size'] = max(self.graph.vs['num_edits'])
            self.graph['min_node_size'] = min(self.graph.vs['num_edits'])
        if 'birth' in self.graph.vs.attributes():
            self.graph['max_birth'] = max(self.graph.vs['birth'])
            self.graph['min_birth'] = min(self.graph.vs['birth'])
        if 'talk_edits' in self.graph.vs.attributes():
            self.graph['max_talk_edits'] = max(self.graph.vs['talk_edits'])
            self.graph['min_talk_edits'] = min(self.graph.vs['talk_edits'])
        if 'weight' in self.graph.es.attributes():
            self.graph['max_edge_size'] = max(self.graph.es['weight'])
            self.graph['min_edge_size'] = min(self.graph.es['weight'])


    def add_others(self, df):
        self.calculate_edits(df, 'talk')


    def calculate_w_time(self, tsp1, tsp2):
        """
        Calculates the weight based on time between 2 editions

        Parameters:
            -tsp1: a timestamp
            -tsp2: a timestamp

        Returns: a number which represent the w_time
        """
        t1 = int(datetime.strptime(str(tsp1),
            "%Y-%m-%d %H:%M:%S").strftime('%s'))
        t2 = int(datetime.strptime(str(tsp2),
            "%Y-%m-%d %H:%M:%S").strftime('%s'))
        t_gap = math.fabs(t1 - t2)

        if t_gap == 0:
            return 2

        if t_gap > self.TIME_DIV:
            return self.TIME_DIV / t_gap

        return 1 + numpy.interp(
            self.TIME_DIV / t_gap, [1, self.TIME_BOUND], [0, 1])