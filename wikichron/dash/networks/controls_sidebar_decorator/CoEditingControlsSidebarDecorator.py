#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   CoEditingControlsSidebarDecorator.py

   Descp: A class to implement the decorator pattern in order to make an
     easier implementation of the right sidebar

   Created on: 08-02-2019

   Copyright 2019 Youssef 'FRYoussef' El Faqir el Rhazoui <f.r.youssef@hotmail.com>
"""

import time
import abc
import json
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime

from .BaseControlsSidebarDecorator import BaseControlsSidebarDecorator
from networks.cytoscape_stylesheet.CoEditingStylesheet import CoEditingStylesheet
from networks.models.CoEditingNetwork import CoEditingNetwork
import data_controller

class CoEditingControlsSidebarDecorator(BaseControlsSidebarDecorator):

    def __init__(self, sidebar):
        super().__init__(sidebar)


    @staticmethod
    def default_stats(st1 = 'Nodes: ...', st2 = 'First User: ...',
            st3 = 'Edges: ...', st4 = 'Last User: ...', st5 = 'Communities: ...',
            st6 = 'Max Hub Degree: ...', st7 = 'Assortativity Degree: ...'):

        return [
                html.Div([
                    html.P(st1, className='left-element'),
                    html.P(st2, className='right-element')
                ]),
                html.Div([
                    html.P(st3, className='left-element'),
                    html.P(st4, className='right-element')
                ]),
                html.Div([
                    html.P(st5, className='left-element', id='n_communities'),
                    html.P(st6, className='right-element')
                ]),
                html.Div([
                    html.P(st7, className='left-element', id='assort_degree')
                ])]


    @staticmethod
    def default_metrics():
        return [
                html.Div(children=[
                    html.Span('PageRank', className='left-element'),
                    html.Button('Run', id='calculate_page_rank',
                                type='button',
                                className='right-element action-button'),
                    ],
                    className='metrics-section'),
                html.Div(children=[
                    html.Span('Betweenness', className='left-element'),
                    html.Button('Run', id='calculate_betweenness',
                                type='button',
                                className='right-element action-button'),
                    ],
                    className='metrics-section'),
                html.Div([
                    html.Span('Communities', className='left-element'),
                    html.Button('Run', id='calculate_communities',
                                type='button',
                                className='right-element action-button')
                ],
                className='metrics-section'),
                html.Div([
                    html.Span('Assortativity', className='left-element'),
                    html.Button('Run', id='calc_assort_degree',
                                type='button',
                                className='right-element action-button')
                ],
                className='metrics-section')
            ]

    @staticmethod
    def default_options():
        return [
                    html.Button('Show Labels', id='show_labels',
                        className='control-button action-button'),
                    html.Button('Show Edits', id='show_edits',
                        className='control-button action-button'),
                    html.Button('Show PageRank', id='show_page_rank',
                        disabled=True,
                        className='control-button action-button'),
                    html.Button('Show Betweenness', id='show_betweenness',
                        disabled=True,
                        className='control-button action-button'),
                    html.Button('Color by Cluster', id='color_cluster',
                        disabled=True,
                        className='control-button action-button'),
                ]


    def add_stats_section(self):
        stats = self.default_stats()
        super().add_stats_section(stats)


    def add_metrics_section(self):
        metrics = self.default_metrics()
        super().add_metrics_section(metrics)


    def add_options_section(self):
        options = self.default_options()
        super().add_options_section(options)


    def add_all_sections(self):
        self.add_stats_section()
        self.add_metrics_section()
        self.add_options_section()


    @classmethod
    def bind_callbacks(cls, app):

        @app.callback(
            Output('stats', 'children'),
            [Input('network-ready', 'value')]
        )
        def update_stats(cy_network):
            if not cy_network:
                return CoEditingControlsSidebarDecorator.default_stats()

            date1 = datetime.fromtimestamp(cy_network["first_entry"]).strftime("%Y-%m-%d")
            date2 = datetime.fromtimestamp(cy_network["last_entry"]).strftime("%Y-%m-%d")

            return CoEditingControlsSidebarDecorator.default_stats(
                st1 = f'Nodes: {cy_network["num_nodes"]}',
                st2 = f'First User: {date1}',
                st3 = f'Edges: {cy_network["num_edges"]}',
                st4 = f'Last User: {date2}',
                st5 = f'Communities: {cy_network["n_communities"]}',
                st6 = f'Max Hub Degree: {cy_network["max_degree"]}',
                st7 = f'Assortativity Degree: {cy_network["assortativity"]}'
                )


        @app.callback(
            Output('show_labels', 'className'),
            [Input('show_labels', 'n_clicks')]
        )
        def switch_show_labels(clicks):
            if not clicks or clicks % 2 == 0:
                return 'control-button action-button'
            return 'control-button action-button-pressed'


        @app.callback(
            Output('show_page_rank', 'className'),
            [Input('show_page_rank', 'n_clicks')]
        )
        def switch_show_page_rank(clicks):
            if not clicks or clicks % 2 == 0:
                return 'control-button action-button'
            return 'control-button action-button-pressed'


        @app.callback(
            Output('show_betweenness', 'className'),
            [Input('show_betweenness', 'n_clicks')]
        )
        def switch_show_betweenness(clicks):
            if not clicks or clicks % 2 == 0:
                return 'control-button action-button'
            return 'control-button action-button-pressed'


        @app.callback(
            Output('show_edits', 'className'),
            [Input('show_edits', 'n_clicks')]
        )
        def switch_show_edits(clicks):
            if not clicks or clicks % 2 == 0:
                return 'control-button action-button'
            return 'control-button action-button-pressed'


        @app.callback(
            Output('color_cluster', 'className'),
            [Input('color_cluster', 'n_clicks')]
        )
        def switch_color_by_cluster(clicks):
            if not clicks or clicks % 2 == 0:
                return 'control-button action-button'
            return 'control-button action-button-pressed'


        @app.callback(
            Output('calculate_page_rank', 'className'),
            [Input('calculate_page_rank', 'n_clicks')]
        )
        def switch_run_page_rank(clicks):
            if not clicks:
                return 'right-element action-button'
            return 'right-element action-button-pressed'


        @app.callback(
            Output('calculate_betweenness', 'className'),
            [Input('calculate_betweenness', 'n_clicks')]
        )
        def switch_run_betweenness(clicks):
            if not clicks:
                return 'right-element action-button'
            return 'right-element action-button-pressed'


        @app.callback(
            Output('calculate_communities', 'className'),
            [Input('calculate_communities', 'n_clicks')]
        )
        def switch_run_communities(clicks):
            if not clicks:
                return 'right-element action-button'
            return 'right-element action-button-pressed'


        @app.callback(
            Output('calc_assort_degree', 'className'),
            [Input('calc_assort_degree', 'n_clicks')]
        )
        def switch_run_assortativity(clicks):
            if not clicks:
                return 'right-element action-button'
            return 'right-element action-button-pressed'


        @app.callback(
            Output('calculate_page_rank', 'disabled'),
            [Input('calculate_page_rank', 'n_clicks')]
        )
        def disable_button_run_page_rank(clicks):
            if not clicks:
                return False
            return True


        @app.callback(
            Output('calculate_betweenness', 'disabled'),
            [Input('calculate_betweenness', 'n_clicks')]
        )
        def disable_button_run_betweenness(clicks):
            if not clicks:
                return False
            return True


        @app.callback(
            Output('calculate_communities', 'disabled'),
            [Input('calculate_communities', 'n_clicks')]
        )
        def disable_button_run_communities(clicks):
            if not clicks:
                return False
            return True


        @app.callback(
            Output('show_page_rank', 'disabled'),
            [Input('calculate_page_rank', 'n_clicks')]
        )
        def disable_toggle_show_page_rank(clicks):
            if not clicks:
                return True
            return False


        @app.callback(
            Output('color_cluster', 'disabled'),
            [Input('calculate_communities', 'n_clicks')]
        )
        def disable_toggle_show_communities(clicks):
            if not clicks:
                return True
            return False


        @app.callback(
            Output('show_betweenness', 'disabled'),
            [Input('calculate_betweenness', 'n_clicks')]
        )
        def disable_toggle_show_betweenness(clicks):
            if not clicks:
                return True
            return False


        @app.callback(
            Output('n_communities', 'content'),
            [Input('calculate_communities', 'n_clicks')],
            [State('network-ready', 'value')]
        )
        def update_num_communities(_, cy_network):
            return f'Communities: {cy_network["n_communities"]}'


        @app.callback(
            Output('assort_degree', 'content'),
            [Input('calc_assort_degree', 'n_clicks')],
            [State('network-ready', 'value')]
        )
        def update_assortativity(_, cy_network):
            return f'Assortativity Degree: {cy_network["assortativity"]}'


        @app.callback(
            Output('cytoscape', 'stylesheet'),
            [Input('cytoscape', 'elements'),
            Input('show_labels', 'n_clicks'),
            Input('show_page_rank', 'n_clicks'),
            Input('show_edits', 'n_clicks'),
            Input('show_betweenness', 'n_clicks'),
            Input('color_cluster', 'n_clicks')],
            [State('network-ready', 'value'),
            State('cytoscape', 'stylesheet')]
        )
        def update_stylesheet(_, lb_clicks, pr_clicks, ed_clicks, bet_clicks,
            com_clicks, cy_network, stylesheet):

            if not cy_network:
                return CoEditingStylesheet().cy_stylesheet

            co_stylesheet = CoEditingStylesheet(stylesheet)
            co_stylesheet.all_transformations(cy_network)

            if lb_clicks and lb_clicks % 2:
                co_stylesheet.set_label('data(label)')
            elif ed_clicks and ed_clicks % 2:
                 co_stylesheet.set_label('data(num_edits)')
            elif pr_clicks and pr_clicks % 2:
                co_stylesheet.set_label('data(page_rank)')
            elif bet_clicks and bet_clicks % 2:
                co_stylesheet.set_label('data(betweenness)')
            else:
                co_stylesheet.set_label('')

            if com_clicks and not cy_network["n_communities"] == '...' \
            and com_clicks % 2 == 1:
                co_stylesheet.color_nodes_by_cluster()
            else:
                co_stylesheet.color_nodes(cy_network)

            return co_stylesheet.cy_stylesheet


        @app.callback(
            Output('network-ready', 'value'),
            [Input('ready', 'value'),
            Input('calculate_page_rank', 'n_clicks'),
            Input('calculate_betweenness', 'n_clicks'),
            Input('calculate_communities', 'n_clicks'),
            Input('calc_assort_degree', 'n_clicks')],
            [State('initial-selection', 'children'),
            State('dates-slider', 'value')]
        )
        def update_network(ready, pr_clicks, bet_clicks, com_clicks, assor_clicks,
            selection_json, slider):

            if not ready:
                return None

            # get network instance from selection
            selection = json.loads(selection_json)
            wiki = selection['wikis'][0]
            network_code = selection['network']

            print(' * [Info] Building the network....')
            time_start_calculations = time.perf_counter()

            first_entry = data_controller.get_first_entry(wiki)
            first_entry = int(datetime.strptime(str(first_entry), "%Y-%m-%d %H:%M:%S").strftime('%s'))

            upper_bound = first_entry + slider[1] * \
            CoEditingNetwork.TIME_DIV
            lower_bound = first_entry + slider[0] * \
            CoEditingNetwork.TIME_DIV

            upper_bound = datetime.fromtimestamp(upper_bound).strftime("%Y-%m-%d %H:%M:%S")
            lower_bound = datetime.fromtimestamp(lower_bound).strftime("%Y-%m-%d %H:%M:%S")

            network = data_controller.get_network(wiki, network_code, lower_bound, upper_bound)

            time_end_calculations = time.perf_counter() - time_start_calculations
            print(f' * [Timing] Network builded in {time_end_calculations} seconds')

            if pr_clicks and pr_clicks % 2:
                network.calculate_page_rank()

            if bet_clicks and bet_clicks % 2:
                network.calculate_betweenness()

            if com_clicks and com_clicks % 2:
                network.calculate_communities()

            if assor_clicks and assor_clicks % 2:
                network.calculate_assortativity_degree()

            return network.to_cytoscape_dict()