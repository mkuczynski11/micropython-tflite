{% args details_list, form_action %}
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
                <h1>Upload details</h1>
                <form action='{{form_action}}' method='POST'>
                    <div class="form-group">
                        {% for value in details_list %}
                        <label for='{{value[0]}}'>{{value[1]}}</label>
                        <input id='{{value[0]}}' type='{{value[2]}}' name='{{value[0]}}' class="form-control form-control-sm"/>
                        {% endfor %}
                        <input class="btn btn-primary mt-3" type='submit' value='submit' />
                    </div>
                </form>
            </div>
        </main>
    </body>
</html>
