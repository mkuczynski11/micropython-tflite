{% args item_list, param_name, item_href, back_href, counter_list=None, param_dict=None %}
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
                <h1>
                Browse images
                {% if param_dict != None %}
                {% for key, value in param_dict.items() %} 
                /{{value}}
                {% endfor %}
                {% endif %}
                </h1>
                <a href="{{back_href}}"><h2>Go back</h2></a>
                {% if param_dict != None and 'model' in param_dict.keys() and 'class' in param_dict.keys() %}
                <a href="/images_visible?model={{param_dict['model']}}&class={{param_dict['class']}}">View image cards<h2></h2></a>
                {% endif %}
            </div>
            {% include "list.tpl" item_list, "delete_images", param_name, item_href, counter_list, param_dict %}
        </main>
    </body>
</html>

