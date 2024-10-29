#!/bin/bash

source activate projects
streamlit run /projects/app.py --server.port=8501 --server.maxUploadSize=1 &
python /projects/telegram_bot.py

# Keep the container running
wait
