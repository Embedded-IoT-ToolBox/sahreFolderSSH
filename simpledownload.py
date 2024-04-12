import os
import paramiko
import time as t

def download_files_via_ssh(hostname, port, username, password, remote_folder, local_folder):
    # Create SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the SSH server
        print("> connecting to SSH server: ",end="")
        ssh_client.connect(hostname=hostname, port=port, username=username, password=password)
    except Exception as e:
        print(f"Error: {e}")
    print("ok")
    try:
        # Create SFTP client
        print("> Creating SFTP client: ",end="")
        sftp_client = ssh_client.open_sftp()
    except Exception as e:
        print(f"Error: {e}")
    print("ok")
    try:
        # Change directory to remote folder
        sftp_client.chdir(remote_folder)
    except Exception as e:
        print(f"Error chdir: {e}")

    print("> Start checking the files... ")
    while True:
        try:
            # List files in the remote folder
            files = sftp_client.listdir_attr()

            # Check each file for modification and download if modified
            for file_info in files:
                remote_file_path = os.path.join(remote_folder, file_info.filename)
                local_file_path = os.path.join(local_folder, file_info.filename)

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

# Example usage
if __name__ == "__main__":
    hostname = "192.168.2.169"
    port = 22  # Default SSH port
    username = "havar"
    password = "123"  # Enter your password here
    # remote_folder = "~/repositories/vx-firmware/build-lynx-mp1/bin"
    remote_folder = f"/home/{username}/repositories/vx-firmware/build-lynx-mp1/bin"
    local_folder = "../../repositories/bin"  # Change this to your local folder path

    download_files_via_ssh(hostname, port, username, password, remote_folder, local_folder)
        

