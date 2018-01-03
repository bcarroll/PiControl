/*
 *
 *
 *
 */

$.ajaxSetup({'cache' : false});

$(document).ready(function () {
	$("#sidebar").mCustomScrollbar({
         theme: "minimal"
    });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
});

function ajax_get(resource, element){
	$.get(resource, function(result){$(element).text(result);});
}

function ajax_get_html(resource, element){
	$.get(resource, function(result){$(element).html(result);});
}

function dump(arr,level) {
	/**
	 * Function : dump()
	 * Arguments: The data - array,hash(associative array),object
	 *    The level - OPTIONAL
	 * Returns  : The textual representation of the array.
	 * This function was inspired by the print_r function of PHP.
	 * This will accept some data as the argument and return a
	 * text that will be a more readable version of the
	 * array/hash/object that is given.
	 * Docs: http://www.openjs.com/scripts/others/dump_function_php_print_r.php
	 */
	var dumped_text = "";
	if(!level) level = 0;
	
	//The padding given at the beginning of the line.
	var level_padding = "";
	for(var j=0;j<level+1;j++) level_padding += "    ";
	
	if(typeof(arr) == 'object') { //Array/Hashes/Objects 
		for(var item in arr) {
			var value = arr[item];
			
			if(typeof(value) == 'object') { //If it is an array,
				dumped_text += level_padding + "'" + item + "' ...\n";
				dumped_text += dump(value,level+1);
			} else {
				dumped_text += level_padding + "'" + item + "' => \"" + value + "\"\n";
			}
		}
	} else { //Stings/Chars/Numbers etc.
		dumped_text = "===>"+arr+"<===("+typeof(arr)+")";
	}
	return dumped_text;
}