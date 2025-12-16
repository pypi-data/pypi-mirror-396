"""
Upload a mesh file from client PC to server host via SSH/SFTP.
Expose both API (upload_mesh) and CLI (neuromeka-upload-mesh).
"""
import argparse
import os
import pathlib
import sys

import paramiko


def upload_mesh(host: str, user: str, port: int = 22, password: str = None, key: str = None, local: str = None, remote: str = None):
    if not local or not remote:
        raise ValueError("local and remote paths are required")
    if not os.path.isfile(local):
        raise FileNotFoundError(f"Local file not found: {local}")
    if password is None and key is None:
        raise ValueError("Either password or key must be provided")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if key:
            ssh.connect(hostname=host, port=port, username=user, key_filename=key)
        else:
            ssh.connect(hostname=host, port=port, username=user, password=password)
        sftp = ssh.open_sftp()
        remote_dir = os.path.dirname(remote)
        if remote_dir:
            # ensure directories exist
            parts = pathlib.Path(remote_dir).parts
            cur = ""
            for p in parts:
                cur = os.path.join(cur, p)
                try:
                    sftp.stat(cur)
                except FileNotFoundError:
                    sftp.mkdir(cur)
        sftp.put(local, remote)
        print(f"Uploaded {local} -> {remote}")
    finally:
        try:
            sftp.close()
        except Exception:
            pass
        ssh.close()


def _parse_args():
    ap = argparse.ArgumentParser(description="Upload mesh file to host via SSH (for FoundationPose docker volume).")
    ap.add_argument("--host", required=True, help="Host IP or name")
    ap.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    ap.add_argument("--user", required=True, help="SSH username")
    auth = ap.add_mutually_exclusive_group(required=True)
    auth.add_argument("--password", help="SSH password")
    auth.add_argument("--key", help="SSH private key path")
    ap.add_argument("--local", required=True, help="Local mesh file path (e.g., mesh/123.stl)")
    ap.add_argument("--remote", required=True, help="Remote host path (mounted into container)")
    return ap.parse_args()


def cli():
    args = _parse_args()
    try:
        upload_mesh(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            key=args.key,
            local=args.local,
            remote=args.remote,
        )
    except Exception as e:
        print(f"Upload failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
