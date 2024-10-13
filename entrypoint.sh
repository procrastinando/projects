#!/bin/bash

source activate projects
streamlit run /projects/csv_translator/csv_translator.py --server.port=8501 --server.maxUploadSize=1 &
streamlit run /projects/img2img/img2img.py --server.port=8502 --server.maxUploadSize=1 &
streamlit run /projects/sub2audio/sub2audio.py --server.port=8503 --server.maxUploadSize=1 &
streamlit run /projects/ip_insight/ip_insight.py --server.port=8504 --server.maxUploadSize=1 &

# # Run a second environment
# source activate assistant
# python /projects/assistant/run_engines.py &
# streamlit run /projects/assistant/app.py --server.port=50002 --server.maxUploadSize=2 &

# Keep the container running
wait
