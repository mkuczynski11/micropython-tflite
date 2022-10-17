import picoweb
import uos

from config import IMAGES_PATH

# NOTE: None in order to pkg_resources to work
app = picoweb.WebApp(None)

@app.route('/')
def index(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite(
"""
<h1>Welcome to the esp32_cam classification tool. Choose your option</h1>
    <ul>
        <li><a href='images'>Images</a></li>
        <li><a href='upload'>Upload</a></li>
    </ul>
""")

# TODO: Running this required to change static folder in picoweb sources
@app.route('/images')
def images(req, resp):
    text = "<h1>Images directories</h1>"
    
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
    
    if class_name != 'false':
        files_dir = IMAGES_PATH + '/' + model + '/' + class_name
        files = uos.listdir(files_dir)
        for file in files:
            text += file + ": <img src='" + files_dir + '/' + file + "'><br />"
    elif model != 'false':
        class_dirs = IMAGES_PATH + '/' + model
        dirs = uos.listdir(class_dirs)
        if dirs:
            text += "<ul>"
        for d in dirs:
            text += "<li><a href=images?model=" + model + "&class=" + d + ">" + d + "</a></li>"
        if dirs:
            text += "</ul>"
    else:
        models_dirs = IMAGES_PATH
        dirs = uos.listdir(models_dirs)
        if dirs:
            text += "<ul>"
        for d in dirs:
            text += "<li><a href=images?model=" + d + ">" + d + "</a></li>"
        if dirs:
            text += "</ul>"
    yield from picoweb.start_response(resp)
    yield from resp.awrite(text)
    
@app.route('/image')
def image(req, resp):
    req.parse_qs()
    model = req.form.get('model', 'false')
    class_name = req.form.get('class', 'false')
    file_name = req.form.get('file', 'false')
    
    if model == 'false' or class_name == 'false' or file_name == 'false':
        yield from picoweb.start_response(writer, status="400")
        yield from resp.awrite("400/r/n")
        
    f_path = IMAGES_PATH + '/' + model + '/' + class_name + '/' + file_name
    f = open(f_path, 'rb')
    buf = f.read()
    f.close()
    
    yield from picoweb.start_response(resp, "image/jpeg")
    yield from resp.awrite(buf)
    
@app.route('/upload')
def upload_form(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite("Upload module")
    
