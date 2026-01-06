# Python image to use.
# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
# FROM python:3.11-alpine
ARG type=flask

ENV APP_ROOT="."
# ENV SERVICE_ACCOUNT='{"serviceaccount":"replacewithfilecontent"}'
# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Set the working directory to /app
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# # copy the requirements file used for dependencies
# COPY requirements.txt .
COPY pyproject.toml uv.lock .

# # Install any needed packages specified in requirements.txt
# RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the rest of the working directory contents into the container at /app
COPY src .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Use the non-root user to run our application
USER nonroot

# Run app.py when the container launches
#
# CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "src/uv_docker_example"]
# CMD ["fastapi", "run", "app.py", ]
CMD ["uvicorn", "app:app","--host", "0.0.0.0","--port", "8080"]
