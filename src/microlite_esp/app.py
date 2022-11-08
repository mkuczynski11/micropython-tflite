import picoweb

from config import (
    IMAGES_ON_PAGE, BUFFER_SIZE, MODEL_REQUEST_END_LENGTH,
    FILE_STREAM_SPLITTER, TEXT_SPLITTER, BYTE_CONTENT_END_SPLITTER)
from model import ModelManager
from app_manager import AppManager, ResponseCode

# Import and initialize template loader
from utemplate.compiled import Loader
template_loader = Loader(None, "templates")

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
    temp = template_loader.load("index.tpl")
    for s in temp():
        yield from res.awrite(s)
    
@app.route('/delete_images')
def delete_images(req, res):
    app_manager = AppManager()
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
    file_name = req.form.get('file', 'false')
    if file_name != 'false' and class_name != 'false' and model != 'false':
        code = app_manager.remove_image(model, class_name, file_name)
        if code != ResponseCode.OK:
            yield from picoweb.start_response(res, status="400")
            temp = template_loader.load("error.tpl")
            for s in temp("{code}", "/images"):
                yield from res.awrite(s)
            return
        msg = f'{file_name} for {model}/{class_name} successfully deleted.'
        url = f'/images?model={model}&class={class_name}'
    elif class_name != 'false' and model != 'false':
        code = app_manager.remove_images_for_class(model, class_name)
        if code != ResponseCode.OK:
            yield from picoweb.start_response(res, status="400")
            temp = template_loader.load("error.tpl")
            for s in temp("{code}", "/images"):
                yield from res.awrite(s)
            return
        msg = f'Images for {model}/{class_name} successfully deleted.'
        url = f'/images?model={model}'
    elif model != 'false':
        code = app_manager.remove_images_for_model(model)
        if code != ResponseCode.OK:
            yield from picoweb.start_response(res, status="400")
            temp = template_loader.load("error.tpl")
            for s in temp("{code}", "/images"):
                yield from res.awrite(s)
            return
        msg = f'Images for {model} successfully deleted.'
        url = f'/images'
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("confirm_action.tpl")
    for s in temp(msg, url):
        yield from res.awrite(s)
        
async def show_models_for_images(res):
    app_manager = AppManager()
    model_list = app_manager.get_model_list()
        
    counter_list = []
    for model in model_list:
        image_count = 0
        for class_name in app_manager.get_class_list(model)[1]:
            image_count += len(app_manager.get_images_list(model, class_name)[1])
        counter_list.append(image_count)
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("image_list.tpl")
    for s in temp(model_list, "model", "/images?model=", "/", counter_list):
        yield from res.awrite(s)
    
async def show_classes(res, model):
    app_manager = AppManager()
    ok, class_list = app_manager.get_class_list(model)
    
    if ok != ResponseCode.OK:
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("{code}", "/images"):
            yield from res.awrite(s)
        return
        
    counter_list = []
    for class_name in class_list:
        image_count = len(app_manager.get_images_list(model, class_name)[1])
        counter_list.append(image_count)
        
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("image_list.tpl")
    for s in temp(class_list, "class", f'/images?model={model}&class=', '/images', counter_list, {'model': model}):
        yield from res.awrite(s)

async def show_images(res, model, class_name):
    app_manager = AppManager()
    ok, file_list = app_manager.get_images_list(model, class_name)
    
    if ok != ResponseCode.OK:
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("{code}", "/images"):
            yield from res.awrite(s)
        return
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("image_list.tpl")
    for s in temp(file_list, "file", f'/image?model={model}&class={class_name}&file=', f'/images?model={model}', None, {'model':model, 'class':class_name}):
        yield from res.awrite(s)

@app.route('/images_visible')
def images_visible(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
    page = req.form.get('page', 'false')
    
    if model == 'false':
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("model parameter was not provided.", "/images"):
            yield from res.awrite(s)
        return
    elif class_name == 'false':
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("class parameter was not provided.", "/images"):
            yield from res.awrite(s)
        return
    
    if page == 'false':
        page = 1
    else:
        int(page)
    
    app_manager = AppManager()
    code, file_list = app_manager.get_images_list(model, class_name)
    
    if code != ResponseCode.OK:
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp(f'{code}', "/images"):
            yield from res.awrite(s)
        return
    
    starting_index = (page - 1)*IMAGES_ON_PAGE
    images_left = min(IMAGES_ON_PAGE, len(file_list) - (page - 1)*IMAGES_ON_PAGE)
    files = file_list[starting_index:starting_index+images_left]
    for i in range(len(files)):
        files[i] = app_manager.get_image_path(model, class_name, files[i])
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("images.tpl")
    for s in temp(files):
        yield from res.awrite(s)

# NOTE: Running this required to change static folder in picoweb sources
# TODO: Add option to download images
@app.route('/images')
def images(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
        
    if class_name != 'false' and model != 'false':
        yield from show_images(res, model, class_name)
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
    
    if model == 'false':
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("model parameter was not provided.", "/images"):
            yield from res.awrite(s)
        return
    elif class_name == 'false':
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("class_name parameter was not provided.", "/images"):
            yield from res.awrite(s)
        return
    elif file_name == 'false':
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("file_name parameter was not provided.", "/images"):
            yield from res.awrite(s)
        return
        
    app_manager = AppManager()
    code, buf = app_manager.get_image(model, class_name, file_name)
    
    if code != ResponseCode.OK:
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp(f'{code}', "/images"):
            yield from res.awrite(s)
        return
    
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
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Before uploading model unload any active models.", "/models"):
            yield from res.awrite(s)
        return
    elif req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Only POST request is accepted.", "/models"):
            yield from res.awrite(s)
        return
    
    app_manager = AppManager()
    
    yield from req.read_form_data()
    try:
        model_name = req.form["modelname"]
        model_width = req.form["modelwidth"]
        model_height = req.form["modelheight"]
    except KeyError:
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Request was not complete. Please use upload form to add new models.", "/models"):
            yield from res.awrite(s)
        return
        
    if not app_manager.is_able_to_create_model():
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Please use upload for adding new model.", "/models"):
            yield from res.awrite(s)
        return
    
    arena_size = app_manager.validate_required_memory(model_width, model_height)
    
    if arena_size == 0:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Model requires too much space to run and cannot be used on this device. Consider addint other models.", "/models"):
            yield from res.awrite(s)
        return
        
    code = write_model_info_to_file(model_width, model_height, arena_size)
    if code != ResponseCode.OK:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp(f'{code}', "/models"):
            yield from res.awrite(s)
        return
    
    app_manager.move_model_from_tmp_folder(model_name)
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("confirm_action.tpl")
    for s in temp(f'Model successfully created.', "/models"):
        yield from res.awrite(s)

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
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Before uploading model unload any active models.", "/models"):
            yield from res.awrite(s)
        return
    elif req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Only POST request is accepted.", "/models"):
            yield from res.awrite(s)
        return
    elif app_manager.model_passed == False:
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Please use upload for adding new model.", "/models"):
            yield from res.awrite(s)
        return
    
    code = yield from read_labels_byte_data_to_file(req)
    
    if code != ResponseCode.OK:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp(f'{code}', "/models"):
            yield from res.awrite(s)
        return
    
    app_manager.labels_passed = True
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("details_form.tpl")
    for s in temp([
        ('modelname', 'Model name', 'text'),
        ('modelwidth', 'Model width', 'number'),
        ('modelheight', 'Model height', 'number')
        ], 'finish',):
        yield from res.awrite(s)

async def read_model_byte_data_to_file(req):
    app_manager = AppManager()
    final_index = int(req.headers[b"Content-Length"]) - MODEL_REQUEST_END_LENGTH
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
            
    yield from req.read_form_byte_data(MODEL_REQUEST_END_LENGTH)
    print("Read file")
    return code
            
    yield from req.read_form_byte_data(MODEL_REQUEST_END_LENGTH)
    print("Read file")
    return code

@app.route('/create')
def create_model(req, res):   
    model_manager = ModelManager()
    app_manager = AppManager()
    if model_manager.is_loaded():
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Before uploading model unload any active models.", "/models"):
            yield from res.awrite(s)
        return
    elif req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Only POST request accepted.", "/models"):
            yield from res.awrite(s)
        return
    elif not app_manager.is_able_to_load_model(int(req.headers[b"Content-Length"])):
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp(f'Model is too big. Maximum size of {MAX_MODEL_RAM_USAGE} bytes for the whole model is allowed', "/models"):
            yield from res.awrite(s)
        return

    app_manager.reset_model_creation()
    
    code = yield from read_model_byte_data_to_file(req)
    
    if code != ResponseCode.OK:
        app_manager.reset_model_creation()
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp(f'{code}', "/models"):
            yield from res.awrite(s)
        yield from app.render_template(res, "error.tpl", (f'{code}', "/models",))
        return
    
    app_manager.model_passed = True
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("file_upload_form.tpl")
    for s in temp(".txt", "labelsfile", "continue", "labels"):
        yield from res.awrite(s)

@app.route('/upload')
def upload_form(req, res):
    model_manager = ModelManager()
    if model_manager.is_loaded():
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Before uploading model unload any active models.", "/models"):
            yield from res.awrite(s)
        return
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("file_upload_form.tpl")
    for s in temp(".tflite", "modelfile", "create", "model"):
        yield from res.awrite(s)
    
@app.route('/change')
def change_model(req, res):
    if req.method != "POST":
        yield from picoweb.start_response(res, status="405")
        temp = template_loader.load("error.tpl")
        for s in temp("Only POST request accepted.", "/models"):
            yield from res.awrite(s)
        return
    
    yield from req.read_form_data()
    try:
        model_name = req.form["models"]
    except KeyError:
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("Model change request was not complete.", "/models"):
            yield from res.awrite(s)
        return
        
    model_manager = ModelManager()
    ok = model_manager.load_model(model_name)
    
    if not ok:
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp(f'{model_name} model does not exist.', "/models"):
            yield from res.awrite(s)
        return
    
    headers = {"Location": "/models"}
    yield from picoweb.start_response(res, status="303", headers=headers)
      
@app.route('/unload')
def unload(req, res):
    model_manager = ModelManager()
    model_manager.unload_model()
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("confirm_action.tpl")
    for s in temp(f'Model successfully unloaded. No models are active.', "/models"):
        yield from res.awrite(s)

@app.route('/models')
def models(req, res):
    model_manager = ModelManager()
    active_model = model_manager.active_model_name
    app_manager = AppManager()
    model_list = app_manager.get_model_list()
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("model_list.tpl")
    for s in temp(model_list, active_model):
        yield from res.awrite(s)

@app.route('/delete_model')
def delete_model(req, res):
    req.parse_qs()
    model = req.form.get('model', 'false')
    if model == 'false':
        yield from picoweb.start_response(res, status="400")
        temp = template_loader.load("error.tpl")
        for s in temp("model parameter was not provided.", "/models"):
            yield from res.awrite(s)
        return
    
    app_manager = AppManager()
    result = app_manager.remove_model(model)
    
    if result != ResponseCode.OK:
        yield from picoweb.start_response(res, status="404")
        temp = template_loader.load("error.tpl")
        for s in temp(f'{model} model was not found.', "/models"):
            yield from res.awrite(s)
        return
    
    yield from picoweb.start_response(res, status="200")
    temp = template_loader.load("confirm_action.tpl")
    for s in temp(f'{model} model successfully deleted.', "/models"):
        yield from res.awrite(s)
