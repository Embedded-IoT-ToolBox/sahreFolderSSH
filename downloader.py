import os
import paramiko
import time as t
import json
import argparse

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

def download_files_via_ssh(config):
    # Create SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the SSH server
        print("> connecting to SSH server: ", end="")
        ssh_client.connect(hostname=config['hostname'], port=config['port'], username=config['username'], password=config['password'])
    except Exception as e:
        print(f"Error: {e}")
    print("ok")
    try:
        # Create SFTP client
        print("> Creating SFTP client: ", end="")
        sftp_client = ssh_client.open_sftp()
    except Exception as e:
        print(f"Error: {e}")
    print("ok")
    try:
        # Change directory to remote folder
        sftp_client.chdir(config['remote_folder'])
    except Exception as e:
        print(f"Error chdir: {e}")

    while True:
        clear_terminal()  # Clear the terminal screen
        print("> Start checking the files... ")
        try:
            # List files in the remote folder
            files = sftp_client.listdir_attr()

            # Check each file for modification and download if modified
            for file_info in files:
                remote_file_path = os.path.join(config['remote_folder'], file_info.filename)
                local_file_path = os.path.join(config['local_folder'], file_info.filename)

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

        except Exception as e:
            print(f"Error download: {e}")
        t.sleep(0.5)

    # # Close SFTP client
    # sftp_client.close()

    # finally:
    #     # Close SSH client
    #     ssh_client.close()

def find_config_file():
    default_file = 'default.conf'
    if os.path.exists(default_file):
        return default_file

    for file in os.listdir('.'):
        if file.endswith('.conf'):
            return file

    return None

def get_config_file():
    default_file = find_config_file()
    if default_file:
        return default_file
    else:
        print("Error: No configuration file found in the current directory.")
        filename = input("Please enter the path to the configuration file: ")
        return filename

def parse_arguments():
    parser = argparse.ArgumentParser(description='Download files via SSH from a remote server.')
    parser.add_argument('-c', '--config', help='Path to the configuration file')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    return parser.parse_args()

# Example usage
if __name__ == "__main__":
    args = parse_arguments()

    if args.config:
        config_file = args.config
    else:
        config_file = get_config_file()

    config = load_config(config_file)

    download_files_via_ssh(config)
