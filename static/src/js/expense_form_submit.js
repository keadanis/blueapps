odoo.define('budget_expense_management.expense_form_submit', function(){ 
 "use strict" 

$(document).ready(function(){
	function sendData() {
    	const XHR = new XMLHttpRequest();
		const FD = new FormData(form);
		XHR.onload = function () {
			if (XHR.readyState == XMLHttpRequest.DONE && XHR.status == 200) {
				const GXHR = new XMLHttpRequest();
				GXHR.addEventListener("load", function() {
					$('body').html(GXHR.responseText);
				});
                GXHR.open( "GET", "/my_expenses", true);
                GXHR.send();
				window.history.pushState({}, null, "/my_expenses");
				}
			}
		XHR.open( "POST", "/my_expenses", true);
		XHR.send(FD);
	
	};
	 const form = document.getElementById("myForm");
	 if(typeof form !== 'undefined' && form !== null) {
		form.addEventListener( "submit", function( ) {
    		event.preventDefault();
    		sendData();
		});	
	   }
	});
	
});
