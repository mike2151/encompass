var curr_method_number = 2;
var curr_code_number = 2;
var curr_test_case = 2;

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

var add_code_file = function (class_name) {
    if (curr_code_number < 10) {
        var added = document.createElement("div");
        added.setAttribute("id", "div_" + class_name + "_code_" + curr_code_number.toString())
        document.getElementById(class_name + "_fields").appendChild(added);
        var name = class_name + "_body_" + curr_code_number.toString();

        var textarea = document.createElement("textarea");
        textarea.setAttribute("name", name);

        var file_name = document.createElement("div");
        file_name.innerHTML = '<input class="form-control name-of-file" id="' + class_name + '_body_name_' + curr_code_number.toString() + '" maxlength="128" name="' + class_name + '_body_name_' + curr_code_number.toString() + '" placeholder="Name of file"></input>'

        var editor = document.createElement("div");
        editor.setAttribute("id", name);
        editor.setAttribute("style", "height: 20vh; width: 100%; margin-bottom: 1vh");    

        var switch_div = document.createElement("div");
        switch_div.innerHTML = 'Code <label class="switch"><input type="checkbox" name="' + class_name + '_switch_' + curr_code_number.toString() +'" id="' + class_name + '_switch_' + curr_code_number.toString() +'"><span class="slider round"></span></label> File';

        var file_div = document.createElement("div");
        file_div.innerHTML = '<input class="form-control" type="file" id="' + class_name + '_file_' + curr_code_number.toString() + '" name="' + class_name + '_file_' + curr_code_number.toString() + '"></input>';

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
        switch_code(curr_code_number.toString(), class_name);
        
        curr_code_number = curr_code_number + 1;
    }
} 

var remove_code_file = function (class_name) {
    if (curr_code_number > 2) {
        document.getElementById("div_" + class_name + "_code_" + (curr_code_number-1).toString()).remove();
        curr_code_number = curr_code_number - 1;
    }
}
