
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function ajax_short(request_dict) {
    var result = $.post("/solo/settings/",
        request_dict,
    );
    return result;
};


var btns_text = {
    "fabric": {"on": "включить", "off": "отключить"},
    "main": {"on": "сделать основным", "off": "основной"},
    "marry": {"on": "включить", "off": "исключить"},
};
function change_set_btn(data, btn, btn_type) {
    if ( data["resp"] === "ok" ) {
        if ( btn.value === "on" ) {
            btn.value = "off";
            btn.textContent = btns_text[btn_type]["off"];
        } else {
            btn.value = "on";
            btn.textContent = btns_text[btn_type]["on"];
        };
    };
};

$(document).ready(function(){
    // trigger for .set btns (change True/False statement)
    $(".set").click(function(){
        var request_dict = {cmd: "edit"}
        request_dict["name"] = this.parentElement.children[0].textContent;
        request_dict["type"] = this.parentElement.children[0].getAttribute("value");
        if (this.value === "on") {
            request_dict["value"] = "active";
        } else {
            request_dict["value"] = "inactive";
        };

        var btn = this;

        if (request_dict["type"] == 'email') {
            request_dict["value_type"] = this.getAttribute("value_type");
        };

        console.log(request_dict);

        var posting = ajax_short(request_dict);

        posting.done( function (data) {
            if (request_dict["type"] == 'fabric') {
                var btn_type = 'fabric';
            } else {
                var btn_type = request_dict["value_type"];
            };
            change_set_btn(data, btn, btn_type);
            console.log(data);
        });
    });
});


function hide_list_by_id(ids) {
    $("#"+ids).hide();
};

function show_list_by_id(ids) {
    $("#"+ids).show();
};

function hide_list_by_cls(cls) {
    $("."+cls).hide();
};

function show_list_by_cls(cls) {
    $("."+cls).show();
};


$(document).on("click", ".hider", function() {
    if (this.textContent == "Свернуть") {
        hide_list_by_id(this.value);
        this.textContent = "Развернуть";
    } else {
        show_list_by_id(this.value);
        this.textContent = "Свернуть";
    };
});

$(document).on("click", ".non_active_hider", function() {
    if (this.textContent == "Свернуть неактивные") {
        hide_list_by_cls(this.value);
        this.textContent = "Развернуть неактивные";
    } else {
        show_list_by_cls(this.value);
        this.textContent = "Свернуть неактивные";
    };
});
