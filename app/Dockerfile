# ─── STAGE 1: BUILDER ───────────────────────────────────────────
# This stage installs all Python dependencies
# We use a separate stage so build tools don't end up in final image
FROM python:3.11-slim AS builder

# Set working directory inside this temporary container
WORKDIR /build

# Copy only requirements first (not the whole app)
# Why? Docker caches each step. If requirements.txt hasn't changed,
# Docker skips the pip install step and reuses the cached result.
# This makes rebuilds much faster.
COPY requirements.txt .

# Install dependencies into a specific folder
# --prefix puts everything into /build/packages
# --no-cache-dir means don't save pip's download cache (saves space)
RUN pip install \
    --prefix=/build/packages \
    --no-cache-dir \
    -r requirements.txt

# ─── STAGE 2: FINAL IMAGE ───────────────────────────────────────
# This is the actual image that runs in production
# We start fresh from the same slim base
FROM python:3.11-slim

# Set working directory for the app
WORKDIR /app

# Copy ONLY the installed packages from stage 1
# We don't copy pip, build tools, or anything else
# This keeps the final image small and secure
COPY --from=builder /build/packages /usr/local

# Copy our application code
COPY app.py .

# Create a non-root user called "appuser" with user ID 1000
# Why non-root? Security best practice.
# If an attacker breaks into the container, they get a user
# with minimal permissions — not root (admin) access.
RUN useradd \
    --uid 1000 \
    --no-create-home \
    appuser \
    && chown appuser /app

# Switch to the non-root user
# All commands after this run as appuser, not root
USER 1000

# Tell Docker this container listens on port 5000
# This is documentation — it doesn't actually open the port
EXPOSE 5000

# The command that runs when the container starts
# We use gunicorn (production server) instead of Flask's dev server
# -w 2 means 2 worker processes (handles more requests)
# -b 0.0.0.0:5000 means listen on all network interfaces, port 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]