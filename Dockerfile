# # Use ContinuumIO Miniconda as the base image
# FROM continuumio/miniconda3

# # Set the working directory
# WORKDIR /projects

# # Install necessary system packages like git
# RUN apt-get update && apt-get install -y git && apt-get clean

# # Clone the GitHub repository
# RUN git clone https://github.com/procrastinando/projects /projects

# # Create and install dependencies for csv-translator environment
# RUN conda create --name csv-translator-env python=3.10 -y && \
#     /bin/bash -c "source activate csv-translator-env && \
#     pip install --upgrade pip && \
#     pip install -r /projects/csv-translator/requirements.txt"

# # Create and install dependencies for img2img environment
# RUN conda create --name img2img-env python=3.10 -y && \
#     /bin/bash -c "source activate img2img-env && \
#     pip install --upgrade pip && \
#     pip install -r /projects/img2img/requirements.txt"

# # Create and install dependencies for sub2audio environment
# RUN conda create --name sub2audio-env python=3.10 -y && \
#     /bin/bash -c "source activate sub2audio-env && \
#     pip install --upgrade pip && \
#     pip install -r /projects/sub2audio/requirements.txt"

# # Set execute permission to the entrypoint script
# RUN chmod +x /projects/entrypoint.sh

# # Expose the necessary ports
# EXPOSE 50001 50002 50003

# # Start the container by running the entrypoint script
# CMD ["/projects/entrypoint.sh"]





# # Use ContinuumIO Miniconda as the base image
# FROM continuumio/miniconda3

# # Set the working directory
# WORKDIR /projects

# # Install necessary system packages such as git
# RUN apt-get update && apt-get install -y git && apt-get clean

# # Clone the GitHub repository
# RUN git clone https://github.com/procrastinando/projects /projects

# # Create a new conda environment and install Python 3.10
# RUN conda create --name projects python=3.10 -y

# # Activate the environment and install requirements for each subproject
# RUN /bin/bash -c "source activate projects && \
#     pip install --upgrade pip && \ 
#     pip install -r requirements.txt

# # Set execute permission for the entrypoint script
# RUN chmod +x /projects/entrypoint.sh

# # Expose ports
# EXPOSE 8501

# # Start the container with the entry point script
# CMD ["/projects/entrypoint.sh"]









# Use ContinuumIO Miniconda as the base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /projects

# Install necessary system packages such as git
RUN apt-get update && apt-get install -y git && apt-get clean

# Clone the GitHub repository
RUN git clone https://github.com/procrastinando/projects /projects

# Create a new conda environment and install Python 3.10
RUN conda create --name projects python=3.10 -y

# Activate the environment and install requirements for each subproject
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && \
    conda activate projects && \
    pip install --upgrade pip && \
    pip install -r /projects/requirements.txt"

# Set execute permission for the entrypoint script
RUN chmod +x /projects/entrypoint.sh

# Expose ports
EXPOSE 8501

# Start the container with the entry point script
CMD ["/projects/entrypoint.sh"]
