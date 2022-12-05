{% args item_list, delete_endpoint, param_name, item_href=None, counter_list=None, param_dict=None %}
<div class="container-fluid">
    <table class="table">
        <thead>
            <tr>
                <th scope="col">{{param_name}}</th>
                <th scope="col">action</th>
                {% if counter_list != None%}
                <th scope="col">occurances</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for i in range(len(item_list)) %}
                <tr>
                    <td>
                        {% if item_href != None %}
                        <button type="button" class="btn btn-outline-primary" onclick="location.href='{{item_href}}{{item_list[i]}}'">{{item_list[i]}}</button>
                        {% else %}
                        <span>{{item_list[i]}}</p>
                        {% endif %}
                    </td>
                    <td>
                        <button name="{{item_list[i]}}" onclick="confirmDeleteAction(this.name)" type="button" class="btn btn-outline-primary">Delete</button>
                    </td>
                    {% if counter_list != None%}
                    <td>
                        <span class="badge badge-pill badge-primary">{{counter_list[i]}}</span>
                    </td>
                    {% endif %}
                </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<script>
    function confirmDeleteAction(name) {
        if (window.confirm("Are you sure you want to delete:" + name + " ?")) {
            var lastIndex = window.location.href.lastIndexOf("/");
            var param_string = ""
            {% if param_dict != None %}
            {% for key, value in param_dict.items() %}
            param_string = param_string + "{{key}}" + "=" + "{{value}}" + "&"
            {% endfor %}
            {% endif %}
            window.location.href = window.location.href.slice(0, lastIndex+1) + "{{delete_endpoint}}" +"?" + param_string +  "{{param_name}}" + "=" + name;
        }
    }
</script>
