odoo.define('budget_expense_management.transfer_form_submit', function(){ 
 "use strict" 

$(document).ready(function(){
	
	function cashTransferEndData() {
    	const XHR = new XMLHttpRequest();
	    //const form = document.getElementById("myForm");
		const FD = new FormData(form);
		
		// Define what happens on successful data submission
		XHR.addEventListener( "load", function() {
			var e = document.getElementById("dest_account_id");
			var des_account_value = e.options[e.selectedIndex].text
			var s = document.getElementById("source_account_id");
			var src_account_value = e.options[s.selectedIndex].text
            $('label[for="date"]').hide();
			$('input[name="date"]').hide();
			$('label[for="note"]').hide();
			$('input[name="note"]').hide();
			$('label[for="source_account"]').hide();
			$('#source_account').hide();
			$('label[for="amount"]').hide();
			$('#amount').hide();
			$('label[for="destination_account"]').hide();
			$('#dest_account_id').hide();
			$('#source_account_id').hide();
			$('button').hide();
			$('.alert').show();
			setTimeout(function(){ $('.alert').show(); }, 3000);
			$("#dest_account").text(des_account_value);
			$("#src_account").text(src_account_value);
			window.history.pushState({}, null, "/cash_transfer");
			window.location.href = '/budget_monthly_rpt/';
		});
		
		XHR.open( "POST", "/cash_transfer", true);
		XHR.send(FD);
	 };
	
	 const form = document.getElementById("transferCash");
	 if(typeof form !== 'undefined' && form !== null) {
		form.addEventListener( "submit", function( ) {
			event.preventDefault();
    		cashTransferEndData();
		});	
	   }
	});
	
});
