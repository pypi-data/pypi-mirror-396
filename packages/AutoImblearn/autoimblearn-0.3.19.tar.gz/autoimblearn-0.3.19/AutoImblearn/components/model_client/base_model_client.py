# AutoImblearn/components/model_client/base_model_client.py
import time
import json
import os
import pickle
import docker
import requests
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import socket
from abc import ABC, abstractmethod
import sys


def get_free_host_port():
    """Find a free port on the host (works from inside a container using DooD)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # let OS pick a free port
        return s.getsockname()[1]

def is_port_free(port):
    """Test if the port is free"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) != 0


def _get_default_gateway_ip():
    """
    Return the default gateway IP (useful when running inside a container).
    """
    try:
        with open("/proc/net/route") as f:
            for line in f.readlines()[1:]:
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                if parts[1] != "00000000":
                    continue
                gateway = int(parts[2], 16)
                return socket.inet_ntoa(gateway.to_bytes(4, "little"))
    except Exception:
        return None
    return None


def _detect_api_host():
    """
    Choose the host to reach Docker-exposed ports.
    - When inside a container, prefer host.docker.internal, fall back to gateway.
    - Default to localhost for host-based execution.
    """
    if os.path.exists("/.dockerenv"):
        try:
            socket.gethostbyname("host.docker.internal")
            return "host.docker.internal"
        except socket.gaierror:
            gateway = _get_default_gateway_ip()
            if gateway:
                return gateway
    return "localhost"


class BaseDockerModelClient(ABC):
    """Build and run the docker container for the selected model

    fit: Ensure the container is running
    """
    def __init__(self, image_name, container_name, container_port=5000, volume_mounts=None, dockerfile_dir=None, is_transformer=False):
        self.image_name = image_name
        self.container_name = container_name
        self.container_port = container_port
        self.volume_mounts = volume_mounts or {}
        self.client = docker.from_env()

        # set container url
        self.api_host = _detect_api_host()
        self.host_port = get_free_host_port()
        if not is_port_free(self.host_port):
            raise Exception(f"Port {self.host_port} is not free")
        self.api_url = f"http://{self.api_host}:{self.host_port}"

        # Dockerfile
        self.dockerfile_dir = dockerfile_dir

        self.args = None
        self.container_id = None  # Initialize container_id
        self.is_transformer = is_transformer  # True for imputers/transformers, False for classifiers

    def _resolve_host_path(self, path_str: str) -> str:
        """
        Translate container-local bind paths (e.g., /code/...) to host paths for DooD.

        If HOST_PROJECT_PATH is provided (e.g., the repo root on the host), replace the
        /code prefix with that host path so the host docker daemon can mount the correct
        directory. Otherwise, fall back to the original path.
        """
        try:
            host_root = os.environ.get("HOST_PROJECT_PATH")
            if host_root and path_str.startswith("/code"):
                candidate = os.path.join(host_root, os.path.relpath(path_str, "/code"))
                return os.path.abspath(candidate)
        except Exception:
            pass
        return path_str

    @property
    @abstractmethod
    def payload(self):
        """Subclasses must return a dict with key arguments."""
        raise NotImplementedError("Subclass must define 'payload'")

    def is_container_running(self):
        """
        Check if the Docker container with self.container_name exists and is running.
        Returns True if running, False otherwise.
        """
        try:
            container = self.client.containers.get(self.container_name)
            return container.status == 'running'
        except docker.errors.NotFound:
            # Container does not exist
            return False
        except Exception as e:
            # Other error (log it if needed)
            import logging
            logging.warning(f"Error checking container status: {e}")
            return False

    def build_image(self):
        """Build image based on Dockerfile provided"""
        logging.info(f"[⛏️ ] Building image '{self.image_name}' from {self.dockerfile_dir}...")
        # self.client.images.build(path=dockerfile_dir, tag=self.image_name)
        try:
            self.client.images.get(self.image_name)
            logging.info('found prebuilt image')
        except docker.errors.ImageNotFound:
            # TODO update this image build process to automate image genenration
            self.client.images.build(path=self.dockerfile_dir, tag=self.image_name, nocache=True)

        logging.info(f"[✓] Image '{self.image_name}' is available now.")

    def start_container(self):
        """
        Start the container
        """
        logging.info(f"[🚀] Starting container '{self.container_name}'...")
        # binds = {
        #     str(Path(local).resolve()): {'bind': container, 'mode': 'rw'}
        #     for local, container in self.volume_mounts.items()
        # }
        binds = {}
        for local, target in self.volume_mounts.items():
            host_path = self._resolve_host_path(str(Path(local).resolve()))
            if isinstance(target, str):
                binds[host_path] = {'bind': target, 'mode': 'rw'}
            elif isinstance(target, dict):
                binds[host_path] = target  # already formatted correctly
            else:
                raise TypeError(f"Invalid volume mount target for {host_path}: {target}")

        self.container = self.client.containers.run(
            image=self.image_name,
            name=self.container_name,
            ports={f"{self.container_port}/tcp": self.host_port},
            volumes=binds,
            entrypoint=["python3","-m", "app"],
            working_dir='/code/AutoImblearn/Docker',
            detach=True
        )
        self.container_id = self.container.id  # Set container_id

    def get_container_logs(self, tail=50):
        """
        Get container logs for debugging.

        Args:
            tail: Number of lines to retrieve from end of logs

        Returns:
            String containing container logs
        """
        try:
            if not self.container_id:
                return "No container ID available"

            container = self.client.containers.get(self.container_id)
            logs = container.logs(tail=tail).decode('utf-8')
            return logs
        except Exception as e:
            return f"Failed to retrieve logs: {str(e)}"

    def stop_container(self):
        """
        Stop the running container with improved error handling.
        """
        logging.info(f"[🧹] Stopping container '{self.container_name}'...")
        try:
            container = self.client.containers.get(self.container_name)
            container.reload()
            # If the container exited with an error, keep it for debugging.
            exit_code = container.attrs.get("State", {}).get("ExitCode")
            status = container.status
            if status == "exited" and exit_code not in (None, 0):
                logging.warning(
                    f"[!] Container '{self.container_name}' exited with code {exit_code}; preserving for debugging."
                )
                return

            container.stop(timeout=5)  # Add timeout
            container.remove()
            logging.info(f"[✓] Container '{self.container_name}' removed.")
            self.container_id = None  # Clear container ID
        except docker.errors.NotFound:
            logging.info("[!] Container not found, skipping.")

    def wait_for_api(self, timeout=180):
        """
        Wait for the container's API to become responsive.
        Raise an error if the container exits or doesn't respond in time.

        Args:
            timeout: Maximum time to wait in seconds (default 180 for initial builds)
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check container state
                container = self.client.containers.get(self.container_name)
                container.reload()
                if container.status == "exited":
                    logs = container.logs().decode(errors="ignore")
                    raise RuntimeError(f"Container exited prematurely.\nLogs:\n{logs}")

                # Check API health
                response = requests.get(f"{self.api_url}/health")
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                pass  # wait and retry
            except docker.errors.NotFound:
                raise RuntimeError("Container was removed unexpectedly.")

            time.sleep(1)

        raise TimeoutError("API did not become available within timeout period.")

    def ensure_container_running(self):
        """
        Ensure the Docker container is running. Build and start if needed.
        """
        try:
            container = self.client.containers.get(self.container_name)
            if container.status == 'running':
                # remove helper containers once the target container is up and running
                for c in self.client.containers.list(all=True):
                    if c.id != container.id and c.status in ("exited", "created"):
                        try:
                            c.remove(force=True)
                        except Exception as e:
                            print(f"skip {c.name}: {e}")

                print(f"Container {self.container_name} is already running.")
                ports = container.attrs['NetworkSettings']['Ports']
                internal = f"{self.container_port}/tcp"
                host_info = ports.get(internal)
                if host_info:
                    self.host_port = int(host_info[0]['HostPort'])
                    self.api_url = f"http://{self.api_host}:{self.host_port}"
                    print(f"Reusing existing container on port {self.host_port}")
                    return
                else:
                    raise RuntimeError("Could not find port mapping for the running container.")

            else:
                print(f"Container {self.container_name} is not running. Starting...")
                container.start()
                container.reload()
                ports = container.attrs['NetworkSettings']['Ports']
                internal = f"{self.container_port}/tcp"
                host_info = ports.get(internal)
                if host_info:
                    self.host_port = int(host_info[0]['HostPort'])
                    self.api_url = f"http://{self.api_host}:{self.host_port}"
                    print(f"Reconnected container on port {self.host_port}")
                else:
                    raise RuntimeError("Could not find port mapping for the restarted container.")

        except docker.errors.NotFound:
            print("Container not found. Building and starting a new one...")
            self.build_image()
            print("Building and starting a new container...")
            self.start_container()

        # self.wait_for_api(host="localhost", port=self.host_port, path='/health')
        self.wait_for_api()
        print("API is ready.")

    def save_data_2_volume(self, data_folder_path: str, dataset_name: str, X_train, y_train=None, X_test=None, y_test=None):
        """
        Save data to docker volume.

        For transformers (imputers), only X_train is required.
        For classifiers, X_train, y_train, X_test, y_test are required.
        For resamplers, X_train and y_train are required.
        """
        import pandas as pd

        # Build list of data to save based on what's provided
        data_to_save = []

        # X_train is always required
        data_to_save.append((X_train, f"X_train_{self.container_name}.csv"))

        # Add optional data if provided
        if y_train is not None:
            data_to_save.append((y_train, f"y_train_{self.container_name}.csv"))
        if X_test is not None:
            data_to_save.append((X_test, f"X_test_{self.container_name}.csv"))
        if y_test is not None:
            data_to_save.append((y_test, f"y_test_{self.container_name}.csv"))

        # Save each file
        for data, name in data_to_save:
            data_path = os.path.join(data_folder_path, "interim", dataset_name, name)
            os.makedirs(os.path.dirname(data_path), exist_ok=True)

            # Convert to DataFrame if needed and save
            if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
                data.to_csv(data_path, index=False, header=True)
            else:
                # For numpy arrays
                np.savetxt(data_path, data, delimiter=",")

        # Return list of filenames
        return [name for _, name in data_to_save]

    def fit(self, args,  X_train, y_train=None, X_test=None, y_test=None, result_file_name=None, result_file_path=None):
        """
        Fit with training data.

        Now includes proper cleanup on error.
        """
        from ..exceptions import DockerContainerError

        logging.info(f"Fitting {self.__class__.__name__}...")
        self.args = args

        # Save temporary data files to docker volume
        try:
            data_names = self.save_data_2_volume(args.path, args.dataset, X_train, y_train, X_test, y_test)
            logging.debug("Data saved to volume")
        except Exception as e:
            raise DockerContainerError(
                f"Failed to save data to Docker volume",
                image_name=self.image_name,
                operation="save_data"
            ) from e

        try:
            self.ensure_container_running()
            logging.debug("Container is running")

            headers = {"Content-Type": "application/json"}

            # Set parameters
            payload = self.payload.copy()
            if result_file_name is not None:
                payload["result_file_name"] = result_file_name
            if result_file_path is not None:
                payload["result_file_path"] = result_file_path

            response = requests.post(f"{self.api_url}/set", json=payload, headers=headers)
            logging.debug("Parameters set")

            if response.status_code != 201:
                resp_body = response.text if hasattr(response, "text") else ""
                raise DockerContainerError(
                    f"Failed to set parameters: HTTP {response.status_code} Body: {resp_body}",
                    container_id=self.container_id,
                    image_name=self.image_name,
                    operation="set_params"
                )

            # Train model
            response = requests.post(f"{self.api_url}/train", json=payload, headers=headers)
            logging.debug("Training complete")
            response.raise_for_status()

            try:
                api_result = response.json()
            except ValueError:
                api_result = None

            if result_file_path and os.path.exists(result_file_path):
                try:
                    with open(result_file_path, "rb") as result_file:
                        return pickle.load(result_file)
                except Exception as load_error:
                    logging.warning(f"Failed to load result file '{result_file_path}': {load_error}")

            return api_result

        except requests.exceptions.RequestException as e:
            # Network/HTTP errors
            logs = self.get_container_logs() if self.container_id else None
            resp_body = None
            if hasattr(e, "response") and e.response is not None:
                try:
                    resp_body = e.response.text
                except Exception:
                    resp_body = None
            if logs:
                logging.error("Container logs on API failure:\n%s", logs)
            if resp_body:
                logging.error("API error response body:\n%s", resp_body)
            raise DockerContainerError(
                f"API request failed: {str(e)}" + (f"\nResponse body: {resp_body}" if resp_body else ""),
                container_id=self.container_id,
                image_name=self.image_name,
                logs=logs,
                operation="train"
            ) from e

        except Exception as e:
            # Other errors
            logs = self.get_container_logs() if self.container_id else None
            if logs:
                logging.error("Container logs on unexpected error:\n%s", logs)
            logging.error(f"Error during fit: {e}")
            raise DockerContainerError(
                f"Unexpected error during training: {str(e)}",
                container_id=self.container_id,
                image_name=self.image_name,
                logs=logs,
                operation="fit"
            ) from e

        finally:
            pass
