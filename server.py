from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
raisa_ui_assets = os.environ.get('UI_ASSETS')
upload_folder = raisa_ui_assets + "/konten"
app.config['UPLOAD_FOLDER'] = upload_folder

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

            print(f'konten_type: {konten_type}, konten_id: {konten_id}, konten_name: {konten_name}')
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

#==================================================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/tambah_konten', methods=['GET', 'POST'])
def tambah_konten():
    if request.method == 'POST':
        file = request.files['file']

        # If the user does not select a file, the browser submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        name = request.form['name']
        option = request.form['option']
        image_duration = 0
        is_image = int(0)

        if option == "is_image":
            is_image = int(1)
            image_duration = request.form['image_duration']
        
        print("Name: ", name)
        print("Adding file: ", file.filename)
        print("Image duration: ", image_duration)
        print("Is image: ", option)

        konten_id, konten_path = get_id_by_name(int(is_image), name)
        print("Konten id: ", konten_id)


        return_string = ''

        if konten_id == -1:
            # Get the first fit id
            first_fit_id = get_first_fit_id(int(is_image))
            print("First fit id: ", first_fit_id)

            new_dir = make_a_dir(int(is_image), first_fit_id, name)
            print("New dir: ", new_dir)

            new_file_name = unknown_to_main(file.filename)
            print("New file name: ", new_file_name)

            file.save(os.path.join(new_dir, new_file_name))

            return_string = 'konten ' + name + ' berhasil ditambahkan'
        else:
            print("Konten already exist")
            new_dir = konten_path
            print("New dir: ", new_dir)

            new_file_name = unknown_to_main(file.filename)
            print("New file name: ", new_file_name)

            clear_dir(new_dir)

            file.save(os.path.join(new_dir, new_file_name))

            return_string = 'konten ' + name + ' berhasil diperbarui'

        return return_string

    return render_template('tambah_konten.html')


#==============================================================================================

if __name__ == '__main__':
    app.run(debug=True)