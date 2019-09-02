var curr_method_number = 2;
var curr_code_number = 2;
var add_api_field = function () {
    var added = document.createElement("div");
    document.getElementById("api_fields").appendChild(added);
    var name = "api_method_" + curr_method_number.toString();

    var textarea = document.createElement("textarea");
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
    textarea.setAttribute("id", name);
    textarea.setAttribute("name", name);

    var label = document.createElement("label");
    label.innerHTML = "Code:";
    label.setAttribute("htmlFor", name);

    added.appendChild(label);
    added.appendChild(document.createElement("br"));
    added.appendChild(textarea);
    added.appendChild(document.createElement("br"));
    
    curr_code_number = curr_code_number + 1;
}