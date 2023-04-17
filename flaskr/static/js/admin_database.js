function remove_all_options(select_box) {
    // remove all of the options currently held within the given select box
    while (select_box.options.length > 0) {
        select_box.remove(0)
    }
}

function update_select_options(select_box, options) {

    // update the options held within a given select box
    remove_all_options(select_box); // delete the current options

    var new_option = document.createElement('option') // create a new base element for an option
    var  option_text = document.createTextNode('-') // create a new base element for a text node

    // combine the option and text node elements
    new_option.appendChild(option_text)
    new_option.setAttribute('value', '')
    select_box.appendChild(new_option)

    // insert all of the new options provided into the select box
    for (let option of options.values()) {
        new_option = document.createElement('option')
        option_text = document.createTextNode(option)

        new_option.appendChild(option_text)
        new_option.setAttribute('value', option)

        select_box.appendChild(new_option)
    }
}

function update_view() {
    // updates the table of the database to match the current search and sort options

    // prepare variables
    var database_container = document.getElementById('database_container');
    var table_name = document.getElementById('table_name').value;
    var field_name_select = document.getElementById('field_name');
    var field_name = field_name_select.value;

    var sort_name = document.getElementById('sort_name').value;
    var sort_direction = document.getElementById('sort_opt').value;

    var search_query = document.getElementById('search_query').value;
    var search_type = document.getElementById('search_type').value;

    var table_URL = window.location.protocol+'//'+window.location.host+'/backend/admin/database/?table='+table_name;

    // if a field name has been provided to search for, add it to the URL parameters
    if (field_name!='') {
        table_URL+='&field='+field_name+'&q='+search_query+'&search_type='+search_type;
    }

    // if a sort option has been provided, add it to the URL parameters
    if (sort_name!='') {
        table_URL+="&sort_field="+sort_name+"&sort_direction="+sort_direction
    }

    // get the new HTML table for the database
    fetch (table_URL)
        .then((response) => response.text())
        .then((data) => database_container.innerHTML=data);
}

function update_fieldnames() {
    // update the fieldnames held within the fieldnames select box to match the current table
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
    // update the entire page (fieldnames and database table together)
    update_fieldnames();
    update_view();
}