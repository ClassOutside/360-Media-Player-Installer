#
# Scripts:
# Command to generate EXE (Windows): pyinstaller --onefile --noconsole --icon="./Media/Logo-background.ico" --add-data="Media;Media" installer.py
# Command to generate EXE (MacOS):   pyinstaller --onefile --noconsole --icon="./Media/Logo.icns" --add-data="Media:Media" --name 'installer' installer.py

import subprocess
import tkinter as tk
from tkinter import messagebox
import os
import platform
from PIL import Image, ImageTk
import sys
if platform.system() == 'Windows':
    from OpenSSL import crypto
from secrets import randbelow
import time
import ctypes

isNvmInstalled = False  # Initialize isNvmInstalled to False
isNodeInstalled = False
mediaProviderString = "360_Media_Provider"
mediaPlayerString = "360_Media_Player"
windowsName = "Windows"
macOSName = "Darwin"
os_type = platform.system()
defaultBackgroundColor = "#1F1B24"
defaultTextColor = "white"
defaultFontAndSize = ("Arial", 16)
headingFontAndSize = ("Arial", 36)
buttonFontAndSize = ("Arial", 12)
isInstallComplete = False

if getattr(sys, "frozen", False):
    icon_path = os.path.join(sys._MEIPASS, "Media/Logo-background.ico")
    logo_path = os.path.join(sys._MEIPASS, "./Media/Logo.png")
else:
    icon_path = "Media/Logo-background.ico"
    logo_path = "./Media/Logo.png"


def install_nvm_Windows():
    global nvmInstalled  # Use the global flag

    installing_text.insert(tk.END, "Installing NVM for Windows...\n")
    root.update_idletasks()
    try:
        # Use the curl command to download NVM-Setup
        subprocess.run(["curl.exe", "-L", "-o", "nvm-setup.exe",
                       "https://github.com/coreybutler/nvm-windows/releases/download/1.1.11/nvm-setup.exe"], check=True, shell=True)

        # Run the installer and check the return code
        nvm_installer = subprocess.Popen("nvm-setup.exe", shell=True)
        return_code = nvm_installer.wait()

        if return_code != 0:
            print("Return code 0 for nvm installation")
        else:
            print("Return code not 0")

        install_complete(
            "NVM for Windows has been installed. Restart Required. Please run the installer again.")

        custom_message_box(
            "Restart Required", "The installer needs a restart. Please run the installer again.")

        nvmInstalled = True  # Set the flag to indicate NVM is installed
    except subprocess.CalledProcessError as e:
        install_complete(f"Failed to download NVM for Windows: {e}")


def install_node_version_Windows(node_version):
    installing_text.insert(tk.END, f"Installing Node.js {node_version}...\n")
    root.update_idletasks()
    try:
        # Use NVM to install the specified Node.js version
        subprocess.run(["nvm",
                       "install", node_version], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        install_complete(f"Node.js {node_version} has been installed.")
    except subprocess.CalledProcessError as e:
        install_complete(f"Failed to install Node.js {node_version}: {e}")


def install_nvm_MacOS():
    # Setup the expected path for .zshrc file
    home_directory = os.path.expanduser("~")
    zshrc_path = os.path.join(home_directory, ".zshrc")

    # Run the 'touch' command to create the .zshrc file
    subprocess.run(["touch", zshrc_path])

    # Install nvm using the curl command
    nvm_install_command = "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash"
    install_output = subprocess.getoutput(nvm_install_command)


def install_node_version_MacOS(node_version):
    installing_text.insert(tk.END, f"Installing Node.js {node_version}...\n")
    root.update_idletasks()
    try:
        # Use NVM to install the specified Node.js version
        result = subprocess.run(
            f'source ~/.nvm/nvm.sh && nvm install {node_version}', shell=True, executable='/bin/zsh', capture_output=True, text=True)
        print(result.stdout)
        install_complete(f"Node.js {node_version} has been installed.")
    except subprocess.CalledProcessError as e:
        install_complete(f"Failed to install Node.js {node_version}: {e}")


def install_complete(message):
    installing_text.insert(tk.END, message + "\n")


def execute_in_directory(directoryName, functionToExecute, *args):
    original_directory = os.getcwd()

    if not os.path.exists(directoryName):
        os.chdir("..")

    while os.path.exists(directoryName):
        os.chdir(directoryName)

    functionToExecute(*args)

    os.chdir(original_directory)


def change_and_install_Windows(directory_name):
    installing_text.insert(
        tk.END, f"Entered {directory_name}.\n")
    root.update_idletasks()

    try:
        result = subprocess.run(
            ["node", "-e",
                "const { execSync } = require('child_process'); console.log(execSync('npm install').toString());"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # Print the output and error messages
        print("Output:", result.stdout)
        print("Error:", result.stderr)
        install_complete(
            f"npm install in {directory_name} folder(s) completed.")
    except subprocess.CalledProcessError as e:
        print("Failedto run ")
        install_complete(f"Failed to run npm install in {directory_name}: {e}")


def setup_keys():
    # Check for the "Keys" directory and enter it
    if os.path.exists("Keys"):
        os.chdir("Keys")
        installing_text.insert(tk.END, "Entered the 'Keys' folder.\n")
        root.update_idletasks()

        # Call the setup_openSSL_Keys function to create server.cert and server.key
        if (os_type == windowsName):
            setup_openSSL_Keys_Windows()
        elif (os_type == macOSName):
            setup_openSSL_Keys_MacOS()

        installing_text.insert(
            tk.END, f"Returned to the original directory.\n")
        root.update_idletasks()
    else:
        installing_text.insert(
            tk.END, f"Returned to the original directory.\n")
        root.update_idletasks()


def setup_openSSL_Keys_MacOS():
    # Use OpenSSL to create server.cert and server.key
    try:
        subprocess.run(["openssl", "req", "-new", "-newkey", "rsa:2048", "-days", "365",
                        "-nodes", "-x509", "-keyout", "server.key", "-out", "server.cert",
                        "-subj", "/C=US/ST=New York/L=New York City/O=Your Organization/OU=Your Org Unit/CN=example.com/emailAddress=youremail@example.com"], check=True)
        install_complete("Created server.cert and server.key with OpenSSL.")
    except subprocess.CalledProcessError as e:
        install_complete(f"Failed to create server.cert and server.key: {e}")


def setup_openSSL_Keys_Windows():
    # Create a key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create a self-signed certificate valid for 100 years
    cert = crypto.X509()
    # If any two seriel numbers match the certificate will not be accepted
    cert.set_serial_number(randbelow(2**64))
    cert.get_subject().CN = "example.com"
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(2147483647)  # Valid for 100 years

    cert.sign(key, 'sha256')

    # Save the private key to a file
    with open("server.key", "wb") as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    # Save the certificate to a file
    with open("server.cert", "wb") as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))


def change_and_install_MacOS(directory_name):
    # Display the entered folder message
    installing_text.insert(
        tk.END, f"Entered {directory_name}.\n")
    root.update_idletasks()

    print("Installing npm in this dir: " + os.getcwd())

    try:
        result = subprocess.run('source ~/.nvm/nvm.sh && npm install',
                                shell=True, executable='/bin/zsh', capture_output=True, text=True)
        print(f"HERE: {result.stdout}")
        install_complete(
            f"npm install in {directory_name} folder(s) completed.")
    except subprocess.CalledProcessError as e:
        install_complete(f"Failed to run npm install in {directory_name}: {e}")


def check_nvm_installed_MacOS():
    try:
        result = subprocess.run('source ~/.nvm/nvm.sh && nvm --version',
                                shell=True, executable='/bin/zsh', capture_output=True, text=True)
        nvm_output = result.stdout.strip()
        print(nvm_output)
        return nvm_output
    except:
        print("NVM is not installed")
        return False


def check_nvm_installed_Windows():
    if os.system("nvm --version") != 0:
        return False
    else:
        return True


def check_node_installed_Windows():
    node_version_check = subprocess.run(
        ["nvm", "list"],
        stdout=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    print("Output of node version check:")
    print(node_version_check.stdout)
    if "18.18.2" not in node_version_check.stdout:
        return False
    else:
        return True


def check_node_installed_MacOS():
    result = subprocess.run('source ~/.nvm/nvm.sh && nvm list', shell=True,
                            executable='/bin/zsh', capture_output=True, text=True)
    nvm_output = result.stdout.strip()
    if "18.18.2" not in nvm_output:
        return False
    else:
        return True


def use_node_version_Windows():
    try:
        subprocess.run(["nvm",
                       "use", "18.18.2"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # Needed to pause so that the node version is set before its used in later methods.
        time.sleep(1)
    except subprocess.CalledProcessError as e:
        install_complete(f"Failed to set Node.js version to 18.18.2: {e}")


def use_node_version_MacOS():
    try:
        subprocess.run('source ~/.nvm/nvm.sh && nvm use 18.18.2', shell=True,
                       executable='/bin/zsh', capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        install_complete(f"Failed to set Node.js version to 18.18.2: {e}")


def perform_installation():
    global isNvmInstalled, isNodeInstalled, os_type, isInstallComplete

    # Clear any previous installation status
    installing_text.delete(1.0, tk.END)

    if (os_type == windowsName):
        perform_installation_Windows()
    elif (os_type == macOSName):
        perform_installation_MacOS()

    if (isInstallComplete):
        # Show a popup message with "Installation complete"
        custom_message_box("Installation Complete",
                           "Installation is complete.")


def custom_message_box(title, message):
    custom_box = tk.Toplevel(root, background=defaultBackgroundColor)
    custom_box.title(title)
    custom_box.iconbitmap(icon_path)

    label = tk.Label(custom_box, text=message, bg=defaultBackgroundColor,
                     fg=defaultTextColor, font=defaultFontAndSize)
    label.pack(padx=10, pady=10)

    ok_button = tk.Button(custom_box, text="OK", command=closeApplication)
    ok_button.pack(pady=10)


def closeApplication():
    root.destroy()


def perform_installation_Windows():
    global isNvmInstalled, isNodeInstalled, os_type, isInstallComplete

    isNvmInstalled = check_nvm_installed_Windows()

    if not isNvmInstalled:
        response = messagebox.askyesno(
            "NVM Installation", "NVM is not installed. Do you want to install it?")
        if response:
            install_nvm_Windows()
    elif isNvmInstalled:
        isNodeInstalled = check_node_installed_Windows()
        print("isNode: " + str(isNodeInstalled))
        if not isNodeInstalled:
            response = messagebox.askyesno(
                "Node.js Installation", "Node.js version 18.18.2 is not installed. Do you want to install it?")
            if response:
                install_node_version_Windows("18.18.2")

        isNodeInstalled = use_node_version_Windows()

        execute_in_directory(mediaProviderString, change_and_install_Windows,
                             mediaProviderString)
        execute_in_directory(mediaProviderString, setup_keys)
        execute_in_directory(mediaPlayerString, change_and_install_Windows,
                             mediaPlayerString)
        execute_in_directory(mediaPlayerString, setup_keys)
        isInstallComplete = True


def perform_installation_MacOS():
    global isNvmInstalled, isNodeInstalled, os_type, isInstallComplete

    # Needed because mac defaults to current user dir
    current_directory = os.path.dirname(sys.executable) if getattr(
        sys, 'frozen', False) else os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_directory)

    isNvmInstalled = check_nvm_installed_MacOS()

    if not isNvmInstalled:
        response = messagebox.askyesno(
            "NVM Installation", "NVM is not installed. Do you want to install it?")
        if response:
            install_nvm_MacOS()

    isNodeInstalled = check_node_installed_MacOS()

    if not isNodeInstalled:
        response = messagebox.askyesno(
            "Node.js Installation", "Node.js version 18.18.2 is not installed. Do you want to install it?")
        if response:
            install_node_version_MacOS("18.18.2")

    isNodeInstalled = use_node_version_MacOS()

    execute_in_directory(mediaProviderString,
                         change_and_install_MacOS, mediaProviderString)
    execute_in_directory(mediaProviderString, setup_keys)
    execute_in_directory(mediaPlayerString,
                         change_and_install_MacOS, mediaPlayerString)
    execute_in_directory(mediaPlayerString, setup_keys)
    isInstallComplete = True


# Create the main window
root = tk.Tk()
root.title("360 Media Player Installation")
root.eval("tk::PlaceWindow . center")
root.iconbitmap(icon_path)

# Set a minimum size for the root window to make it larger by default
root.minsize(400, 200)
root.configure(bg=defaultBackgroundColor)

# Create a container frame for the first page
page1_container = tk.Frame(root, bg=defaultBackgroundColor)
page1_container.grid(row=0, column=0, sticky="nsew")

# Create the first page frame within the container
page1 = tk.Frame(page1_container, bg=defaultBackgroundColor)
page1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Directory Selector with text and "Browse" button in the center
headerFrame = tk.Frame(page1, bg=defaultBackgroundColor)
headerFrame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

# Load the image
original_image = Image.open(logo_path)
resized_image = original_image.resize((100, 100), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_image)

# Display the image at the top left
logo_label = tk.Label(headerFrame, image=logo_image, bg=defaultBackgroundColor)
logo_label.grid(row=0, column=0, sticky="nw")

# Label (centered)
heading_label = tk.Label(headerFrame, text="360 Media Player Installer",
                         bg=defaultBackgroundColor, fg=defaultTextColor, font=headingFontAndSize)
heading_label.grid(row=0, column=1, padx=10, pady=20, sticky="n")

processLogFrame = tk.Frame(page1, bg=defaultBackgroundColor)
processLogFrame.grid(row=1, column=0, columnspan=2, pady=28, sticky="n")

# Create a label for the list of dependencies
dependency_label = tk.Label(
    processLogFrame, text="The following are some dependencies that will be installed:", font=defaultFontAndSize, bg=defaultBackgroundColor, fg=defaultTextColor, anchor='w')  # Set anchor to 'w' for left alignment
# Add sticky to anchor it to the west (left)
dependency_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

# Create a bulleted list
bulleted_list = tk.Label(
    processLogFrame, text="- Node Version Manager (NVM)\n- Node.JS\n", justify='left', font=defaultFontAndSize, bg=defaultBackgroundColor, fg=defaultTextColor, anchor='w')  # Set anchor to 'w' for left alignment
# Add sticky to anchor it to the west (left)
bulleted_list.grid(row=2, column=0, padx=(0, 10), sticky="w")

# Create a label for the installation status
installing_label = tk.Label(
    processLogFrame, text="Installation Status", font=defaultFontAndSize, bg=defaultBackgroundColor, fg=defaultTextColor, anchor='w')  # Set anchor to 'w' for left alignment
# Add sticky to anchor it to the west (left)
installing_label.grid(row=3, column=0, padx=(0, 10), sticky="w")

# Create a Text widget for displaying the installation progress
installing_text = tk.Text(processLogFrame, height=6, width=40,
                          font=defaultFontAndSize, bg=defaultBackgroundColor, fg=defaultTextColor, wrap='word', insertofftime=1000)
# Add sticky to anchor it to the west (left)
installing_text.grid(row=4, column=0, padx=(0, 10), sticky="w")

# Create buttons for "Install" and "Cancel" aligned horizontally
button_frame = tk.Frame(page1, bg=defaultBackgroundColor)
button_frame.grid(row=2, column=0, columnspan=2, pady=28, sticky="n")

cancel_button = tk.Button(button_frame, text="Cancel",
                          command=root.quit, font=defaultFontAndSize)
cancel_button.grid(row=0, column=0, padx=(0, 80))

install_button = tk.Button(
    button_frame, text="Install", command=perform_installation, font=defaultFontAndSize)
install_button.grid(row=0, column=1, padx=(0, 80))

root.mainloop()
