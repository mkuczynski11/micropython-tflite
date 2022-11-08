{% args accept_type, input_name, form_action, input_label %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Classification tool</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
</head>
    <body>
        {% include "nav.tpl" %}
        <main class="container">
            <div class="p-3">
                <h1>Upload {{input_label}}</h1>
                <div class="alert alert-secondary">Please be patinent. Uploading file can take up to several minutes</div>
                <form action='{{form_action}}' enctype="multipart/form-data" method='POST'>
                    <div class="form-group">
                        <label for='file'>{{input_label}}</label>
                        <input id='file' type='file' accept='{{accept_type}}' name='{{input_name}}' class="form-control form-control-sm"/>
                        <input class="btn btn-primary mt-3" type='submit' />
                    </div>
                </form>
            </div>
        </main>
    </body>
</html>