odoo.define('budget_expense_management.change_month', function(require) {
	 "use strict"
	$(document).ready(function() {
		function update_summary(month_name,year){
			var xhttp = new XMLHttpRequest();
			xhttp.onload = function () {
			if (xhttp.readyState == XMLHttpRequest.DONE && xhttp.status == 200) {
				$('body').html(xhttp.responseText);
				}
			};
			var url = "/budget_monthly_rpt/?current_month=" + month_name;
			url += "&current_year="+ year;
			xhttp.open("GET", url, true);
			xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			xhttp.send();
		};

		$("#change_month").change(function() {
			var month_name = $("#change_month").val();
			var b_year = $("#change_year").val();
			sessionStorage.setItem("SelItem", month_name);
			update_summary(month_name, b_year);
		});
		$("#change_year").change(function() {
			var month_name = $("#change_month").val();
			var s_year = $("#change_year").val();
			sessionStorage.setItem("SelYear", s_year);
			update_summary(month_name, s_year);
		});

	});


	window.onload = function() {
	    var selItem = sessionStorage.getItem("SelItem");
		var SelYear = sessionStorage.getItem("SelYear");
		if (selItem) {
		 var curr_month = $('input[id="current_month"]').attr('value');
		 $('#change_month').val(curr_month);
		}
		if (SelYear) {
		 var curr_year = $('input[id="current_year"]').attr('value');
		 $('#change_year').val(curr_year);
		}
		var Year = sessionStorage.getItem("Year");
		if (Year) {
		 var c_year = $('input[id="c_year"]').attr('value');
		 $('#change_annual_year').val(c_year);
		}
    }

});
