function search() {
    // inserts a search value into the URL parameters and refreshes the page
    var url = new URL (window.location)
    console.log(url)
    query = document.getElementById('search').value

    if(url.href.includes('q')){
        url.searchParams.set('q', query)
    } else {
        url.searchParams.append('q', query)
    }
    window.location.href = url
}