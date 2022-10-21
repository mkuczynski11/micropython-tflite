import picoweb
import uos
import gc

from config import (
    IMAGES_PATH, MODELS_PATH, TMP_MODEL_PATH,
    TMP_LABELS_PATH, TMP_INFO_PATH, TMP_MODEL_PATH_DIR,
    MICROSD_DIRECTORY, MAX_MODEL_RAM_USAGE,
    IMAGES_ON_PAGE, BUFFER_SIZE, MODEL_REQUEST_END_LEGTH,
    FILE_STREAM_SPLITTER, TEXT_SPLITTER, BYTE_CONTENT_END_SPLITTER)
from utils import get_free_space, get_file_size
from model import ModelManager
from app_manager import AppManager

# NOTE: None in order to pkg_resources to work
app = picoweb.WebApp(None)

# NOTE: For debug purposes
@app.route('/predict')
def predict(req, res):
    model_manager = ModelManager()
    model_manager.predict_scenario()
    
    yield from picoweb.start_response(res)
    yield from res.awrite("Predict ended. ")

@app.route('/')
def index(req, res):
    yield from picoweb.start_response(res)
    yield from res.awrite(
"""
<h1>Welcome to the esp32_cam classification tool.</h1>
    <ul>
        <li><a href='images'>Images</a></li>
        <li><a href='models'>Models</a></li>
        DEBUG:<a href='predict'>Predict</a>
    </ul>
""")
        
async def show_models_for_images(res):
    dirs = uos.listdir(IMAGES_PATH)
    html = """
            <h1>Image models</h1>
            <h2><a href=/>Main page</a></h2>
            """
    if dirs:
        html += "<ul>"
        
    for d in dirs:
        html += f'<li><a href=images?model={d}>{d}</a></li>'
    
    if dirs:
        html += "</ul>"
        
    yield from res.awrite(html)
    
async def show_classes(res, model):
    class_dirs = IMAGES_PATH + '/' + model
    dirs = uos.listdir(class_dirs)
    
    html = f'<h1>Classes for {model}</h1>'
    html += "<h2><a href=images>Image models</a></h2>"
    
    if dirs:
        html += "<ul>"
        
    for d in dirs:
        html += f'<li><a href=images?model={model}&class={d}&page=1>{d}</a></li>'
    
    if dirs:
        html += "</ul>"
    yield from res.awrite(html)

async def show_images(res, model, class_name, page):
    files_dir = IMAGES_PATH + '/' + model + '/' + class_name
    files = uos.listdir(files_dir)
    
    html = f'<h1>Images for {model} class {class_name}</h1>'
    html += f'<h2>Back to <a href=images?model={model}>Classes for {model}</a></h2>'
    if page > 1:
        html += f'<h2><a href=images?model={model}&class={class_name}&page={page-1}>Previous page</a></h2>'
    if page*IMAGES_ON_PAGE < len(files):
        html += f'<h2><a href=images?model={model}&class={class_name}&page={page+1}>Next page</a></h2>'
    yield from res.awrite(html)
    
    starting_index = (page - 1)*IMAGES_ON_PAGE
    for i in range(min(IMAGES_ON_PAGE, len(files) - (page - 1)*IMAGES_ON_PAGE)):
        file = files[starting_index + i]
        yield from res.awrite(f'<a href=image?model={model}&class={class_name}&file={file}>{file}</a>: <img src="{files_dir + '/' + file}"><br />')

# NOTE: Running this required to change static folder in picoweb sources
# TODO: Add option to download images
# TODO: Create option to view only file list
@app.route('/images')
def images(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
    page = req.form.get('page', 'false')
    
    yield from picoweb.start_response(res)
    
    if class_name != 'false':
        if page == 'false':
            page = 1
        else:
            page = int(page)
        yield from show_images(res, model, class_name, page)
    elif model != 'false':
        yield from show_classes(res, model)
    else:
        yield from show_models_for_images(res)
    
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

# TODO: Find out how to validate arena size
def validate_required_memory(model_width, model_height):
    return 800_000
#     # Memory left for arena size = max_usage - (model_size + image input size)
#     arena_size_memory = MAX_MODEL_RAM_USAGE - (get_file_size(TMP_MODEL_PATH) + (model_width * model_height * 3))
# 
#     model = bytearray(get_file_size(TMP_MODEL_PATH))
#     file = open(TMP_MODEL_PATH, 'rb')
#     file.readinto(model)
#     file.close()
# 
#     interpreter = microlite.interpreter(model, arena_size_memory, None, None)

def write_model_info_to_file(model_width, model_height, arena_size):
    f = open(TMP_INFO_PATH, 'a')
    f.write(model_width + '\n')
    f.write(model_height + '\n')
    f.write(str(arena_size) + '\n')
    f.close()

@app.route('/finish')
def finish_create_model(req, res):
    if req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST request accepted. Back to <a href='/upload'>Upload page</a>")
        return
    
    app_manager = AppManager()
    
    yield from req.read_form_data()
    try:
        model_name = req.form["modelname"]
        model_width = req.form["modelwidth"]
        model_height = req.form["modelheight"]
    except KeyError:
        yield from picoweb.start_response(res, status="400")
        yield from res.awrite("Request was not complete. Consider creating model from <a href='/upload'>Upload page</a>.")
        return
        
    if not app_manager.is_able_to_create_model():
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="409")
        yield from res.awrite("Please use <a href='/upload'>Upload page</a> to add new model.")
        return
    
    arena_size = validate_required_memory(model_width, model_height)
    
    if arena_size == 0:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="409")
        yield from res.awrite("Uploaded model requires too much space to run and cannot be run on this device. Please consider uploading other models.")
    
    write_model_info_to_file(model_width, model_height, arena_size)
    
    app_manager.move_model_from_tmp_folder(model_name)
    
    yield from picoweb.start_response(res, status="201")
    yield from res.awrite("Model created. Back to <a href='/models'>Model list</a>.")

async def read_labels_byte_data_to_file(req):
    size = int(req.headers[b"Content-Length"])
    yield from req.read_form_byte_data(size)
    labels_file = req.data.split(TEXT_SPLITTER)[1].split(BYTE_CONTENT_END_SPLITTER)[0]
    
    if len(labels_file) > get_free_space(MICROSD_DIRECTORY):
        return False
    
    f = open(TMP_LABELS_PATH, 'wb')
    f.write(labels_file)
    f.close()
    
    return True

@app.route('/continue')
def continue_create_model(req, res):
    app_manager = AppManager()
    
    if req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST request accepted. Back to <a href='/upload'>Upload page</a>")
        return
    elif app_manager.model_passed == False:
        yield from picoweb.start_response(res, status="409")
        yield from res.awrite("Please usse <a href='/upload'>Upload page</a> to add new model.")
        return
    
    ok = yield from read_labels_byte_data_to_file(req)
    
    if not ok:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="500")
        yield from res.awrite("There is no space left on the device. Consider removing some models in <a href=models>models list</a>")
        return
    
    app_manager.labels_passed = True
    
    html = """
    <h1>Labels uploaded. Please provide model details.</h1>
    <form action='finish' method='POST'>
    Model name: <input type='text' name='modelname' />
    Model width: <input type='number' name='modelwidth' />
    Model height: <input type='number' name='modelheight' />
    <input type='submit' />
    </form>
    """
    
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite(html)

async def read_model_byte_data_to_file(req):
    f = open(TMP_MODEL_PATH, 'wb')
    final_index = int(req.headers[b"Content-Length"]) - MODEL_REQUEST_END_LEGTH
    print(f'Will read {str(final_index // BUFFER_SIZE)} buffers with size {str(BUFFER_SIZE)}')
    for i in range(0, final_index, BUFFER_SIZE):
        if (i + BUFFER_SIZE) > final_index:
            print(f'Reading last {str(final_index % BUFFER_SIZE)} bytes')
            yield from req.read_form_byte_data(final_index % BUFFER_SIZE)
        else:
            print(f'Reading {str(i // BUFFER_SIZE + 1)} buffer')
            yield from req.read_form_byte_data(BUFFER_SIZE)
            
        if i == 0:
            req.data = req.data.split(FILE_STREAM_SPLITTER)[1]
            
        if len(req.data) > get_free_space(MICROSD_DIRECTORY):
            return False
        
        f.write(req.data)

    yield from req.read_form_byte_data(MODEL_REQUEST_END_LEGTH)
    print("Read file")
    f.close()
    return True

def write_model_size_to_file():
    f = open(TMP_INFO_PATH, 'w')
    model_size = get_file_size(TMP_MODEL_PATH)
    f.write(str(model_size))
    f.close()

@app.route('/create')
def create_model(req, res):
    if req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST request accepted. Back to <a href='/upload'>Upload page</a>")
        return
    elif int(req.headers[b"Content-Length"]) > MAX_MODEL_RAM_USAGE:
        yield from picoweb.start_response(res, status="409")
        yield from res.awrite(f'Model is too big. Maximum size of {MAX_MODEL_RAM_USAGE} bytes for the whole model is allowed. Back to <a href="/upload">Upload page</a>')
        return
    
    app_manager = AppManager()
    app_manager.reset_model_creation()
    
    ok = yield from read_model_byte_data_to_file(req)
    
    if not ok:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="500")
        yield from res.awrite("There is no space left on the device. Consider removing some models in <a href=models>models list</a>")
        return
    
    write_model_size_to_file()
    
    app_manager.model_passed = True
        
    html = """
    <h1>Model uploaded. Please provide labels file.</h1>
    <form action='continue' enctype="multipart/form-data" method='POST'>
    Labels file: <input type='file' accept='.txt' name='labelsfile' />
    <input type='submit' />
    </form>
    """
    
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite(html)
    
@app.route('/upload')
def upload_form(req, res):
    html = """
    <h1>Add new model</h1>
    <form action='create' enctype="multipart/form-data" method='POST'>
    Model file: <input type='file' accept='.tflite' name='modelfile' />
    <input type='submit' />
    </form>
    """
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite(html)
    
@app.route('/change')
def change_model(req, res):
    if req.method == "GET":
        html = """
        <h1>Change active model</h1>
        <form action='change' method='POST'>
        <label for='models'>Choose model:</label>
        <select id='models' name='models' size=5>
        """
        
        model_list = uos.listdir(MODELS_PATH)
        
        for model in model_list:
            html += f'<option value="{model}">{model}</option>'
    
        html += """
        <input type='submit' />
        </form>
        """
        yield from picoweb.start_response(res, status="200")
        yield from res.awrite(html)
    elif req.method == "POST":
        yield from req.read_form_data()
        try:
            model_name = req.form["models"]
        except KeyError:
            yield from picoweb.start_response(res, status="400")
            yield from res.awrite("Request was not complete. Consider changing active model from <a href='/change'>Change page</a>.")
            return
            
        model_manager = ModelManager()
        model_manager.load_from_path(MODELS_PATH + '/' + model_name)
        
        yield from picoweb.start_response(res, status="200")
        yield from res.awrite(f'Successfully changed model to {model_name}. Back to <a href="/models">Model list</a>')
    else:
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST and GET request accepted. Back to <a href='/models'>Model list</a>")
    
# DEV: All paths work    
@app.route('/unload')
def unload(req, res):
    model_manager = ModelManager()
    model_manager.unload_model()
    
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite("Model unloaded. Back to <a href='/models'>Model list</a>")

async def show_models(res):
    dirs = uos.listdir(MODELS_PATH)
    html = ""
    if dirs:
        html += "<ul>"
        
    for d in dirs:
        html += f'<li>{d}<button onclick="confirmDeleteAction(this.name)" name={d}>Delete</button></li>'
    
    if dirs:
        html += "</ul>"
        
    yield from res.awrite(html)

# DEV: All paths work
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
    
    model_manager = ModelManager()
    active_model = model_manager.active_model_name
    
    if active_model == None:
        html+= "<h2>No active model. Pick one to enable classification.</h2>"
    else:
        html += f'<h2>Currently active model is {active_model}</h2>'
    
    html += "<a href=upload> Add new model </a><br />"
    html += "<a href=change> Change active model</a><br />"
    html += "<a href=unload> Unload active model</a><br />"
    
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite(html)
    
    yield from show_models(res)

# DEV: All paths work
@app.route('/delete')
def delete_model(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    if model == 'false':
        yield from picoweb.start_response(res, status="400")
        yield from res.awrite("Please use <a href=models>Model list</a> to delete models.")
        return
    elif model not in uos.listdir(MODELS_PATH) or model not in uos.listdir(IMAGES_PATH):
        yield from picoweb.start_response(res, status="400")
        yield from res.awrite("Model does not exist.Please use <a href='/models'>Model list</a> to delete models.")
        return
    
    app_manager = AppManager()
    app_manager.remove_model(model)
    
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite("Model successfully deleted. Back to <a href='/models'>Model list</a>")
