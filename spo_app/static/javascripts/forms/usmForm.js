function poMo() {}

usmForm = function( options ){
  this.options = $.extend({}, options);
  this.init();
}

usmForm.prototype = {
    
    id: 0,
    url: "",
    
    init: function() {
        
        this.url = this.options.url;
        
        var scope = this;
        $('.doReveal').click(function(evt){
             scope.id = $(this).data('id');
             $.ajax({
                url: scope.url + scope.id + "/", 
                //data: $.param(args), 
                type: "GET", 
                cache: false, 
                dataType: "html", 
                success: function(data, status, response) {
                    scope.profileModal(data);   	
                }, error: function(response) {
                    //console.log("ERROR:", response);
                }
            });
        });
    },
    
    profileModal: function(data) {
        
        var scope = this;
        
        $("#Modal").html(data);
        $('#Modal').reveal({
           closeonbackgroundclick: true,              //if you click background will modal close?
           dismissmodalclass: 'close-reveal-modal',
           opened: poMo
        });
        
        
        $("#modal_form").validate({
          submitHandler: function(form) {
            var connection = new apiConnection();
            $(connection).bind('update_success', _.bind(scope.editSuccess,scope));
            $(connection).bind('update_failure', _.bind(scope.editFailure,scope));
            connection.postForm( $(form).attr("action"), form, "update" );
            return false;
          },
            errorElement: "small",
            rules: scope.options.rules 
        });
    },
    
    editSuccess: function( event, response ) {
        if (response.status == "success") {
            $("#container_" + this.id).html(response.result);
            if (response.more) {
                $("#more_" + this.id).html(response.more);
            }
        } else {
            //alert(response.message);
            alert("Sorry, there was an error.");
        }
        this.init();
        $('#Modal').trigger('reveal:close'); 
    },
    
    editFailure: function( event, response ) {
        console.log("failure");
        //alert(response);
        //$("#container_1").html(response); 
    }

}// JavaScript Document
