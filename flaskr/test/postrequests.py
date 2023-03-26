import requests
domain = 'http://localhost:5000/'

accounts = {
    '1':{
        'email':'jeff@gmail.com',
        'pass':'TestPass12!'
    },
    '2':{
        'email':'test2@test.com',
        'pass':'Password123'
    },
}

def add_page3():
    url = domain+'login/'
    data = accounts['2']
    requests.post(url, json=data)

    url = domain+'page/add/1/'
    data = {
        'title':'Morpork',
        'content':''
    }
    requests.post(url, json=data)
    
    url = domain+'logout/'
    requests.get(url)

def add_page4():
    url = domain+'login/'
    data = accounts['1']
    requests.post(url, json=data)

    url = domain+'page/add/99/'
    data = {
        'title':'Morpork',
        'content':''
    }
    requests.post(url, json=data)
    
    url = domain+'logout/'
    requests.get(url)

def comment_document3():
    url = domain+'login/'
    data = accounts['2']
    requests.post(url, json=data)

    url = domain+'document/comment/1/'
    data = {
        'content':'WOw!!!!'
    }
    requests.post(url, json=data)
    requests.get(domain+'logout/')

def comment_document4():
    url = domain+'login/'
    data = accounts['2']
    requests.post(url, json=data)

    url = domain+'document/comment/99/'
    data = {
        'content':'Cant wait for this stuff to be finished'
    }
    requests.post(url, json=data)
    requests.get(domain+'logout/')

def like_document2():
    url = domain+'login/'
    data = accounts['2']
    requests.post(url, json=data)

    url = domain+'document/like/1'
    requests.post(url)

    requests.post(domain+'logout/')

def like_document3():
    url = domain+'login/'
    data = accounts['2']
    requests.post(url, json=data)

    url = domain+'document/like/999'
    requests.post(url)

    requests.post(domain+'logout/')

def like_document4():
    url = domain+'login/'
    data = accounts['2']
    requests.post(url, json=data)

    url = domain+'document/like/'
    requests.post(url)

    requests.post(domain+'logout/')

def create_newsletter4():
    url = domain+'login/'
    data = accounts['2']
    requests.post(url, json=data)

    url = domain+'admin/newsletter/create/'
    data = {
        'subject':'Welcome',
        'content':'HAHAAH I HAVE BROKEN INTO THE SYSTEM',
        'send_date':'2050-10-02'
    }
    requests.post(url, json=data)
    
    requests.post(domain+'logout/')

def edit_newsletter3():
    url = domain+'login/'
    data = accounts['2']
    requests.post(url, json=data)

    url = domain+'admin/newsletter/edit/1'
    data = {
        'subject':'Welcome',
        'content':'HAHAAH I HAVE BROKEN INTO THE SYSTEM',
        'send_date':'2024-04-92'
    }
    requests.post(url, json=data)
    
    requests.post(domain+'logout/')

def edit_newsletter4():
    url = domain+'login/'
    data = accounts['1']
    requests.post(url, json=data)

    url = domain+'admin/newsletter/edit/99'
    data = {
        'subject':'Welcome',
        'content':'Hmph this newsletter should not exist',
        'send_date':'2024-04-92'
    }
    requests.post(url, json=data)
    
    requests.post(domain+'logout/')


if __name__ == '__main__':
    edit_newsletter4()
    