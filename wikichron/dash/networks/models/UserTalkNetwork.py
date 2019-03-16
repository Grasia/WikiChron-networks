"""
   UserTalkNetwork.py

   Descp: Implementation of User-Talk Pages

   Created on: 16/03/2019

   Copyright 2019 Youssef 'FRYoussef' El Faqir el Rhazoui <f.r.youssef@hotmail.com>
"""

import pandas as pd
import re

from .BaseNetwork import BaseNetwork

class UserTalkNetwork(BaseNetwork):
    """
    This class use user-talk pages to perform a network, 
    where NODES are wiki users who edit in a user-talk page, and a tie
    is inferred when user A edits the B's user-talk-page.
    Thus the EDGES are directed.

    Arguments:
        - Node:
            * num_edits: the number of edits in itself's user-talk-page
            * article_edits: edits in article pages
            * talk_edits: edits in talk pages
            * id: The user id in the wiki
            * label: the user name in the wiki
        
        - Edge:
            * id: sourceId + targetId 
            * source: user_id
            * target: user_id
            * weight: the number of editions in the user-talk-page
    """

    NAME = 'User Talk Pages'
    CODE = 'user_talk_network'

    AVAILABLE_METRICS = {
        'Edits in its own Page': 'num_edits',
        'Betweenness': 'betweenness',
        'Page Rank': 'page_rank'
    }

    SECONDARY_METRICS = {
        'Article Edits': {
            'key': 'article_edits',
            'max': 'max_article_edits',
            'min': 'min_article_edits'
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
        'Article Edits': 'article_edits',
        'Talk Edits': 'talk_edits'
    }

    def __init__(self, is_directed = True, graph = {}):
        super().__init__(is_directed = is_directed, graph = graph)


    def generate_from_pandas(self, df):
        user_per_page = {}
        mapper_v = {}
        count = 0

        dff = self.remove_non_user_talk_data(df)
        for _, r in dff.iterrows():
            # Nodes
            if not r['contributor_name'] in mapper_v:
                self.graph.add_vertex(count)
                mapper_v[r['contributor_name']] = count
                self.graph.vs[count]['id'] = int(r['contributor_id'])
                self.graph.vs[count]['label'] = r['contributor_name']
                self.graph.vs[count]['num_edits'] = 0
                count += 1

            page_t = re.sub('User talk:', '', r['page_title'])

            if page_t == r['contributor_name']:
                self.graph.vs[count]['num_edits'] += 1
            else:
                # A page gets serveral contributors
                if not page_t in user_per_page:
                    user_per_page[page_t] = {r['contributor_name']: 1}
                else:
                    if r['contributor_name'] in user_per_page[page_t]:
                        user_per_page[page_t][r['contributor_name']] += 1
                    else:
                        user_per_page[page_t][r['contributor_name']] = 1

        count = 0
        # Edges
        for page_name, p_dict in user_per_page.items():
            for user, edits in p_dict.items():
                self.graph.add_edge(mapper_v[user], mapper_v[page_name])
                count += 1
                source = self.graph.vs[mapper_v[user]]['id']
                target = self.graph.vs[mapper_v[page_name]]['id']
                edge_id = (source << 32) + target
                self.graph.es[count]['id'] = edge_id
                self.graph.es[count]['weight'] = edits
                self.graph.es[count]['source'] = source
                self.graph.es[count]['target'] = target
                