function hideMe() {
    var textbox = document.getElementById('q_comment');
    var textboxstyle = window.getComputedStyle(textbox, null);
    if (textboxstyle['display'] === 'none') {
        textbox.style.display = 'block';
    } else {
        textbox.style.display = 'none';
    }
}