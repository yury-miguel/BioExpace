# -*- coding: utf-8 -*-

# Autor: Yury
# Data: 04/10/2025

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from business.orch import BioInsightPipeline

llms = BioInsightPipeline()
llms.run()