{% args file_list %}
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
        <main class="container py-5">
            <div class="row">
                {% for file in file_list %}
                <div class="col-sm-4">
                    <div class="card mb-4 shadow-sm">
                        <div name="spinner_{{file}}" class="spinner-border" role="status">
                            <span class="sr-only">Loading...</span>
                        </div>
                        <img name="{{file}}" onload="imageLoad(this.name)" class="card-img-top" src="{{file}}" alt="{{file.rsplit('/')[-1]}}">
                        <div class="card-body">
                            <p class="card-text">{{file.rsplit('/')[-1]}}</p>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </main>
        <script>
            function imageLoad(name) {
                var div_element = document.getElementsByName("spinner_" + name)[0];
                div_element.style.display = "none";
            }
        </script
    </body>
</html>


