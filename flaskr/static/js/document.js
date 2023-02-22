function like_document (document_id) {
    var URL = window.location.protocol+'//'+window.location.host+'/document/like/'+document_id
    var likes = document.getElementById('likes')

    fetch(URL, {method: 'POST'})
    .then((response) => response.json())
    .then((data) => likes.innerHTML=data);
}

function get_comments(document_id, offset) { 
    var URL = window.location.protocol+'//'+window.location.host+'/document/commentlist'
    var comments = document.getElementById('comments')
    var data = {'document_id': document_id, 'offset': offset}

    fetch(URL, {method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }) 
    .then((response) => response.text())
    .then((data) => comments.innerHTML = data )
}