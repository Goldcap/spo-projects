// JavaScript Document
apiConnection = function( options ){
  this.options = $.extend({
    format: 'json'
	}, options);
	this.init();
}

apiConnection.prototype = {

  event: null,
  
  init: function() {
  },
  
  get: function( url, args, event ) {
    
    this.event = event;
    
    var data = $.extend( args , this.options );
    
    $.ajax({
			type: 'GET',
			url: url,
			data: data,
			dataType: 'json',
			timeout: _.bind(this.onTimeout, this),
			complete: _.bind(this.onComplete, this),
			success: _.bind(this.onSuccess, this),
			error: _.bind(this.onFailure, this)
		});
    
  },
  
  post: function( url, args, event ) {
    
    this.event = event;
    
    var data = $.extend( args , this.options);
    
    $.ajax({
			type: 'POST',
			url: url,
			data: data,
			timeout: _.bind(this.onTimeout, this),
			complete: _.bind(this.onComplete, this),
			success: _.bind(this.onSuccess, this),
			error: _.bind(this.onFailure, this)
		});
  },
  
  postForm: function( url, form, event ) {
    
    this.event = event;
    
    if (url == null) {
      url = $(form).attr("action");
    }
    
    $.ajax({
			type: 'POST',
			url: url,
			data: $(form).serialize(),
			dataType: 'json',
			timeout: _.bind(this.onTimeout, this),
			complete: _.bind(this.onComplete, this),
			success: _.bind(this.onSuccess, this),
			error: _.bind(this.onFailure, this)
		});
  },
  
  postRest: function (url, form, event) {
    
    var values = {};
    
    $.each($(form).serializeArray(), function(i, field) {
      values[field.name] = field.value;
    })
    
    this.send( url, values, $(form).attr("method"), event );

  },
  
  send: function( url, args, method, event ) {
    
    this.event = event;
    
    if (method == undefined)
      method = 'PATCH'
      
    var data = $.extend( args, this.options );
    var postVars = JSON.stringify(data);
     
    $.ajax({
			type: method,
			url: url,
			data: postVars,
			contentType: 'application/json',
			dataType: 'json',
			timeout: _.bind(this.onTimeout, this),
			complete: _.bind(this.onComplete, this),
			success: _.bind(this.onSuccess, this),
			error: _.bind(this.onFailure, this)
		});
  },
  
  onComplete: function(response) {
    //console.log(this.event+'_complete');
    $(this).trigger(this.event+'_complete', response);
  },
  
  onSuccess: function(response) {
    //console.log(this.event+'_success');
    $(this).trigger(this.event+'_success', response);
  },
  
  onFailure: function(response) {
    //console.log(this.event+'_failure');
   $(this).trigger(this.event+'_failure', response);
  },
  
  onTimeout: function(response) {
    //console.log(this.event+'_timeout');
   $(this).trigger(this.event+'_timeout', response);
  }
  
}