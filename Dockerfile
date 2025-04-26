FROM continuumio/miniconda3:24.5.0-0

WORKDIR /app

# Create the prod conda environment
COPY ./environment.yml ./
RUN conda env create -p /opt/env -f environment.yaml
ENV PATH="/opt/env/bin:${PATH}"

# Copy in the app code
COPY main.py ./

# Expose the port and run the service
EXPOSE 8000
ENTRYPOINT ["fastapi"]
CMD ["run", "main.py"]
