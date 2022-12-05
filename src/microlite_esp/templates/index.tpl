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
        <main role="main">
            <section class="jumbotron text-center">
                <div class="container">
                    <h1 class="jumbotron-heading">Esp32 cam classificaton tool</h1>
                    <p class="lead text-muted">Thank you for using our tool for classificaton purposes. With this device you are able to use your favourite classification models with built-in camera.</p>
                </div>
            </section>
            <div class="py-5 bg-light">
                <div class="container">
                    <div class="row">
                        <div class="col-md-12">
                            <div class="card-group">
                                <div class="card mb-4 shadow-sm">
                                    <div class="card-body flex-column d-flex">
                                        <h5 class="card-title">Model list</h5>
                                        <p class="card-text">Explore model list and play with your favourite.</p>
                                        <button type="button" class="btn btn-lg btn-block btn-outline-primary mt-auto" onclick="location.href='/models'">View models</button>
                                    </div>
                                </div>
                                <div class="card mb-4 shadow-sm">
                                    <div class="card-body flex-column d-flex">
                                        <h5 class="card-title">Image list</h5>
                                        <p class="card-text">Explore list of images for all models available.</p>
                                        <button type="button" class="btn btn-lg btn-block btn-outline-primary mt-auto" onclick="location.href='/images'">View images</button>
                                    </div>
                                </div>
                                <div class="card mb-4 shadow-sm">
                                    <div class="card-body flex-column d-flex">
                                        <h5 class="card-title">Model creation</h5>
                                        <p class="card-text">Add your favourite model.</p>
                                        <button type="button" class="btn btn-lg btn-block btn-outline-primary mt-auto" onclick="location.href='/upload'">Add new model</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </body>
</html>
