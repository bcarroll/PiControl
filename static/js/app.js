/*
 *
 *
 *
 */

$.ajaxSetup({'cache' : false});

$(document).ready(function () {
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