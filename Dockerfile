# # Use the continuumio/miniconda3 image as the base
# FROM continuumio/miniconda3

# # Set the working directory
# WORKDIR /

# # Install necessary packages
# RUN apt-get update && apt-get install -y git && apt-get clean

# # Clone the projects
# RUN git clone https://github.com/procrastinando/projects

# # Create a conda environment for csv-translator project and install dependencies
# RUN conda create --name csv-translator python=3.10 -y \
#     && /bin/bash -c "source activate csv-translator" \
#     && pip install -r /projects/csv-translator/requirements.txt

# RUN conda create --name assistant python=3.9 -y \
#     && /bin/bash -c "source activate assistant" \
#     && pip install -r /projects/assistant/requirements.txt

# # Give execute permissions to the entrypoint script
# RUN chmod +x /projects/entrypoint.sh

# # Expose the ports for both projects
# EXPOSE 50001 50001

# # Start the entrypoint script
# CMD ["/projects/entrypoint.sh"]





# Use the continuumio/miniconda3 image as the base
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /projects

# Install necessary packages
RUN apt-get update && apt-get install -y git && apt-get clean

# Clone the projects
RUN git clone https://github.com/procrastinando/projects .

# Create a conda environment for csv-translator project and install dependencies
RUN conda create --name csv-translator python=3.10 -y \
    && /bin/bash -c "source activate csv-translator && pip install -r csv-translator/requirements.txt"

# Create a conda environment for assistant project and install dependencies
RUN conda create --name assistant python=3.9 -y \
    && /bin/bash -c "source activate assistant && pip install -r assistant/requirements.txt"

# Give execute permissions to the entrypoint script
RUN chmod +x /projects/entrypoint.sh

# Expose the ports for both projects
EXPOSE 50001 50001

# Start the entrypoint script
CMD ["/projects/entrypoint.sh"]
