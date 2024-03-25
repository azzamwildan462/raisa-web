from flask import Flask, render_template, request, jsonify, redirect, make_response
import os
import re
import mimetypes
import zipfile
import shutil
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, decode_token
import datetime
import socket

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
raisa_ui_assets = os.environ.get('UI_ASSETS')
upload_folder = raisa_ui_assets + "/konten"
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['JWT_SECRET_KEY'] = "The-key-is-very-secret"
jwt = JWTManager(app)

PORT_MONITOR_ATAS = 65530
PORT_MONITOR_BAWAH = 65531

print("Files placed here: ", upload_folder)

#==============================================================================================

def get_first_fit_id(_type):
    first_fit_id = 0

    id_array = []

    # Iterate through all directory in upload_folder and print the name of the directory
    for dir in os.listdir(upload_folder):
        # print(dir)

        # regex the %d_%d_%s format, the %s is contain space bar and other special character
        pattern = r'(\d+)_(\d+)_(.*)$'

        # match the pattern
        match = re.match(pattern, dir)

        konten_type = 0
        konten_id = 0
        konten_name = ''

        # if match is found
        if match:
            konten_type = match.group(1)
            konten_id = match.group(2)
            konten_name = match.group(3)
        
            if int(konten_type) == _type:
                # print(f'konten_type: {konten_type}, konten_id: {konten_id}, konten_name: {konten_name}')
                id_array.append(int(konten_id))
    
    id_array.sort()

    for i in range(len(id_array)):
        if first_fit_id != id_array[i]:
            break
        first_fit_id += 1

    return first_fit_id

def make_a_dir(konten_type, konten_id, konten_name):
    # Create a directory in upload_folder
    new_dir = f'{upload_folder}/{konten_type}_{konten_id}_{konten_name}'
    os.makedirs(new_dir)

    return new_dir

def unknown_to_main(filename):
    pattern = r'(.*)\.(\w+)'
    match = re.findall(pattern, filename)

    if not match:
        return filename
    
    new_file_name = "main." + match[0][1]
    return new_file_name

def get_id_by_name(_type, name):
    id = -1
    name_ret = ''

    for dir in os.listdir(upload_folder):
        pattern = r'(\d+)_(\d+)_(.*)$'
        match = re.match(pattern, dir)

        konten_type = 0
        konten_id = 0
        konten_name = ''

        if match:
            konten_type = match.group(1)
            konten_id = match.group(2)
            konten_name = match.group(3)

            if int(konten_type) == _type and name == konten_name:
                id = int(konten_id)
                name_ret = upload_folder + "/" + dir
                break

    return id, name_ret

def clear_dir(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def remove_content(_type, _name):
    id, name_ret = get_id_by_name(int(_type), _name)

    if id != -1:
        shutil.rmtree(name_ret)
        return True
    else:
        return False

def convert_relative_links_to_absolute(markdown_file, current_dir):
    # Read the content of the Markdown file
    with open(markdown_file, 'r') as file:
        content = file.read()

    # Regular expression pattern to match Markdown links
    pattern = r'\[.*?\]\((.*?)\)'
    pattern_abs = r'\<(.*?)\>'
    pattern_kotak = r'\[(.*?)\]'

    # Function to replace relative links with absolute links
    def replace_links(match):
        original = match.group(0)
        relative_path = match.group(1)
        original_name = ''

        if ':' in relative_path:
            return ""

        result2 = re.match(pattern_abs,relative_path)

        if result2:
            relative_path = result2.group(1)
        
        if os.path.isabs(relative_path):
            return original

        result3 = re.search(pattern_kotak,original)

        if result3:
            original_name = result3.group(1)
        else:
            original_name = os.path.basename(relative_path)

        absolute_path = os.path.join(current_dir, relative_path).replace('\\', '/')
        return '[' + original_name + '](<' + absolute_path + '>)'

    # Replace relative links with absolute links in the content
    new_content = re.sub(pattern, replace_links, content)

    # Write the modified content back to the Markdown file
    with open(markdown_file, 'w') as file:
        file.write(new_content)

def sanitize_markdowns(directory):
    # Iterate over all files and directories in the current directory
    for entry in os.listdir(directory):
        entry_path = os.path.join(directory, entry)
        if os.path.isdir(entry_path):
            # Recursively process subdirectories
            sanitize_markdowns(entry_path)
        elif entry.endswith(".md"):
            # Process Markdown files
            convert_relative_links_to_absolute(entry_path, directory)
            # Create a symbolic link to the main Markdown file
            if entry.endswith("README.md"):
                os.symlink(entry,directory + "/main.md")

def admin_auth(password):
    if password != "awk":
        return False
    
    return True

def verif_jwt_admin(request):
    cookies = request.cookies
    access_token_cookie = request.cookies.get('access_token')
    if not access_token_cookie:
        return False 
    
    try:
        decoded_token = decode_token(access_token_cookie)
        current_user = decoded_token['sub']

        if current_user != "admin":
            return False
        
        return True
    except:
        return False


def send_udp_trigger(message="its"):
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode(), ('127.0.0.1', PORT_MONITOR_ATAS))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock2:
        sock2.sendto(message.encode(), ('127.0.0.1', PORT_MONITOR_BAWAH))

def get_all_contents(type_filter = []):
    contents = []
    for dir in os.listdir(upload_folder):
        pattern = r'(\d+)_(\d+)_(.*)$'
        match = re.match(pattern, dir)

        konten_type = 0
        konten_id = 0
        konten_name = ''

        if match:
            konten_type = match.group(1)
            konten_id = match.group(2)
            konten_name = match.group(3)

            if len(type_filter) == 0:
                if int(konten_type) == 0:
                    contents.append({'name': konten_name, 'type': 'video'})
                elif int(konten_type) == 1:
                    contents.append({'name': konten_name, 'type': 'image'})
                elif int(konten_type) == 9:
                    contents.append({'name': konten_name, 'type': 'markdown'})
            else:
                for i in type_filter:
                    if int(konten_type) == i:
                        if int(konten_type) == 0:
                            contents.append({'name': konten_name, 'type': 'video'})
                        elif int(konten_type) == 1:
                            contents.append({'name': konten_name, 'type': 'image'})
                        elif int(konten_type) == 9:
                            contents.append({'name': konten_name, 'type': 'markdown'})

    return contents

#==================================================================================================

@app.route('/reg_wajah', methods=['GET'])
def reg_wajah():

    return render_template('reg_wajah.html')

@app.route('/hapus_konten_by_name', methods=['GET'])
def hapus_konten_by_name():
    is_verified = verif_jwt_admin(request)
    if not is_verified:
        return redirect('/admin')

    name = ""
    konten_type = 0
    if not 'name' in request.args:
        return 'Name not found'
    
    if not 'type' in request.args:
        return 'Type not found'

    name = request.args['name']
    type_buffer = request.args['type']

    if type_buffer == "video":
        konten_type = 0
    elif type_buffer == "image":
        konten_type = 1
    elif type_buffer == "markdown":
        konten_type = 9
    else:
        return 'Type not found'

    if remove_content(int(konten_type), name):
        send_udp_trigger()
        return redirect('/konten')
    else:
        return redirect('/konten')

@app.route('/')
def index():
    return render_template('index.html')    

@app.route('/konten')
def konten():
    is_verified = verif_jwt_admin(request)
    if not is_verified:
        return redirect('/admin')

    # Get type filter
    type_filter = []
    if 'filt_video' in request.args:
        type_filter.append(0)
    if 'filt_image' in request.args:
        type_filter.append(1)
    if 'filt_md' in request.args:
        type_filter.append(9)

    if not 'filt_video' in request.args and not 'filt_image' in request.args and not 'filt_md' in request.args:
        type_filter = [0,1,9]

    contents = get_all_contents(type_filter)
    return render_template('konten.html', contents=contents)

@app.route('/clear_cookie')
def clear_cookie():
    response = make_response(jsonify({'message': 'JWT token cleared from cookie'}), 200)
    # Set the cookie's value to an empty string
    response = make_response(redirect('/admin'))
    response.set_cookie('access_token', '', expires=0)
    return response

@app.route('/admin',methods=['GET', 'POST'])
def admin():
    is_verified = verif_jwt_admin(request)
    if is_verified:
        return redirect('/konten')

    if request.method == 'POST':
        password = request.form['password']

        ret = admin_auth(password)

        if not ret:
            return render_template('admin.html')
        
        access_token = create_access_token(identity="admin", expires_delta=datetime.timedelta(hours=1))
        response = make_response(redirect('/konten'))
        response.set_cookie('access_token', value=access_token, httponly=True)
        return response

    return render_template('admin.html')

@app.route('/tambah_konten', methods=['GET', 'POST'])
def tambah_konten():
    is_verified = verif_jwt_admin(request)
    if not is_verified:
        return redirect('/admin')

    if request.method == 'POST':
        file = request.files['file']

        # If the user does not select a file, the browser submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        name = request.form['name']
        option = request.form['option']
        image_duration = 0
        konten_type = 0
        konten_type_str = ''

        if option == "is_image":
            konten_type = 1
            image_duration = request.form['image_duration']
            konten_type_str = 'image'
        elif option == "is_video":
            konten_type = 0
            konten_type_str = 'video'
        elif option == "is_md":
            konten_type = 9
            konten_type_str = 'markdown'
        
        # print("Name: ", name)
        # print("Adding file: ", file.filename)
        # print("Image duration: ", image_duration)
        # print("Is image: ", option)



        konten_id, konten_path = get_id_by_name(int(konten_type), name)
        # print("Konten id: ", konten_id)

        return_string = ''
        new_dir = ''
        new_file_name = ''

        if konten_id == -1:
            # Get the first fit id
            first_fit_id = get_first_fit_id(int(konten_type))
            # print("First fit id: ", first_fit_id)

            new_dir = make_a_dir(int(konten_type), first_fit_id, name)
            # print("New dir: ", new_dir)

            new_file_name = unknown_to_main(file.filename)
            # print("New file name: ", new_file_name)

            return_string = 'konten ' + konten_type_str + " " + name + ' berhasil ditambahkan'
        else:
            # print("Konten already exist")
            new_dir = konten_path
            # print("New dir: ", new_dir)

            new_file_name = unknown_to_main(file.filename)
            # print("New file name: ", new_file_name)

            clear_dir(new_dir)

            return_string = 'konten ' + konten_type_str + " " + name + ' berhasil diperbarui'
        
        # Save zip file
        if konten_type == 9 and file.filename.endswith('.zip'):
            # print("ZIP FILE DETECTED")
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(new_dir)
            
            sanitize_markdowns(new_dir)
            send_udp_trigger()
            return 'konten ' + konten_type_str + " " + name + ' berhasil ditambahkan'

        # Save main file
        file.save(os.path.join(new_dir, new_file_name))

        # Save attribut file
        if konten_type == 1:
            with open(new_dir + "/duration_ms.txt", "w") as f:
                f.write(image_duration)
        
        send_udp_trigger()
        return return_string

    return render_template('tambah_konten.html')

@app.route('/hapus_konten', methods=['GET', 'POST'])
def hapus_konten():
    is_verified = verif_jwt_admin(request)
    if not is_verified:
        return redirect('/admin')

    if request.method == 'POST':
        name = request.form['name']
        option = request.form['option']

        konten_type = 0
        konten_type_str = ''

        if option == "is_image":
            konten_type = 1
            konten_type_str = 'image'
        elif option == "is_video":
            konten_type = 0
            konten_type_str = 'video'
        elif option == "is_md":
            konten_type = 9
            konten_type_str = 'markdown'
        else:
            return 'Type not found'
        
        if remove_content(int(konten_type), name):
            send_udp_trigger()
            return 'konten ' + konten_type_str + " " + name + ' berhasil dihapus'
        else:
            return 'konten ' + konten_type_str + " " + name + ' tidak ditemukan'

    return render_template('hapus_konten.html')


#==============================================================================================

if __name__ == '__main__':
    app.run(debug=True)
