function insert_into_textarea(text) {
    textarea = document.getElementById('content')
    //IE support
    if (document.selection) {
        textarea.focus();
        sel = document.selection.createRange();
        sel.text = text;
    }
    //MOZILLA and others
    else if (textarea.selectionStart || textarea.selectionStart == '0') {
        var startPos = textarea.selectionStart;
        var endPos = textarea.selectionEnd;
        textarea.value = textarea.value.substring(0, startPos)
            + text
            + textarea.value.substring(endPos, textarea.value.length);

        textarea.focus()
        textarea.selectionEnd = endPos
        textarea.selectionStart = endPos
    } else {
        textarea.value += text;
        textarea.focus()
        cursorPos = textarea.value.length-text.length
        textarea.selectionEnd = cursorPos
        textarea.selectionStart = cursorPos
    }
}

function italic() {
    textarea = document.getElementById('content')
    cursorPos = insert_into_textarea('**')

    textarea.selectionEnd+=1
    textarea.selectionStart+=1
}

function bold() {
    textarea = document.getElementById('content')
    insert_into_textarea('****')

    textarea.selectionEnd+=2
    textarea.selectionStart+=2
}

function header(size) {
    textarea = document.getElementById('content')
    insert_into_textarea('#'.repeat(size)+' ')

    textarea.selectionEnd+=(size+1)
    textarea.selectionStart+=(size+1)
}

function bulletpoint() {
    textarea = document.getElementById('content')
    insert_into_textarea('\n- ')
    textarea.selectionEnd+=3
    textarea.selectionStart+=3
}