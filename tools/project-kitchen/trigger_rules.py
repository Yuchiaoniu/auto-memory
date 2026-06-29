# -*- coding: utf-8 -*-
import re, os

TRIGGER_DOCS = [
    (re.compile(r'besu|gcp|vm\b|rpc|節點|私鏈|bootnode|gcloud', re.I),
     os.path.join('docs', 'besu-reference.md')),
    (re.compile(r'thesis.rewrite|論文改寫|論文段落|學術寫作', re.I),
     os.path.join('docs', 'thesis-writing-rules.md')),
]
