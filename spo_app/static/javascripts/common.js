/**
 * Created with PyCharm.
 * User: user
 * Date: 5/29/13
 * Time: 11:51 AM
 * To change this template use File | Settings | File Templates.
 */
function validateEmail(sEmail) {
    var filter = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
    if (filter.test(sEmail)) {
        return true;
    }
    else {
        return false;
    }
}

$("span.custom.checkbox").click(function(){
    var chkbox = $(this).parent().children("input:hidden");
    var chkval = chkbox.val()=="1"?"0":"1";
    chkbox.val(chkval);
});

$("span.custom.radio").click(function(){
    $(this).parent().parent().parent().find("td span.custom.radio").filter(function(e) {
        if($(this).hasClass('checked')){
            $(this).removeClass('checked');
        }
    }) ;
    var chkbox = $(this).parent().parent().parent().children("input:hidden");
    var chkval = chkbox.val()=="1"?"0":"1";
    chkbox.val(chkval);
    $(this).addClass('checked');
});

function submit_page(val)
{
    $("#id_GotoNextPage").val(val);
    var is_valid = true;
    
    if(is_valid){
        $("#main_form").submit();
        return true;
    }
    return false;
}

function removeImage( type, image ) {
    if (confirm("Are you sure you want to delete this image?")) {
        ajax_req = $.ajax({
            url: '/image_manager/delete/',
            type: "POST",
            data: {
                    "atype":type,
                    "image":image
                },
            success: function(data) {
                $("#tr_"+type+"_"+data.image+"."+type).remove();
                console.log(type);
                console.log($("tr."+type).length);
                if ($("tr."+type).length == 1) {
                    $("#tr_"+type+"_0"+"."+type).fadeIn();
                }
                linkImages();
            },
            error: function(data) {
            }
        });
    }
}

function linkImages() {
    
    $(".image").unbind( "click" );
    $(".overlay").unbind( "click" );
    $(".inline-editable-checkbox").unbind( "click" );
    
    $(".image").mouseover(function(e){
        $(this).prev().show().delay(3000).fadeOut();
        //addClass("image_rollover");
    });
    
    $(".image").click(function(e){
        var type = $(this).attr("type");
        var image = this.id.replace(type+"_","");
        removeImage(type, image);
    });
    
    $(".overlay").click(function(e){
        var type = $(this).attr("type");
        var image = this.id.replace(type+"_","");
        removeImage(type, image);
    });
    
    $('.inline-editable-checkbox').click(function(e){
        
        e.preventDefault();
        
        var pk = $(this).data("pk");
        var value = ($(this).text() == "Yes") ? 0 : 1;
        
        var scope = this;
        ajax_req = $.ajax({
            url: '/image_manager/info/',
            type: "POST",
            data: {
                    "name":"status",
                    "pk":pk,
                    "value":value
                },
            success: function(response) {
                if (response.status == 'success') {
                    if (response.value == 1) {
                        $(scope).text('Yes');
                    } else {
                        $(scope).text('No');
                    }
                }
            },
            error: function(data) {
            }
        });
    });
    
    $('.inline-editable').editable({
        success: function(response, newValue) {
            if(response.status == 'error') return response.msg; //msg will be shown in editable form
        }
    });

    
}

$(document).ready(function() {
    $.fn.editable.defaults.mode = 'inline';
    
    linkImages();
    
});