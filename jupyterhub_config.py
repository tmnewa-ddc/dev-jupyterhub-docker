# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()  # noqa: F821

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"

# Spawn containers from this image
c.DockerSpawner.allowed_images = os.environ.get("DOCKER_LAB_IMAGE", '').split(';')

# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get("DOCKER_SPAWN_CMD", "start-singleuser.sh")
c.DockerSpawner.cmd = spawn_cmd

# Connect containers to this Docker network
network_name = os.environ["DOCKER_NETWORK_NAME"]
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name

# Explicitly set notebook directory because we'll be mounting a volume to it.
# Most `jupyter/docker-stacks` *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR", "/home/jovyan/work")
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": notebook_dir}

# Remove containers once they are stopped
c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = "jupyterhub"
c.JupyterHub.hub_port = 8080

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

# Authenticate users with Native Authenticator
c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator"

# Allow anyone to sign-up without approval
c.NativeAuthenticator.open_signup = False

# Allowed admins
admin = os.environ.get("JUPYTERHUB_ADMIN")
if admin:
    c.Authenticator.admin_users = [admin]


### expand

# notebook cpu in the container
c.DockerSpawner.cpu_limit = float(os.environ.get("DOCKER_LAB_CPU", '1'))
# notebook memory in the container
c.DockerSpawner.mem_limit = os.environ.get("DOCKER_LAB_MEM", "4G")


# Authenticator
c.NativeAuthenticator.allowed_failed_logins = 3
c.NativeAuthenticator.check_common_password = True
c.NativeAuthenticator.minimum_password_length = 8

# idle
c.ServerApp.shutdown_no_activity_timeout = 60 * 60
c.MappingKernelManager.cull_idle_timeout = 30 * 60
c.MappingKernelManager.cull_interval = 5 * 60

# env
c.DockerSpawner.extra_create_kwargs = {'user': 'root'}
c.DockerSpawner.extra_host_config = {'runtime': 'nvidia'}
c.DockerSpawner.environment = {
    'GRANT_SUDO': '1',
    "JUPYTER_ENABLE_LAB": 'yes',
    'UID': '0',
    "NVIDIA_VISIBLE_DEVICES": os.environ.get("DOCKER_LAB_GPU", "")
}
