function like_document (document_id) {
    // likes a document when the 'like' button is pressed

    // prepare variables
    var URL = window.location.protocol+'//'+window.location.host+'/document/like/'+document_id
    var likes = document.getElementById('likes')

    // make a post request on the like route for the provided document
    // and update the like count to match the data returned
    fetch(URL, {method: 'POST'})
    .then((response) => response.json())
    .then((data) => likes.innerHTML=data);
}

function get_comments(document_id, offset) { 
    // fetches all the comments associated with a document and inserts them on to the page

    // prepare variables
    var URL = window.location.protocol+'//'+window.location.host+'/document/commentlist'
    var comments = document.getElementById('comments')
    var data = {'document_id': document_id, 'offset': offset}

    // retrieve comments list
    fetch(URL, {method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }) 
    .then((response) => response.text())
    .then((data) => comments.innerHTML = data )
}