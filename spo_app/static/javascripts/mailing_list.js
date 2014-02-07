// JavaScript Document

jQuery(document).ready(function($) {
    
    // Code that uses jQuery's $ can follow here.
    $(".usm-showform").click(function(e){
        e.preventDefault();
        $("#floater").fadeIn();
    });
    
    addEventListener("message", receiveMessage, false);
    
    function receiveMessage(event) { 
        if (event.data == 'close') {
            $("#floater").fadeOut();
        }
    }    
});

