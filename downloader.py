#!/usr/bin/env python3
import os
import paramiko
import time as t
import json
import argparse
import sys

def clear_terminal():
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For Unix/Linux/MacOS
    else:
        _ = os.system('clear')

def load_config(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def download_files_via_ssh(master_node, nodes):
    while True:
        clear_terminal()  # Clear the terminal screen
        print("> Start checking the files... ")
        for node in nodes:
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                # Connect to the SSH server
                print(f"> Connecting to SSH server ({node['ip']}): ", end="")
                ssh_client.connect(hostname=node['ip'], port=node['port'], username=node['username'], password=node['password'])
                print("OK")

                # Create SFTP client
                sftp_client = ssh_client.open_sftp()

                # Change directory to remote folder
                sftp_client.chdir(node['directory'])

                # List files in the remote folder
                files = sftp_client.listdir_attr()

                # Check each file for modification and download if modified
                for file_info in files:
                    remote_file_path = os.path.join(node['directory'], file_info.filename)
                    local_file_path = os.path.join(master_node['directory'], file_info.filename)

                    # Check if the file is a .hex file
                    if file_info.filename.endswith('.hex'):

                        # Check if local file exists
                        if os.path.exists(local_file_path):
                            # Get modification time of local file
                            local_mtime = os.path.getmtime(local_file_path)

                            # Get modification time of remote file
                            remote_mtime = file_info.st_mtime

                            # Compare modification times
                            if local_mtime < remote_mtime:
                                # Download file if remote file is newer
                                sftp_client.get(remote_file_path, local_file_path)
                                print(f"Downloaded: {file_info.filename}")
                        else:
                            # Download file if local file doesn't exist
                            sftp_client.get(remote_file_path, local_file_path)
                            print(f"Downloaded: {file_info.filename}")

                # Close SFTP client
                sftp_client.close()

                # Close SSH client
                ssh_client.close()

            except Exception as e:
                print(f"Error: {e}")

            t.sleep(0.5)

def find_config_file():
    config_file = 'nodes.conf'
    if os.path.exists(config_file):
        return config_file

    for file in os.listdir('.'):
        if file.endswith('.conf'):
            return file

    return None

def check_config_file(filename):
    try:
        with open(filename, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False

def get_config_file():
    config_file = find_config_file()
    if config_file:
        return config_file
    else:
        print("Error: No configuration file found in the current directory.")
        sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Download files via SSH from remote servers.')
    parser.add_argument('-c', '--config', help='Path to the configuration file')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    if args.config:
        if not check_config_file(args.config):
            print("Error: The provided configuration file is not valid or does not exist.")
            sys.exit(1)

    return args

# Example usage
if __name__ == "__main__":
    args = parse_arguments()

    config_file = args.config if args.config else get_config_file()
    config = load_config(config_file)

    master_node = config['master']

    download_files_via_ssh(master_node, config['nodes'])
