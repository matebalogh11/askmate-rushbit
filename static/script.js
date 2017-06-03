
function hideMe_q_submit() {
    var textbox = document.getElementById('q_comment_submit');
    var textboxstyle = window.getComputedStyle(textbox, null);
    if (textboxstyle['display'] === 'none') {
        textbox.style.display = 'block';
    } else {
        textbox.style.display = 'none';
    }
}

function hideMe_q_edit(element_id) {
    var textbox = document.getElementById(element_id);
    var textboxstyle = window.getComputedStyle(textbox, null);
    if (textboxstyle['display'] === 'none') {
        textbox.style.display = 'block';
    } else {
        textbox.style.display = 'none';
    }
}

function hideMe_a_submit(element_id) {
    var textbox = document.getElementById(element_id);
    var textboxstyle = window.getComputedStyle(textbox, null);
    if (textboxstyle['display'] === 'none') {
        textbox.style.display = 'block';
    } else {
        textbox.style.display = 'none';
    }
}

function hideMe_a_edit(element_id) {
    var textbox = document.getElementById(element_id);
    var textboxstyle = window.getComputedStyle(textbox, null);
    if (textboxstyle['display'] === 'none') {
        textbox.style.display = 'block';
    } else {
        textbox.style.display = 'none';
    }
}
