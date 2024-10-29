# Use ContinuumIO Miniconda as the base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /projects

# Install necessary system packages such as git
RUN apt-get update && apt-get install -y git && apt-get clean

# Clone the GitHub repository
RUN git clone https://github.com/procrastinando/projects .

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
CMD ["/bin/bash", "/projects/entrypoint.sh"]
