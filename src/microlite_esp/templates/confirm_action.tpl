{% args msg, href_back %}
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
            <div>
                <div class="alert alert-success">
                    {{msg}}
                </div>
                <p>
                    <a href="{{href_back}}">Go back</a>
                </p>
            </div>
        </main>
    </body>
</html>


