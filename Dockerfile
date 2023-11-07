# Include Python
FROM runpod/pytorch:3.10-2.0.0-117

RUN apt update
RUN apt install -y libgl1-mesa-glx ffmpeg libsm6 libxext6

# Define your working directory
RUN mkdir /src
WORKDIR /src

# Install runpod
RUN pip install runpod

# Download SDXL model for training
RUN mkdir /src/sdxl-cache
RUN wget https://weights.replicate.delivery/default/sdxl/sdxl-vae-fix-1.0.tar && tar -xvf sdxl-vae-fix-1.0.tar -C /src/sdxl-cache && rm sdxl-vae-fix-1.0.tar

# Instal python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the training files
COPY * .

# Call your file when your container starts
CMD [ "python", "-u", "/src/worker.py" ]