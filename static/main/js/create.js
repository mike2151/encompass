var curr_method_number = 2;
var curr_code_numbers = {};

var add_api_field = function () {
    var added = document.createElement("div");
    document.getElementById("api_fields").appendChild(added);
    var name = "api_method_" + curr_method_number.toString();

    var textarea = document.createElement("textarea");
    textarea.className = "form-control";
    textarea.setAttribute("id", name);
    textarea.setAttribute("name", name);

    var label = document.createElement("label");
    label.innerHTML = "Method:";
    label.setAttribute("htmlFor", name);

    added.appendChild(label);
    added.appendChild(document.createElement("br"));
    added.appendChild(textarea);
    added.appendChild(document.createElement("br"));
    
    curr_method_number = curr_method_number + 1;
};

function element_exists(string_id) {
    var element =  document.getElementById(string_id);
    return (typeof(element) != 'undefined' && element != null);
}

function get_starting_num(class_name) {
    var curr_num = 1;
    var string_name = class_name + "_switch_" + curr_num.toString();
    while (element_exists(string_name)) {
        curr_num = curr_num + 1;
        string_name = class_name + "_switch_" + curr_num.toString();
    }
    return curr_num;
}

var add_code_file = function (class_name) {
    if (!(class_name in curr_code_numbers)) {
        curr_code_numbers[class_name] = get_starting_num(class_name);
    }
    if (curr_code_numbers[class_name] < 10) {
        var added = document.createElement("div");
        added.setAttribute("id", "div_" + class_name + "_code_" + curr_code_numbers[class_name].toString())
        document.getElementById(class_name + "_fields").appendChild(added);
        var name = class_name + "_body_" + curr_code_numbers[class_name].toString();

        var textarea = document.createElement("textarea");
        textarea.setAttribute("name", name);

        var file_name = document.createElement("div");
        file_name.innerHTML = '<input class="form-control name-of-file" id="' + class_name + '_body_name_' + curr_code_numbers[class_name].toString() + '" maxlength="128" name="' + class_name + '_body_name_' + curr_code_numbers[class_name].toString() + '" placeholder="Name of file"></input>'

        var editor = document.createElement("div");
        editor.setAttribute("id", name);
        editor.setAttribute("style", "height: 20vh; width: 100%; margin-bottom: 1vh");    

        var switch_div = document.createElement("div");
        switch_div.setAttribute("class", "centered");
        switch_div.innerHTML = 'Code <label class="switch"><input type="checkbox" name="' + class_name + '_switch_' + curr_code_numbers[class_name].toString() +'" id="' + class_name + '_switch_' + curr_code_numbers[class_name].toString() +'"><span class="slider round"></span></label> File';

        var file_div = document.createElement("div");
        file_div.setAttribute("class", "centered");
        file_div.innerHTML = '<input type="file" id="' + class_name + '_file_' + curr_code_numbers[class_name].toString() + '" name="' + class_name + '_file_' + curr_code_numbers[class_name].toString() + '"></input>';

        added.appendChild(document.createElement("center"));
        added.appendChild(switch_div);
        added.appendChild(document.createElement("center"));
        added.appendChild(file_div);
        added.appendChild(file_name);
        added.appendChild(editor);
        added.appendChild(document.createElement("br"));
        added.appendChild(textarea);
        added.appendChild(document.createElement("br"));

        textarea_edit(name);
        switch_code(curr_code_numbers[class_name].toString(), class_name);
        
        curr_code_numbers[class_name] = curr_code_numbers[class_name] + 1;
    }
} 

var remove_code_file = function (class_name) {
    if (!(class_name in curr_code_numbers)) {
        curr_code_numbers[class_name] = get_starting_num(class_name);
    }
    if (curr_code_numbers[class_name] > 2) {
        document.getElementById("div_" + class_name + "_code_" + (curr_code_numbers[class_name]-1).toString()).remove();
        curr_code_numbers[class_name] = curr_code_numbers[class_name] - 1;
    }
}
