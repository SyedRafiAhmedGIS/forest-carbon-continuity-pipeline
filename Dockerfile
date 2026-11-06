FROM continuumio/miniconda3:latest
WORKDIR /app
COPY environment.yaml .
RUN conda env create -f environment.yaml
RUN echo "conda activate forest-carbon-continuity" >> ~/.bashrc
SHELL ["/bin/bash", "-c", "source /opt/conda/bin/activate forest-carbon-continuity && $@"]
COPY . .
EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
