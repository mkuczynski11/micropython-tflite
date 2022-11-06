{% args model_list, active_model %}
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
            <div class="row p-3">
                <div class="col-md-6 d-flex flex-column justify-content-around">
                    <h1>Model list</h1>
                    <a href="/upload"><h4>Add new model</h4></a>
                    <a href="/unload"><h4>Unload model</h4></a>
                </div>
                <div class="col-md-6">
                    {% if active_model == None %}
                    <div class="alert alert-warning" role="alert">
                        No active model. Pick one to enable classification.
                    </div>
                    {% else %}
                    <div class="alert alert-primary" role="alert">
                        Currently active model is {{active_model}}
                    </div>
                    {% endif %}
                    <form action='change' method='POST'>
                        <div class="form-group">
                            <label for='models'>Choose model:</label>
                            <select id='models' name='models' class="form-control form-control-sm">
                            {% for model in model_list %}
                            <option value="{{model}}">{{model}}</option>
                            {% endfor %}
                        </div>
                        <input class=" btn btn-primary mt-3" type='submit' />
                    </form>
                </div>
            </div>
            {% include "list.tpl" model_list, "delete_model", "model" %}
        </main>
    </body>
</html>
