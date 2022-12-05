{% args accept_type, input_name, form_action, input_label %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Classification tool</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet"/>
    <link href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet"/>
</head>
    <body>
        {% include "nav.tpl" %}
        <main class="container">
            <div class="p-3">
                <h1>Upload {{input_label}}</h1>
                <div class="alert alert-secondary">Please be patinent. Uploading file can take up to several minutes</div>
                <form action='{{form_action}}' enctype="multipart/form-data" method='POST'>
                    <div class="form-group row">
                        <label class="btn btn-primary col-sm-12">
                            <i class="fa fa-image"></i>{{input_label}}<input id='file' type='file' accept='{{accept_type}}' name='{{input_name}}' style="display: none;"/>
                        </label>
                        <input class="btn btn-primary mt-3 col-sm-4" type='submit' value='submit' />
                    </div>
                </form>
            </div>
        </main>
    </body>
</html>