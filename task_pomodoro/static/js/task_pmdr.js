// print = console.log;

var curr_pmdr = null;
var message = null;
var prev_status = null;
var prev_notification = null;
var queue_pmdr = null;
/*
{
    timestamp: 1234567890,
    remaining_time: 0,
    prefix: 'Remain: ',
    elem_done_text: 'Finished!',
    notification: 'Count down finished!'
}
*/

// This is read-only by update_remaining function
var in_pmdr = false;

function get_elem_by_name_or_id(name_or_id) {
    // This only works with Odoo 12
    var elem = $(`[name='${name_or_id}']`);
    if(elem) {
        // Found element by name
    } else {
        elem = $(`#${name_or_id}`);
    }
    return (elem && elem[0])?elem[0]:null;
}

function to_int(text) {
    // As remaining time is integer,
    // separators should be removed before parsing.
    remain_text = text.replace(/\./g, '').replace(/,/g, '');
    return parseInt(remain_text);
}

function get_button_contains(text, another) {
    var elem = $(`button:contains('${text}')`);
    if(elem && elem[0]) {
        // Found it, continue
    } else {
        var elem = $(`button:contains('${another}')`);
    }
    return (elem && elem[0])?elem[0]:null;
}

function set_remaining(timestamp_name, remain_elem_name, prefix,
        elem_done_text, notification_text) {
    timestamp = to_int(get_elem_by_name_or_id(timestamp_name).innerHTML);
    remain = to_int(get_elem_by_name_or_id(remain_elem_name).innerHTML);
    if(isNaN(remain)) {
        console.log(remain_text, 'is not a number.');
    } else if(remain > 0) {
        clear_notification();
        in_pmdr = true;
        update_remaining({
                timestamp: timestamp,
                remaining_time: remain,
                prefix: $("[name='pmdr_status']")[0].innerHTML + ' ',
                elem_done_text: elem_done_text,
                notification: notification_text
            })
    } else {
        in_pmdr = false;
    }
}

function update_remaining(next_pmdr=null) {
    var unix_now = (new Date()).getTime();

    if(next_pmdr) {
        next_pmdr.unix_stop = unix_now + next_pmdr.remaining_time*1000;
        has_current = in_pmdr && curr_pmdr != null;
        // print('Current', has_current, curr_pmdr);
        queue_pmdr = next_pmdr;
        // print('Next', queue_pmdr);
        if(has_current) {
            var newer_timer = queue_pmdr.timestamp > curr_pmdr.timestamp;
            if(newer_timer) {
                // Keep newer count down in queue
            } else {
                queue_pmdr = null;
            }
            // Next timeout will pickup new pomodoro information, thus no need
            // to do anything else
            return;
        } else { }
    } else { }

    if(queue_pmdr) {
        curr_pmdr = queue_pmdr;
        queue_pmdr = null;
    } else { }

    if(in_pmdr && curr_pmdr) {
        // Still in pomodoro cycle, continue
    } else {
        // Need this for stop button
        curr_pmdr = null;
        return;
    }

    var prefix = curr_pmdr.prefix;
    var elem_done_text = curr_pmdr.elem_done_text
    var elem = get_button_contains(prefix, elem_done_text);

    var text = '';
    if(unix_now <= curr_pmdr.unix_stop) {
        setTimeout(update_remaining, 500);

        var remaining_time = Math.floor((curr_pmdr.unix_stop - unix_now)/1000);
        var mins = Math.floor(remaining_time / 60);
        var secs = remaining_time % 60;
        var pad_secs = secs<10?'0':'';
        text = `${prefix}${mins}:${pad_secs}${secs}`;

    } else {
        message = curr_pmdr.notification;
        prev_status = $("[name='pmdr_status']")[0].innerHTML;
        notify_user();

        text = elem_done_text;
        // ========== From this point onward, curr_pmdr may not be available
        curr_pmdr = null;
    }

    if(elem) {
        // Still has element to update
        elem.innerHTML = text;
    } else {
        // Bug or design? Task > Parent (count down still running) > Child
        // (count down stop running)
        // Other page is loaded, stop the count down, user need to manually
        // update status
        curr_pmdr = null;
    }
}

function notify_user() {
    // https://developer.mozilla.org/en-US/docs/Web/API/Notification/Notification
    clear_notification();

    var options = {
        // not require user interaction because we repeat notification
        //requireInteraction: true,
    }
    try {
        pmdr_status = $("[name='pmdr_status']")[0].innerHTML;
    } catch (err) {
        return;
    }
    //console.log(prev_status);
    if(pmdr_status != prev_status) {
        return;
    }

    prev_notification = new Notification(message, options);
    if(prev_status == 'Long' || prev_status == 'Short' || prev_status == 'Focus')
    {
        setTimeout(notify_user, 5000);
    }
}

function clear_notification() {
    if (prev_notification == null) { }
    else {
        console.log('prev_noti: ', prev_notification);
        prev_notification.close();
        prev_notification = null;
    }
}
