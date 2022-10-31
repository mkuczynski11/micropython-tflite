import picoweb

from config import (
    IMAGES_ON_PAGE, BUFFER_SIZE, MODEL_REQUEST_END_LEGTH,
    FILE_STREAM_SPLITTER, TEXT_SPLITTER, BYTE_CONTENT_END_SPLITTER)
from model import ModelManager
from app_manager import AppManager, ResponseCode

# NOTE: None in order to pkg_resources to work
app = picoweb.WebApp(None)

# NOTE: For debug purposes
# TODO: Remove when not needed
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
    
@app.route('/delete_images')
def delete_images(req, res):
    app_manager = AppManager()
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
    if class_name != 'false' and model != 'false':
        code = app_manager.remove_images_for_class(model, class_name)
        if code != ResponseCode.OK:
            yield from picoweb.start_response(res, status="400")
            yield from res.awrite(f'{code}.Back to <a href=images>Images</a>')
            return
    elif model != 'false':
        code = app_manager.remove_images_for_model(model)
        if code != ResponseCode.OK:
            yield from picoweb.start_response(res, status="400")
            yield from res.awrite(f'{code}.Back to <a href=images>Images</a>')
            return
    
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite("Images successfully deleted. Back to <a href='/images'>Images list</a>")
        
async def show_models_for_images(res):
    html = """
    <head>
    <script>
    function confirmDeleteAction(name) {
        if (window.confirm("Are you sure you want to delete images for:" + name + " ?")) {
            var lastIndex = window.location.href.lastIndexOf("/");
            window.location.href = window.location.href.slice(0, lastIndex+1) + "delete_images?model=" + name;
        }
    }
    </script>
    </head>
    <h1>Image models</h1>
    <h2><a href=/>Main page</a></h2>
    """
    app_manager = AppManager()
    models = app_manager.get_model_list()
    if models:
        html += "<ul>"
        
    for model in models:
        image_count = 0
        for class_name in app_manager.get_class_list(model):
            image_count += len(app_manager.get_images_list(model, class_name))
        html += f'<li><a href=images?model={model}>{model}</a>: {image_count} Images<button onclick="confirmDeleteAction(this.name)" name={model}>Delete images</button></li>'
    
    if models:
        html += "</ul>"
        
    yield from res.awrite(html)
    
async def show_classes(res, model):
    html = """
    <head>
    <script>
    function confirmDeleteAction(name) {
        if (window.confirm("Are you sure you want to delete images for:" + name + " ?")) {
            var lastIndex = window.location.href.lastIndexOf("/");
            var slashIndex = name.lastIndexOf("/");
            var model = name.slice(0, slashIndex);
            var class_name = name.slice(slashIndex+1);
            window.location.href = window.location.href.slice(0, lastIndex+1) + "delete_images?model=" + model + "&class=" + class_name;        }
    }
    </script>
    </head>
    <h1>Image models</h1>
    <h2><a href=/>Main page</a></h2>
    """
    app_manager = AppManager()
    class_list = app_manager.get_class_list(model)
    
    html += f'<h1>Classes for {model}</h1>'
    html += "<h2><a href=images>Image models</a></h2>"
    
    if class_list:
        html += "<ul>"
        
    for class_name in class_list:
        image_count = len(app_manager.get_images_list(model, class_name))
        html += f'<li><a href=images?model={model}&class={class_name}&page=1>{class_name}</a>: {image_count} Images<button onclick="confirmDeleteAction(this.name)" name={model}/{class_name}>Delete Images</button></li>'
    
    if class_list:
        html += "</ul>"
    yield from res.awrite(html)

async def show_images(res, model, class_name, page):
    app_manager = AppManager()
    files = app_manager.get_images_list(model, class_name)
    
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
        yield from res.awrite(f'<a href=image?model={model}&class={class_name}&file={file}>{file}</a>: <img src="{app_manager.get_image_path(model, class_name, file)}"><br />')

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
        
    app_manager = AppManager()
    code, buf = app_manager.get_image(model, class_name, file_name)
    
    if code != ResponseCode.OK:
        yield from picoweb.start_response(res, status="400")
        yield from res.awrite(f'{code}.Back to <a href=images>Images</a>')
    
    yield from picoweb.start_response(res, "image/jpeg")
    yield from res.awrite(buf)

def write_model_info_to_file(model_width, model_height, arena_size):
    app_manager = AppManager()
    info = [model_width + '\n', model_height + '\n', str(arena_size) + '\n']
    return app_manager.append_to_info_file_from_string_list(info)

@app.route('/finish')
def finish_create_model(req, res):
    model_manager = ModelManager()
    if model_manager.is_loaded():
        html = """
        <h1>Please unload model in order to add new model. Click <a href=unload>here</a> to unload model.</h1>
        """
        yield from picoweb.start_response(res, status="200")
        yield from res.awrite(html)
        return
    elif req.method != "POST":
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
    
    arena_size = app_manager.validate_required_memory(model_width, model_height)
    
    if arena_size == 0:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="409")
        yield from res.awrite("Uploaded model requires too much space to run and cannot be run on this device. Please consider uploading other models.")
    
    code = write_model_info_to_file(model_width, model_height, arena_size)
    if code != ResponseCode.OK:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="409")
        yield from res.awrite(f'{code}. Back to <a href=upload>Upload page</a>')
    
    app_manager.move_model_from_tmp_folder(model_name)
    
    yield from picoweb.start_response(res, status="201")
    yield from res.awrite("Model created. Back to <a href='/models'>Model list</a>.")

async def read_labels_byte_data_to_file(req):
    size = int(req.headers[b"Content-Length"])
    yield from req.read_form_byte_data(size)
    labels_file = req.data.split(TEXT_SPLITTER)[1].split(BYTE_CONTENT_END_SPLITTER)[0]
    
    app_manager = AppManager()
    
    return app_manager.create_labels_file_from_buffer(labels_file)

@app.route('/continue')
def continue_create_model(req, res):
    app_manager = AppManager()
    model_manager = ModelManager()
    if model_manager.is_loaded():
        html = """
        <h1>Please unload model in order to add new model. Click <a href=unload>here</a> to unload model.</h1>
        """
        yield from picoweb.start_response(res, status="200")
        yield from res.awrite(html)
        return
    elif req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST request accepted. Back to <a href='/upload'>Upload page</a>")
        return
    elif app_manager.model_passed == False:
        yield from picoweb.start_response(res, status="409")
        yield from res.awrite("Please usse <a href='/upload'>Upload page</a> to add new model.")
        return
    
    code = yield from read_labels_byte_data_to_file(req)
    
    if code != ResponseCode.OK:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="500")
        yield from res.awrite(f'{code}. Back to <a href=upload>Upload page</a>')
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
    app_manager = AppManager()
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
            
        code = app_manager.append_to_model_file_from_buffer(req.data)
        if code != ResponseCode.OK:
            return code
            
    yield from req.read_form_byte_data(MODEL_REQUEST_END_LEGTH)
    print("Read file")
    return code

@app.route('/create')
def create_model(req, res):   
    model_manager = ModelManager()
    app_manager = AppManager()
    if model_manager.is_loaded():
        html = """
        <h1>Please unload model in order to add new model. Click <a href=unload>here</a> to unload model.</h1>
        """
        yield from picoweb.start_response(res, status="200")
        yield from res.awrite(html)
        return
    elif req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST request accepted. Back to <a href='/upload'>Upload page</a>")
        return
    elif not app_manager.is_able_to_load_model(int(req.headers[b"Content-Length"])):
        yield from picoweb.start_response(res, status="409")
        yield from res.awrite(f'Model is too big. Maximum size of {MAX_MODEL_RAM_USAGE} bytes for the whole model is allowed. Back to <a href="/upload">Upload page</a>')
        return
    
    app_manager.reset_model_creation()
    
    code = yield from read_model_byte_data_to_file(req)
    
    if code != ResponseCode.OK:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="500")
        yield from res.awrite(f'{code}. Back to <a href=upload>Upload page</a>')
        return
    
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
    model_manager = ModelManager()
    if model_manager.is_loaded():
        html = """
        <h1>Please unload model in order to add new model. Click <a href=unload>here</a> to unload model.</h1>
        """
        yield from picoweb.start_response(res, status="200")
        yield from res.awrite(html)
        return
    
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
        app_manager = AppManager()
        model_list = app_manager.get_model_list()
        
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
        model_manager.load_model(model_name)
        
        yield from picoweb.start_response(res, status="200")
        yield from res.awrite(f'Successfully changed model to {model_name}. Back to <a href="/models">Model list</a>')
    else:
        yield from picoweb.start_response(res, status="405")
        yield from res.awrite("Only POST and GET request accepted. Back to <a href='/models'>Model list</a>")
      
@app.route('/unload')
def unload(req, res):
    model_manager = ModelManager()
    model_manager.unload_model()
    
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite("Model unloaded. Back to <a href='/models'>Model list</a>")

async def show_models(res):
    app_manager = AppManager()
    model_list = app_manager.get_model_list()
    html = ""
    if model_list:
        html += "<ul>"
        
    for model in model_list:
        html += f'<li>{model}<button onclick="confirmDeleteAction(this.name)" name={model}>Delete</button></li>'
    
    if model_list:
        html += "</ul>"
        
    yield from res.awrite(html)

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

@app.route('/delete')
def delete_model(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    if model == 'false':
        yield from picoweb.start_response(res, status="400")
        yield from res.awrite("Please use <a href=models>Model list</a> to delete models.")
        return
    
    app_manager = AppManager()
    app_manager.remove_model(model)
    
    yield from picoweb.start_response(res, status="200")
    yield from res.awrite("Model successfully deleted. Back to <a href='/models'>Model list</a>")
