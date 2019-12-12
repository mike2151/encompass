var NUM_FIELDS = 30;

var curr_method_number = 2;
var curr_code_numbers = {};

var add_api_field = function () {
    var added = document.createElement("div");
    document.getElementById("api_fields").appendChild(added);
    var name = "api_method_" + curr_method_number.toString();

    var textarea = document.createElement("textarea");
    textarea.setAttribute("id", name);
    textarea.setAttribute("rows", 5);
    textarea.setAttribute("name", name);
    textarea.setAttribute("placeholder", "Method Name: description, args, return type");
    textarea.setAttribute("class", "form-control small-margin-top");

    added.appendChild(textarea);
    
    curr_method_number = curr_method_number + 1;
};

var remove_api_field = function() {
    if (curr_method_number > 2) {
        document.getElementById("api_method_" + (curr_method_number-1).toString()).remove();
        curr_method_number = curr_method_number - 1;
    }
}

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
    if (curr_code_numbers[class_name] < NUM_FIELDS) {
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
        editor.setAttribute("class", "code-editor");    

        var switch_div = document.createElement("div");
        switch_div.setAttribute("class", "centered");
        switch_div.innerHTML = 'File <label class="switch"><input type="checkbox" name="' + class_name + '_switch_' + curr_code_numbers[class_name].toString() +'" id="' + class_name + '_switch_' + curr_code_numbers[class_name].toString() +'"><span class="slider round"></span></label> Code';

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

function textarea_edit(name) {
    var editor = ace.edit(name);
    editor.setTheme("ace/theme/chrome");
    editor.session.setMode("ace/mode/python");
    editor.setOptions({
        "showPrintMargin": !1,
        fontSize: "12pt",
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true
    });

    var textarea = $('textarea[name="' + name + '"]').hide();
    textarea.val(editor.getSession().getValue());
    editor.getSession().on('change', function(){
        textarea.val(editor.getSession().getValue());
    });
}    

function switch_code(number, name) {
    $("#" + name + "_body_name_" + number).hide();
    $("#" + name + "_body_" + number).hide();
    $("#" + name + "_switch_" + number).change(function() {
        if(this.checked) {
            $("#" + name + "_body_" + number).show();
            $("#" + name + "_body_name_" + number).show();
            $("#" + name + "_file_" + number).hide();
        } else {
            $("#" + name + "_body_name_" + number).hide();
            $("#" + name + "_body_" + number).hide();
            $("#" + name + "_file_" + number).show();
        }
    });
}

$(document).on("keydown", ":input:not(textarea)", function(event) {
    return event.key != "Enter";
});

// form library things
var validation_rules = {};
validation_rules["name"] = "required";
validation_rules["description"] = "required";
validation_rules["starter_file_1"] = {required: '#starter_body_name_1:blank'};
validation_rules["starter_body_name_1"] = {required: '#starter_file_1:blank'};

for (var i = 2; i < NUM_FIELDS+1; i++) {
    validation_rules["starter_file_" + i.toString()] = {required: '#starter_body_name_' + i.toString() + ':blank'};
    validation_rules["starter_body_name_" + i.toString()] = {required: '#starter_file_' + i.toString() + ':blank'};
    validation_rules["example_file_" + i.toString()] = {required: '#example_body_name_' + i.toString() + ':blank'};
    validation_rules["example_body_name_" + i.toString()] = {required: '#example_file_' + i.toString() + ':blank'};
    validation_rules["supporting_file_" + i.toString()] = {required: '#supporting_body_name_' + i.toString() + ':blank'};
    validation_rules["supporting_body_name_" + i.toString()] = {required: '#supporting_file_' + i.toString() + ':blank'};    
}

var has_been_created = {};
has_been_created[2] = false;
has_been_created[4] = false;
has_been_created[5] = false;
has_been_created[6] = false;
has_been_created[7] = false;
var form = $("#wizard");
form.validate({
    errorPlacement: function errorPlacement(error, element) { element.before(error); },
    rules: validation_rules
});
form.steps({
    headerTag: "h2",
    bodyTag: "section",
    transitionEffect: "slideLeft",
    autoFocus: true,
    enableFinishButton: false,
    onStepChanging: function (event, currentIndex, newIndex)
    {
        if (newIndex > currentIndex) {
            form.validate().settings.ignore = ":disabled,:hidden";
            return form.valid();
        }
        return true;
    },
    onFinishing: function (event, currentIndex)
    {
        form.validate().settings.ignore = ":disabled";
        return form.valid();
    },
    onStepChanged: function (event, currentIndex, newIndex)
    {
        if (currentIndex === 2) {
            if (!has_been_created[currentIndex]) {
                textarea_edit("supporting_body_1");
                switch_code("1", "supporting")
                has_been_created[currentIndex] = true;
            }
        } else if  (currentIndex === 4) {
            if (!has_been_created[currentIndex]) {
                textarea_edit("starter_body_1");
                switch_code("1", "starter");
                has_been_created[currentIndex] = true;
            }
        } else if  (currentIndex === 5) {
            if (!has_been_created[currentIndex]) {
                textarea_edit("example_body_1");
                switch_code("1", "example");
                has_been_created[currentIndex] = true;
            }
        } else if  (currentIndex === 6) {
            if (!has_been_created[currentIndex]) {
                textarea_edit("test_body_1");
                switch_code("1", "test");
                has_been_created[currentIndex] = true;
            }
        } else if  (currentIndex === 7) {
            if (!has_been_created[currentIndex]) {
                textarea_edit("solution_body_1");
                switch_code("1", "solution");
                has_been_created[currentIndex] = true;
            }
        } 
    }
});

$('#banned_imports').amsifySuggestags({
    type :'amsify',
  });

function resize_steps() {
    var w = parseInt(window.innerWidth);
    if(w <= 600) {
        for (var i = 0; i < 8; i++) {
            $("#wizard-t-" + i.toString()).html((i+1).toString());
        }
    }
}

window.onbeforeunload = function(e) {
    return "Are you sure you want to leave this page?";
};
resize_steps();
