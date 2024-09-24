#!/bin/bash

# Activate the conda environment for translator and run the app on port 101
source activate csv-translator
streamlit run /projects/csv-translator/app.py --server.port 101 &

# Keep the container running
wait