import os
import paramiko

def download_files_via_ssh(hostname, port, username, password, remote_folder, local_folder):
    # Create SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the SSH server
        ssh_client.connect(hostname=hostname, port=port, username=username, password=password)

        # Create SFTP client
        sftp_client = ssh_client.open_sftp()

        # Change directory to remote folder
        sftp_client.chdir(remote_folder)

        # List files in the remote folder
        files = sftp_client.listdir()

        # Download each file
        for file_name in files:
            remote_file_path = os.path.join(remote_folder, file_name)
            local_file_path = os.path.join(local_folder, file_name)
            sftp_client.get(remote_file_path, local_file_path)
            print(f"Downloaded: {file_name}")

        # Close SFTP client
        sftp_client.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close SSH client
        ssh_client.close()

# Example usage
if __name__ == "__main__":
    hostname = "192.168.2.169"
    port = 22  # Default SSH port
    username = "havar"
    password = "123"  # Enter your password here
    remote_folder = "~/repositories/vx-firmware/build-lynx-mp1/bin"
    local_folder = "/"  # Change this to your local folder path

    download_files_via_ssh(hostname, port, username, password, remote_folder, local_folder)

