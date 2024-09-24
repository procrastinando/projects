# # Use the continuumio/miniconda3 image as the base
# FROM continuumio/miniconda3

# # Set the working directory
# WORKDIR /projects

# # Install necessary packages
# RUN apt-get update && apt-get install -y git && apt-get clean

# # Clone the projects
# RUN git clone https://github.com/procrastinando/projects .

# # Create a conda environment for csv-translator project and install dependencies
# RUN conda create --name projects python=3.10 -y \
#     && conda activate projects \
#     && pip install -r csv-translator/requirements.txt \
#     && pip install -r img2img/requirements.txt \
#     && pip install -r sub2audio/requirements.txt

# # # Create a second conda environment
# # RUN conda create --name assistant python=3.9 -y \
# #     && /bin/bash -c "source activate assistant && pip install -r assistant/requirements.txt"

# # Give execute permissions to the entrypoint script
# RUN chmod +x /projects/entrypoint.sh

# # Expose the ports for both projects
# EXPOSE 50001 50002 50003

# # Start the entrypoint script
# CMD ["/projects/entrypoint.sh"]












# # Use the continuumio/miniconda3 image as the base
# FROM continuumio/miniconda3

# # Set the working directory
# WORKDIR /projects

# # Install necessary packages
# RUN apt-get update && apt-get install -y git && apt-get clean

# # Clone the projects
# RUN git clone https://github.com/procrastinando/projects .

# # Create a conda environment for projects and install dependencies
# RUN conda create --name projects python=3.10 -y
# SHELL ["conda", "run", "-n", "projects", "/bin/bash", "-c"]

# # Install requirements
# RUN pip install -r csv-translator/requirements.txt \
#     && pip install -r img2img/requirements.txt \
#     && pip install -r sub2audio/requirements.txt

# # Give execute permissions to the entrypoint script
# RUN chmod +x /projects/entrypoint.sh

# # Expose the ports for both projects
# EXPOSE 50001 50002 50003

# # Start the entrypoint script
# CMD ["/projects/entrypoint.sh"]












# Use the specified base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /projects

# Install necessary packages
RUN apt-get update && apt-get install -y git && apt-get clean

# Clone the repository
RUN git clone https://github.com/procrastinando/projects .

# Create a new conda environment
RUN conda create --name projects python=3.10 -y

# Activate the conda environment and install requirements
RUN echo "source activate projects" > ~/.bashrc
ENV PATH /opt/conda/envs/projects/bin:$PATH

RUN pip install -r csv-translator/requirements.txt \
    && pip install -r img2img/requirements.txt \
    && pip install -r sub2audio/requirements.txt

# Make the entrypoint script executable
RUN chmod +x /projects/entrypoint.sh

# Expose the specified ports
EXPOSE 50001 50002 50503

# Set the entrypoint
CMD ["/projects/entrypoint.sh"]