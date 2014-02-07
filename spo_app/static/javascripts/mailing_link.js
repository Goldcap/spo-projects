// JavaScript Document

$(document).ready(function() {
     
    $(".overlay").click(function(e){
        e.preventDefault();
        parent.postMessage("close", "*");
    });
    
    $(".ko-submitbutton").click(function(e){
        $("#ko-submit").submit();
    });
    
});


    
    
