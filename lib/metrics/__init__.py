#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   __init__.py

   Defines metrics package and init public list: available_metrics.

   Created on: 15-nov-2017

   Copyright 2017 Abel 'Akronix' Serrano Juste <akronix5@gmail.com>
"""

from metrics.metrics_generator import generate_metrics

print('Generating available metrics...')
available_metrics = generate_metrics()

