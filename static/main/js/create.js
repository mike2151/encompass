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

var add_code_body = function () {
    var added = document.createElement("div");
    document.getElementById("code_fields").appendChild(added);
    var name = "code_body_" + curr_code_number.toString();

    var textarea = document.createElement("textarea");
    textarea.setAttribute("name", name);

    var editor = document.createElement("div");
    editor.setAttribute("id", name);
    editor.setAttribute("style", "height: 20vh; width: 100%; margin-bottom: 1vh");

    added.appendChild(editor);
    added.appendChild(document.createElement("br"));
    added.appendChild(textarea);
    added.appendChild(document.createElement("br"));

    textarea_edit(name);
    
    curr_code_number = curr_code_number + 1;
}
