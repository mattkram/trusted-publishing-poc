FROM continuumio/miniconda3:24.5.0-0

WORKDIR /app

# Create the prod conda environment
COPY ./environment.yaml ./
RUN conda env create -p /opt/env -f environment.yaml
ENV PATH="/opt/env/bin:${PATH}"

# Copy in the app code
COPY app.py ./

# Expose the port and run the service
EXPOSE 8000
ENTRYPOINT ["fastapi"]
CMD ["run", "app.py"]
