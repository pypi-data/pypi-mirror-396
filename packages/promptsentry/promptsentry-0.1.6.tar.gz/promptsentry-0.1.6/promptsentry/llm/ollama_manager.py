"""
Ollama Management - Auto-start and model management

Automatically ensures Ollama is running and required models are available.
"""

import subprocess
import time


class OllamaManager:
    """
    Manages Ollama service and model availability.

    Automatically:
    - Starts Ollama if not running
    - Downloads models if not available
    """

    DEFAULT_MODEL = "qwen2.5-coder:0.5b"

    @staticmethod
    def is_ollama_running() -> bool:
        """Check if Ollama service is running."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def start_ollama() -> bool:
        """
        Start Ollama service in the background.

        Returns:
            True if successfully started, False otherwise
        """
        try:
            # Try to start Ollama serve in background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Wait a bit for Ollama to start
            time.sleep(3)

            # Verify it's running
            return OllamaManager.is_ollama_running()
        except FileNotFoundError:
            return False
        except Exception:
            return False

    @staticmethod
    def is_model_available(model_name: str = DEFAULT_MODEL) -> bool:
        """
        Check if a specific model is available in Ollama.

        Args:
            model_name: Name of the model to check

        Returns:
            True if model is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Check if model name is in the output
                return model_name in result.stdout
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def pull_model(model_name: str = DEFAULT_MODEL, verbose: bool = True) -> bool:
        """
        Pull/download a model from Ollama registry.

        Args:
            model_name: Name of the model to pull
            verbose: Show download progress

        Returns:
            True if successfully pulled, False otherwise
        """
        try:
            if verbose:
                print(f"Downloading {model_name} (~397 MB)...")
                print("This may take a few minutes depending on your connection...")

            result = subprocess.run(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE if not verbose else None,
                stderr=subprocess.PIPE if not verbose else None,
                timeout=600  # 10 minute timeout for download
            )

            if result.returncode == 0:
                if verbose:
                    print(f"✓ {model_name} downloaded successfully!")
                return True
            return False
        except subprocess.TimeoutExpired:
            if verbose:
                print(f"✗ Timeout while downloading {model_name}")
            return False
        except FileNotFoundError:
            if verbose:
                print("✗ Ollama not found. Please install Ollama from https://ollama.com")
            return False
        except Exception as e:
            if verbose:
                print(f"✗ Error downloading model: {e}")
            return False

    @staticmethod
    def ensure_ollama_ready(model_name: str = DEFAULT_MODEL, verbose: bool = True) -> tuple[bool, str]:
        """
        Ensure Ollama is running and the model is available.
        Automatically starts Ollama and downloads model if needed.

        Args:
            model_name: Name of the model required
            verbose: Show progress messages

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Step 1: Check if Ollama is installed
        try:
            subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=5
            )
        except FileNotFoundError:
            return False, (
                "Ollama is not installed. Please install it from https://ollama.com\n"
                "After installation, run: promptsentry init"
            )

        # Step 2: Check if Ollama is running, start if not
        if not OllamaManager.is_ollama_running():
            if verbose:
                print("Ollama is not running. Starting Ollama...")

            if OllamaManager.start_ollama():
                if verbose:
                    print("✓ Ollama started successfully")
            else:
                return False, (
                    "Failed to start Ollama automatically.\n"
                    "Please start it manually by running: ollama serve"
                )

        # Step 3: Check if model is available, download if not
        if not OllamaManager.is_model_available(model_name):
            if verbose:
                print(f"Model {model_name} not found. Downloading...")

            if OllamaManager.pull_model(model_name, verbose=verbose):
                return True, f"Ollama is ready with {model_name}"
            else:
                return False, f"Failed to download {model_name}"

        # Everything is ready
        if verbose:
            print(f"✓ Ollama is running with {model_name}")
        return True, f"Ollama is ready with {model_name}"

    @staticmethod
    def get_available_models() -> list[str]:
        """
        Get list of available models in Ollama.

        Returns:
            List of model names
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]  # First column is name
                        models.append(model_name)
                return models
            return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
