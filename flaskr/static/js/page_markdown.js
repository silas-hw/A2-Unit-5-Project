function insert_into_textarea(text) {
    // insert a given string into the textarea at the current position of the cursor
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

        textarea.focus() // ensures the textarea remains selected so the user can continue typing
        textarea.selectionEnd = endPos
        textarea.selectionStart = endPos
    } else {
        textarea.value += text;
        textarea.focus()// ensures the textarea remains selected so the user can continue typing
        cursorPos = textarea.value.length-text.length
        textarea.selectionEnd = cursorPos
        textarea.selectionStart = cursorPos
    }
}

function italic() {
    // add markup for italic text into textarea
    textarea = document.getElementById('content')
    cursorPos = insert_into_textarea('**')

    textarea.selectionEnd+=1
    textarea.selectionStart+=1
}

function bold() {
    // add markup for bold text into textarea
    textarea = document.getElementById('content')
    insert_into_textarea('****')

    textarea.selectionEnd+=2
    textarea.selectionStart+=2
}

function header(size) {
    // add markup for a header of a given size into the textarea
    textarea = document.getElementById('content')
    insert_into_textarea('#'.repeat(size)+' ')

    textarea.selectionEnd+=(size+1)
    textarea.selectionStart+=(size+1)
}

function bulletpoint() {
    // add markup for a bulletpoint into the textarea
    textarea = document.getElementById('content')
    insert_into_textarea('\n- ')
    textarea.selectionEnd+=3
    textarea.selectionStart+=3
}