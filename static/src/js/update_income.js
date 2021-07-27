odoo.define('budget_expense_management.myincomes', function(require){
 "use strict"


    $(document).ready(function(){

        //Call Delete request and return Get Response

        $('button[name="del_income"]').click(function() {
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function () {
                if (xhttp.readyState == XMLHttpRequest.DONE && xhttp.status == 200) {
                    window.location.href = '/my_incomes';
                }
            };
            var data = {"income_id": this.value };
            var url = "/my_incomes";
            xhttp.open("DELETE", url, true);
            xhttp.setRequestHeader('Content-type', 'application/json');
            data = JSON.stringify(data)
            xhttp.send(data);
        })

        $('td').on('click', function(e) {
            if ('text-right td_marked' == ($(this).context.className)) {
                if ($(this).context.id === 'income_acct') {
                    $(this).prop('contenteditable', false);
                    $(this).addClass('td_marked');
                    $(this).context.parentNode.cells[3].childNodes[1].style.display = "none";
                    $(this).context.parentNode.cells[3].childNodes[3].style.display = "inline-block";
                }
                if ($(this).context.id === 'income_catg') {
                    $(this).prop('contenteditable', false);
                    $(this).addClass('td_marked');
                    $(this).context.parentNode.cells[1].childNodes[1].style.display = "none";
                    $(this).context.parentNode.cells[1].childNodes[3].style.display = "inline-block";
                }
            }
                });

        $('button[name="edit_income"]').on('click', function() {
            var currentTD = $(this).closest('tr').find('td').not(':nth-child(8), :nth-child(7), :nth-child(9)');
            var td_date = $(this).closest('tr').find('td')[0];
            $('tr').removeClass('marked');
            $("td").removeClass('td_marked');
            $.each(currentTD, function () {
                          $(this).prop('contenteditable', true)
                          $(this).addClass('td_marked');
                      });
            $(this).closest('tr').find('td:first-child').click(function() {
                $('tr').find('td:first-child').prop('contenteditable', false);
                var e_new_date = td_date.children[1].innerText;
                var e_date_split = e_new_date.split('/');
                var e_date_str = e_date_split[2] + '-' + e_date_split[0] + '-' + e_date_split[1];
            /*td_date.children[0] - datepicker element */
            /*td_date.children[1] - date span element */
                td_date.children[0].value = e_date_str;
                td_date.children[0].innerText = $(this).closest('tr').find('td')[0].children[1].innerText;
                td_date.children[0].innerHTML = $(this).closest('tr').find('td')[0].children[1].innerText;
                td_date.children[0].type = 'date';
                td_date.children[0].style.display = 'inline-block';
                td_date.children[1].style.display = 'none';
                });
                td_date.parentNode.children[5].children[0].style.display='none';
                td_date.parentNode.children[5].children[1].style.display='inline-block';
                td_date.parentNode.children[5].children[1].contentEditable = false;
            });

        $('button[name="save_income"]').click(function(e){
            e.preventDefault();
            var data = {}
            var all_tds = $(this).closest('tr').find('td');
            var date_td = all_tds[0];
            var account_td= all_tds[3];
            var category_td= all_tds[1];
            var xhttp = new XMLHttpRequest();
            var currentTD = $(this).closest('tr').find('td').not(':nth-child(8), :nth-child(7), :nth-child(9)');
            $.each(currentTD, function () {
                        $(this).prop('contenteditable', false)
                        $(this).removeClass('td_marked');

                                });
            /* Toggle Edit/Save button */

            date_td.parentNode.children[5].children[1].style.display='none';
            date_td.parentNode.children[5].children[0].style.display='inline-block';
            date_td.parentNode.children[5].children[0].contentEditable = false;

            /* hide datepicker and assign its value to stae span element*/
            if (all_tds[0].firstElementChild.innerText){
                var new_date = $(this).closest('tr').find('td')[0].children[0].value;
                var date_split = new_date.split('-');
                var date_str = date_split[1] + '/' + date_split[2] + '/' + date_split[0];
                date_td.children[1].value = date_str;
                date_td.children[1].innerHTML = date_str;
                date_td.children[0].style.display = 'none';
                date_td.children[1].style.display = 'block';
            }
            xhttp.onreadystatechange = function () {

                if (xhttp.readyState == XMLHttpRequest.DONE) {
                    if (xhttp.status == 200) {
                        $(".alert").fadeTo(2000, 500).slideUp(500, function() {
                                  $(".alert").slideUp(500);
                                });
                    /* account dropdown is changed to span account elemnt while saving expense  */
                            account_td.children[1].style.display = 'none';
                            account_td.children[0].style.display = 'block';
                            account_td.children[0].value = account_td.children[1].value;
                            account_td.children[0].textContent = account_td.children[1].value;
                    /* category dropdown is changed to span category elemnt while saving expense  */
                            category_td.children[1].style.display = 'none';
                            category_td.children[0].style.display = 'block';
                            category_td.children[0].value = category_td.children[1].value;
                            category_td.children[0].textContent = category_td.children[1].value;

                    }
                }
            }
            if (account_td.children[1].value){
                var account = account_td.children[1].value;
            } else {
                var account = account_td.children[0].textContent;
            }
            if (all_tds[1].children[1].value){
                var category = all_tds[1].children[1].value;
            } else {
                var category = all_tds[1].children[0].textContent;
            }
            if (all_tds[0].firstElementChild.innerText){
                date_str = date_str;

            }
            else{
                date_str = all_tds[0].innerText;
            }
            var data = {
                'date': date_str,
                'category':category,
                'description':all_tds[2].textContent,
                'account':account,
                'amount': all_tds[4].textContent,
                'inc_id':this.value
            }
            var url = "/my_incomes";
            xhttp.open('PATCH', url, true);
            xhttp.setRequestHeader('Content-type', 'application/json');
            data = JSON.stringify(data);
            xhttp.send(data);
        });
    });
});
