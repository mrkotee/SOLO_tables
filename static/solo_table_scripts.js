

var analog_vcodes_dict = {};
var analog_vcodes_counter_dict = {};

$(document).ready(function(){
	var comments = $(".comment");
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
