#!/bin/bash

source activate projects
streamlit run /projects/csv-translator/app.py --server.port=50001 --server.maxUploadSize=1 --server.enableCORS=false &
streamlit run /projects/img2img/app.py --server.port=50002 --server.maxUploadSize=1 --server.enableCORS=false &
streamlit run /projects/sub2audio/app.py --server.port=50003 --server.maxUploadSize=1 --server.enableCORS=false &
streamlit run /projects/ip-insight/app.py --server.port=50004 --server.maxUploadSize=1 --server.enableCORS=false &

# # Run a second environment
# source activate assistant
# python /projects/assistant/run_engines.py &
# streamlit run /projects/assistant/app.py --server.port=50002 --server.maxUploadSize=2 &

# Keep the container running
wait
