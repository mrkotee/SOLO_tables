

var analog_vcodes_dict = {};
var analog_vcodes_counter_dict = {};

$(document).ready(function(){
	var comments = $(".comment");
	var footer = false;
	for (var i = 0; i < comments.length; i++) {
		var comment = $(".comment")[i];
		var comment_text = comment.textContent;
		if ( comment_text.search("Аналоги:") != -1 ) {
			var vcode = comment.parentElement.children[0].textContent;
			comment.parentElement.children[0].classList.add(vcode) ;
			comment.classList.add("has_analog");
			analog_vcodes_counter_dict[vcode] = 0;
			analog_vcodes_dict[vcode] = [];
			if ( comment_text.search("не найден") == -1 ) { analog_vcodes_dict[vcode].push(vcode) };
			comment_text = comment_text.slice( comment_text.search("Аналоги:")+9);
			while ( comment_text.search(/(\d+[PV]\d)/g) != -1 ) {
				var comm_vcode = comment_text.slice( comment_text.search(/(\d+[PV]\d)/g), comment_text.search(/(P4|P8|V8|V4)/g)+2 );
				analog_vcodes_dict[vcode].push(comm_vcode);
				comment_text = comment_text.slice( comment_text.search(/(P4|P8|V8|V4)/g)+2 );

			};
			if ( footer == false ) {
				$("table")[0].insertAdjacentHTML('afterEnd', '<p>*При нажатии на коментарий с аналогами фотообоев - артикул заменится автоматически</p>');
				footer = true;
			};
		};
	};


});



$(document).ready(function(){

	$(".has_analog").click(function(){

		vcode = $(this).parent().find(".vcode")[0].classList[1];

		analog_vcodes = analog_vcodes_dict[vcode];

		if (analog_vcodes.length > 1) {
			var analog_vcode = analog_vcodes[analog_vcodes_counter_dict[vcode]];
			analog_vcodes_counter_dict[vcode]++;
			if (analog_vcodes_counter_dict[vcode] == analog_vcodes.length) {
				analog_vcodes_counter_dict[vcode] = 0
			};
		} else {
			var analog_vcode = analog_vcodes[0];
		};
		$(this).parent().find(".vcode").text( analog_vcode );
	});
});


//regexp for photo vcode
// .search(/(\d+[PV]\d)/g)

//regexp for end of vcode
// .search(/(P4|P8|V8|V4)/g)


$(document).on("dblclick", ".vcode", function() {
	var text_ = $(this).text();
	$(this).replaceWith("<input class=\"vcode\" value=\"" + text_ + "\" autofocus>");
	$("input.vcode").click();

});


$(document).on("keydown", "input.vcode", function(e) {
	if(e.keyCode === 13) {
		if($(this).parent().children()[3].textContent != 0) {var vall = this.value + " " + $(this).parent().children()[3].textContent}
		else {var vall = this.value};
		var inpt_el = this;
		$.ajax({
			type:"GET",
			url: "/solo/senddata",
			data: {
				data: vall
			},
			success: function(data) {
				inpt_el.parentElement.children[2].textContent = data.consig;
				inpt_el.parentElement.children[3].textContent = data.number;
				inpt_el.parentElement.children[4].textContent = data.comment;
				$(inpt_el).replaceWith("<td class=\"vcode\">" + data.vcode + "</td>");
			}
		})
	}
});


$(document).on("dblclick", ".number", function() {
	var text_ = $(this).text();
	$(this).replaceWith("<input class=\"number\" value=\"" + text_ + "\" style=\"width: 60px\"; autofocus>");
	$("input.number").click();

});

$(document).on("keydown", "input.number", function(e) {
	if(e.keyCode === 13) {
		// if(this.value != 0) {var vall = $(this).parent().children()[0].textContent + " " + this.value}
		// else {var vall = $(this).parent().children()[0].textContent};
		var vall = $(this).parent().children()[0].textContent + " " + this.value
		
		var inpt_el = this;
		$.ajax({
			type:"GET",
			url: "/solo/senddata",
			data: {
				data: vall
			},
			success: function(data) {
				inpt_el.parentElement.children[0].textContent = data.vcode;
				inpt_el.parentElement.children[2].textContent = data.consig;
				inpt_el.parentElement.children[4].textContent = data.comment;
				$(inpt_el).replaceWith("<td class=\"number\">" + data.number + "</td>");
			}
		})
	}
});
