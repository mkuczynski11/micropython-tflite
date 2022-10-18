import picoweb
import uos
import gc

from config import IMAGES_PATH, MODELS_PATH, TMP_MODEL_PATH, MICROSD_DIRECTORY
from utils import get_free_space

# NOTE: None in order to pkg_resources to work
app = picoweb.WebApp(None)

@app.route('/')
def index(req, res):
    yield from picoweb.start_response(res)
    yield from res.awrite(
"""
<h1>Welcome to the esp32_cam classification tool.</h1>
    <ul>
        <li><a href='images'>Images</a></li>
        <li><a href='models'>Models</a></li>
    </ul>
""")

# NOTE: Running this required to change static folder in picoweb sources
#TODO: Add option to download images
@app.route('/images')
def images(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
    
    yield from picoweb.start_response(res)
    if class_name != 'false':
        files_dir = IMAGES_PATH + '/' + model + '/' + class_name
        files = uos.listdir(files_dir)
        html = "<h1>Images for " + model + " class " + class_name + "</h1><h2>Back to <a href=images?model=" + model + ">image " + model + " list</a></h2>"
        yield from res.awrite(html)
        for file in files:
            yield from res.awrite("<a href=image?model=" + model + "&class=" + class_name + "&file=" + file + ">" + file + "</a>" + ": <img src='" + files_dir + '/' + file + "'><br />")
    elif model != 'false':
        class_dirs = IMAGES_PATH + '/' + model
        dirs = uos.listdir(class_dirs)
        html = "<h1>Image " + model + " classes</h1><h2>Back to <a href=images>image models list</a></h2>"
        if dirs:
            html += "<ul>"
        for d in dirs:
            html += "<li><a href=images?model=" + model + "&class=" + d + ">" + d + "</a></li>"
        if dirs:
            html += "</ul>"
        yield from res.awrite(html)
    else:
        models_dirs = IMAGES_PATH
        dirs = uos.listdir(models_dirs)
        html = "<h1>Image models</h1><h2>Back to <a href=/>main page</a></h2>"
        if dirs:
            html += "<ul>"
        for d in dirs:
            html += "<li><a href=images?model=" + d + ">" + d + "</a></li>"
        if dirs:
            html += "</ul>"
        yield from res.awrite(html)
    
@app.route('/image')
def image(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
    file_name = req.form.get('file', 'false')
    
    if model == 'false' or class_name == 'false' or file_name == 'false':
        yield from picoweb.start_response(res, status="400")
        yield from res.awrite("Bad request")
        
    f_path = IMAGES_PATH + '/' + model + '/' + class_name + '/' + file_name
    f = open(f_path, 'rb')
    buf = f.read()
    f.close()
    
    yield from picoweb.start_response(res, "image/jpeg")
    yield from res.awrite(buf)

@app.route('/finish')
def finish_create_model(req, res):
    if req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST request accepted")
    else:
        yield from req.read_form_data()
        try:
            model_name = req.form["modelname"]
            model_width = req.form["modelwidth"]
            model_height = req.form["modelheight"]
            arena_size = req.form["arenasize"]
            
            file_list = uos.listdir(TMP_MODEL_PATH)
            if "labels.txt" not in file_list:
                yield from picoweb.start_response(res, status="400")
                yield from res.awrite("Labels file was not provided. Please use <a href='/models'>Model list</a> to add new model.")
            elif "model.tflite" not in file_list:
                yield from picoweb.start_response(res, status="400")
                yield from res.awrite("Model file was not provided. Please use <a href='/models'>Model list</a> to add new model.")
            elif len(file_list) != 2:
                yield from picoweb.start_response(res, status="507")
                yield from res.awrite("Model couldn't be created because of file system error. Please repeat adding model <a href='/models'>Model list</a>.")
                for file in file_list:
                    uos.remove(TMP_MODEL_PATH + '/' + file)
            else:
                f = open(TMP_MODEL_PATH + '/info.txt', 'w')
                f.write(model_width + '\n')
                f.write(model_height + '\n')
                f.write(arena_size + '\n')
                f.close()
                
                uos.rename(TMP_MODEL_PATH, MODELS_PATH + '/' + model_name)
                uos.mkdir(TMP_MODEL_PATH)
                
                uos.mkdir(IMAGES_PATH + '/' + model_name)
                f = open(MODELS_PATH + '/' + model_name + '/labels.txt')
                lines = f.readlines()
                for line in lines:
                    uos.mkdir(IMAGES_PATH + '/' + model_name + '/' + line.strip())
                f.close()
                
                yield from picoweb.start_response(res, status="201")
                yield from res.awrite("Model created. Back to <a href='/models'>Model list</a>.")
        except KeyError:
            yield from picoweb.start_response(res, status="400")
            yield from res.awrite("Request was not complete. Consider creating model from <a href='/models'>Model list</a>.")

# TODO: Check if user provided data
@app.route('/continue')
def continue_create_model(req, res):
    if req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST request accepted")
    else:
        try:
            yield from req.read_form_byte_data()
            splitter = b'text/plain\r\n\r\n'
            second_splitter = b'\r\n------'
            labels_file = req.data.split(splitter)[1].split(second_splitter)[0]
            
            if len(labels_file) > get_free_space(MICROSD_DIRECTORY):
                yield from picoweb.start_response(res, status="500")
                yield from res.awrite("There is no space left on the device. Consider removing some models in <a href=models>models list</a>")
            else:
                model_path = TMP_MODEL_PATH
                f = open(model_path + '/labels.txt', 'wb')
                f.write(labels_file)
                f.close()
                
                html = "<h1>Labels uploaded. Please provide model details.</h1>"
                html += """
                <form action='finish' method='POST'>
                Model name: <input type='text' name='modelname' />
                Model width: <input type='number' name='modelwidth' />
                Model height: <input type='number' name='modelheight' />
                Arena size: <input type='number' name='arenasize' />
                <input type='submit' />
                </form>
                """
                
                yield from picoweb.start_response(res, status="200")
                yield from res.awrite(html)
        except MemoryError:
            yield from picoweb.start_response(res, status="500")
            yield from res.awrite("Labels file is too big. Make sure that there is no model running and that your model meets requirements. Back to <a>Upload page</a>")

# TODO: ModelManager should clear resources
# TODO: Make user disable any running model
# TODO: Check if user provided data
@app.route('/create')
def create_model(req, res):
    if req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST request accepted")
    else:
        try:
            yield from req.read_form_byte_data()
            splitter = b'application/octet-stream\r\n\r\n'
            second_splitter = b'\r\n------'
            model_file = req.data.split(splitter)[1].split(second_splitter)[0]
            
            if len(model_file) > get_free_space(MICROSD_DIRECTORY):
                yield from picoweb.start_response(res, status="500")
                yield from res.awrite("There is no space left on the device. Consider removing some models in <a href=models>models list</a>")
            else:
                model_path = TMP_MODEL_PATH
                f = open(model_path + '/model.tflite', 'wb')
                f.write(model_file)
                f.close()
                
                html = "<h1>Model uploaded. Please provide labels file.</h1>"
                html += """
                <form action='continue' enctype="multipart/form-data" method='POST'>
                Labels file: <input type='file' accept='.txt' name='labelsfile' />
                <input type='submit' />
                </form>
                """
                
                yield from picoweb.start_response(res, status="200")
                yield from res.awrite(html)
        except MemoryError:
            yield from picoweb.start_response(res, status="500")
            yield from res.awrite("Model is too big to run on this device. Make sure that there is no model running and that your model meets requirements. Back to <a>Upload page</a>")

@app.route('/upload')
def upload_form(req, res):
    html = "<h1>Post new model</h1>"
    html += """
    <form action='create' enctype="multipart/form-data" method='POST'>
    Model file: <input type='file' accept='.tflite' name='modelfile' />
    <input type='submit' />
    </form>
    """
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite(html)
    
# TODO: Create an option to enable/disable active model
@app.route('/models')
def models(req, res):
    html = """
    <head>
    <script>
    function confirmDeleteAction(name) {
        if (window.confirm("Are you sure you want to delete model:" + name + " ?")) {
            var lastIndex = window.location.href.lastIndexOf("/");
            window.location.href = window.location.href.slice(0, lastIndex+1) + "delete?model=" + name;
        }
    }
    </script>
    </head>
    <h1>Models</h1>
    <h2>Back to <a href=/>main page</a></h2>
    """
    html += "<a href=upload> Add new model </a>"
    
    models_dirs = MODELS_PATH
    dirs = uos.listdir(models_dirs)
    if dirs:
        html += "<ul>"
    for d in dirs:
        html += "<li>" + d + "<button onclick='confirmDeleteAction(this.name)' name=" + d + ">Delete</button>" + "</li>"
    if dirs:
        html += "</ul>"
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite(html)

@app.route('/delete')
def delete_model(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    if model == 'false':
        yield from picoweb.start_response(res, status="400")
        yield from res.awrite("Please use <a href=models>Model list</a> to delete models.")
    elif model not in uos.listdir(MODELS_PATH) or model not in uos.listdir(IMAGES_PATH):
        yield from picoweb.start_response(res, status="400")
        yield from res.awrite("Model does not exist.Please use <a href='/models'>Model list</a> to delete models.")
    else:
        for file in uos.listdir(MODELS_PATH + '/' + model):
            uos.remove(MODELS_PATH + '/' + model + '/' + file)
        uos.rmdir(MODELS_PATH + '/' + model)
        for d in uos.listdir(IMAGES_PATH + '/' + model):
            for file in uos.listdir(IMAGES_PATH + '/' + model + '/' + d):
                uos.remove(IMAGES_PATH + '/' + model + '/' + d + '/' + file)
            uos.rmdir(IMAGES_PATH + '/' + model + '/' + d)
        uos.rmdir(IMAGES_PATH + '/' + model)
        
        yield from picoweb.start_response(res, status="200")
        yield from res.awrite("Model successfully deleted. Back to <a href='/models'>Model list</a>")
