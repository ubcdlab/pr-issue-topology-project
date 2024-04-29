#!/bin/bash
python interactive_html/generate_embeddable_html.py --cypher cypher_scripts/CompetingPRs.cypher --name=competing_prs
python interactive_html/generate_embeddable_html.py --cypher cypher_scripts/DivergentPR.cypher --name=divergent_pr
python interactive_html/generate_embeddable_html.py --cypher cypher_scripts/ExtendedPR.cypher --name=extended_prs
python interactive_html/generate_embeddable_html.py --cypher cypher_scripts/DuplicateIssueHub.cypher --name=duplicate_issue_hub
python interactive_html/generate_embeddable_html.py --cypher cypher_scripts/DecomposedIssue.cypher --name=decomposed_issue
python interactive_html/generate_embeddable_html.py --cypher cypher_scripts/DependentPRs.cypher --name=dependent_prs
python interactive_html/generate_embeddable_html.py --cypher=cypher_scripts/Consequence_1.cypher --name=consequent_issue
python interactive_html/generate_embeddable_html.py --cypher=cypher_scripts/Consequence_2.cypher --name=consequent_issue_prs
python interactive_html/generate_embeddable_html.py --cypher=cypher_scripts/IntegratingPRHub.cypher --name=integrating_pr_hub

python interactive_html/generate_repo_html.py --repo Rapptz/discord.py 
python interactive_html/generate_repo_html.py --repo metafizzy/flickity
python interactive_html/generate_repo_html.py --repo kubernetes-sigs/kustomize
python interactive_html/generate_repo_html.py --repo TypeStrong/ts-node
python interactive_html/generate_repo_html.py --repo MithrilJS/mithril.js
python interactive_html/generate_repo_html.py --repo jupyterhub/jupyterhub
python interactive_html/generate_repo_html.py --repo apache/dubbo
python interactive_html/generate_repo_html.py --repo App-vNext/Polly
python interactive_html/generate_repo_html.py --repo mlflow/mlflow
python interactive_html/generate_repo_html.py --repo rematch/rematch
python interactive_html/generate_repo_html.py --repo grpc/grpc-web
python interactive_html/generate_repo_html.py --repo chaijs/chai
python interactive_html/generate_repo_html.py --repo iron/iron
python interactive_html/generate_repo_html.py --repo ptomasroos/react-native-scrollable-tab-view
python interactive_html/generate_repo_html.py --repo Project-OSRM/osrm-backend
python interactive_html/generate_repo_html.py --repo tensorpack/tensorpack
python interactive_html/generate_repo_html.py --repo BurntSushi/toml
python interactive_html/generate_repo_html.py --repo summernote/summernote
python interactive_html/generate_repo_html.py --repo MagicStack/uvloop
python interactive_html/generate_repo_html.py --repo deployphp/deployer
python interactive_html/generate_repo_html.py --repo varvet/pundit 
python interactive_html/generate_repo_html.py --repo pagekit/pagekit

