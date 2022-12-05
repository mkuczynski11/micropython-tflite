{% args file_list, back_href, page, render_next_page, model, class_name %}
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
        <script>
            function imageLoad(name) {
                var div_element = document.getElementsByName("spinner_" + name)[0];
                div_element.style.display = "none";
            }
        </script>
        {% include "nav.tpl" %}
        <main class="container py-5">
            <a href="{{back_href}}"><h2>Go back</h2></a>
            <div class="row">
                {% for file in file_list %}
                <div class="col-sm-4">
                    <div class="card mb-4 shadow-sm">
                        <div name="spinner_{{file}}" class="spinner-border" role="status">
                            <span class="sr-only">Loading...</span>
                        </div>
                        <img name="{{file}}" onload="imageLoad(this.name)" class="card-img-top" src="{{file}}" alt="{{file.rsplit('/')[-1]}}">
                        <div class="card-body">
                            <a target="_blank" href="/image?model={{model}}&class={{class_name}}&file={{file.rsplit('/')[-1]}}"><p class="card-text">{{file.rsplit('/')[-1]}}</p></a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% if page != 1 %}
            <button type="button" class="btn btn-outline-primary" onclick="location.href='/images_visible?model={{model}}&class={{class_name}}&page={{page-1}}'">Previous page</button>
            {% endif %}
            {% if render_next_page %}
            <button type="button" class="btn btn-outline-primary" onclick="location.href='/images_visible?model={{model}}&class={{class_name}}&page={{page+1}}'">Next page</button>
            {% endif %}
        </main>
    </body>
</html>


