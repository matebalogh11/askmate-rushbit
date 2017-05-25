function hideMe() {
    debugger;
    var textbox = document.getElementById('q_comment');
    if (textbox.style.display === 'none') {
        textbox.style.display = 'block';
    } else {
        textbox.style.display = 'none';
    }
}