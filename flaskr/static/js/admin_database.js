function remove_all_options(select_box) {
    while (select_box.options.length > 0) {
        select_box.remove(0)
    }
}

function update_select_options(select_box, options) {
    remove_all_options(select_box);

    var new_option = document.createElement('option')
    var  option_text = document.createTextNode('-')

    new_option.appendChild(option_text)
    new_option.setAttribute('value', '')
    select_box.appendChild(new_option)

    for (let option of options.values()) {
        new_option = document.createElement('option')
        option_text = document.createTextNode(option)

        new_option.appendChild(option_text)
        new_option.setAttribute('value', option)

        select_box.appendChild(new_option)
    }
}

function update_view() {
    var database_container = document.getElementById('database_container');
    var table_name = document.getElementById('table_name').value;
    var field_name_select = document.getElementById('field_name');
    var field_name = field_name_select.value;

    var sort_name = document.getElementById('sort_name').value;
    var sort_direction = document.getElementById('sort_opt').value;

    var search_query = document.getElementById('search_query').value;
    var search_type = document.getElementById('search_type').value;

    var table_URL = window.location.protocol+'//'+window.location.host+'/backend/admin/database/?table='+table_name;
    if (field_name!='') {
        table_URL+='&field='+field_name+'&q='+search_query+'&search_type='+search_type;
    }

    if (sort_name!='') {
        table_URL+="&sort_field="+sort_name+"&sort_direction="+sort_direction
    }
    fetch (table_URL)
        .then((response) => response.text())
        .then((data) => database_container.innerHTML=data);
}

function update_fieldnames() {
    var table_name = document.getElementById('table_name').value;
    var field_name_select = document.getElementById('field_name');
    var sort_name_select = document.getElementById('sort_name')
    var search_query = document.getElementById('search_query')
    var res_data

    field_name_select.value = ''
    search_query.value = ''

    var field_URL = window.location.protocol+'//'+window.location.host+'/backend/admin/database/fieldnames/?table='+table_name;
    fetch(field_URL) 
        .then((response) => response.json())
        .then((data) => res_data = data)
        .then(() => update_select_options(field_name_select, res_data))
        .then(() => update_select_options(sort_name_select, res_data))
}

function update_page() {
    update_fieldnames();
    update_view();
}