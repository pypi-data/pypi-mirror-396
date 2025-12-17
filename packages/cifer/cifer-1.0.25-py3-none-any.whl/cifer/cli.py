import os
import sys
import subprocess
import requests
import typer

# ===== Cifer Modules =====
from cifer.agent_ace import run_agent_ace
from cifer.securetrain import encrypt_dataset, train_model, decrypt_model



# ===== Main Typer App =====
app = typer.Typer(help="Cifer CLI")

# ===== Sub App: Securetrain =====
securetrain_app = typer.Typer(help="Secure training commands")
app.add_typer(securetrain_app, name="securetrain")


# ================= Securetrain Commands =================
@securetrain_app.command("encrypt-dataset")
def securetrain_encrypt(
    dataset: str = typer.Option(..., help="Dataset path or URL"),
    output: str = typer.Option(..., help="Output path for encrypted file"),
):
    """Encrypt dataset with Homomorphic Encryption"""
    encrypt_dataset(dataset, output)


@securetrain_app.command("train")
def securetrain_train(
    encrypted_data: str = typer.Option(..., help="Path to encrypted dataset"),
    output_model: str = typer.Option(..., help="Output path for trained model"),
):
    """Train model on encrypted dataset"""
    train_model(encrypted_data, output_model)


@securetrain_app.command("decrypt-model")
def securetrain_decrypt(
    input_model: str = typer.Option(..., help="Encrypted model path"),
    output_model: str = typer.Option(..., help="Decrypted output path"),
):
    """Decrypt trained encrypted model"""
    decrypt_model(input_model, output_model)


# ================= Kernel Command =================
@app.command("register-kernel")
def register_kernel():
    """Register Jupyter Kernel"""
    kernel_name = "cifer-kernel"
    display_name = "Cifer Kernel"
    kernel_dir = os.path.expanduser(f"~/.local/share/jupyter/kernels/{kernel_name}")

    if os.path.exists(kernel_dir):
        typer.echo(f"Kernel already exists: {display_name}")
        return

    typer.echo(f"Registering Jupyter kernel: {display_name}")
    try:
        subprocess.run(
            [
                sys.executable, "-m", "ipykernel", "install",
                "--user", "--name", kernel_name,
                "--display-name", display_name
            ],
            check=True
        )
        typer.echo(f"Kernel registered as: {display_name}")
    except Exception as e:
        typer.echo(f"Failed to register kernel: {e}")


# ================= Agent Command =================
@app.command("agent-ace")
def agent_ace(
    port: int = typer.Option(9999, help="Port for agent server"),
):
    """Launch agent ACE server"""
    run_agent_ace(port=port)


# ================= Notebook Command =================
@app.command("download-notebook")
def download_notebook(
    url: str = typer.Option(..., help="URL to download notebook"),
):
    """Download notebook from URL"""
    filename = url.split("/")[-1]
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            typer.echo(f"Notebook downloaded: {filename}")
        else:
            typer.echo(f"Failed to download notebook. Status: {response.status_code}")
    except Exception as e:
        typer.echo(f"Error downloading notebook: {e}")


# ================= Sync Command =================
@app.command("sync")
def sync_folder(
    folder: str = typer.Option(..., help="Folder to simulate syncing"),
):
    """Simulate folder sync"""
    typer.echo(f"Simulating sync of folder '{folder}' to remote server...")


# ================= Training Simulation Command =================
@app.command("train")
def simulate_training(
    epochs: int = typer.Option(5, help="Training epochs"),
    lr: float = typer.Option(0.001, help="Learning rate"),
):
    """Simulate training loop"""
    typer.echo(f"Simulating training... Epochs: {epochs}, Learning Rate: {lr}")
    for i in range(1, epochs + 1):
        typer.echo(f"Epoch {i}/{epochs}... (lr={lr})")
    typer.echo("Training simulation completed.")


# ================= Main Entrypoint =================
def main():
    app()


if __name__ == "__main__":
    main()