#!/bin/bash

source /opt/conda/etc/profile.d/conda.sh
conda activate projects
streamlit run /projects/app.py --server.port=8501 --server.maxUploadSize=1

# # Run a second environment
# source activate assistant
# python /projects/assistant/run_engines.py &
# streamlit run /projects/assistant/app.py --server.port=50002 --server.maxUploadSize=2 &

# Keep the container running
wait
