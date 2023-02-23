# Note: for an understanding of how the terms 'document' and 'page' relate to each other in this context refer to the design document

from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3
import markdown
import time

# local imports
from .decorators import *
from .config import Config as config

bp = Blueprint('documents', __name__)

#############
# DOCUMENTS #
#############

@bp.route('/mydocuments/', methods=['GET'])
@check_loggedin
def my_documents():
    '''
    Lists all of the users documents
    '''

    # create an sqlite connection and retrieve a list of the currently logged in users documents
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT DocumentName, Description, Public, DocumentID FROM Document WHERE AccountID=?', (session['userid'],))
    documents = cursor.fetchall()

    # count how many documents the user has created
    cursor = db_conn.execute('SELECT COUNT(DocumentID) FROM Document WHERE AccountID=?', (session['userid'], ))
    num_docs = cursor.fetchone()[0]
    db_conn.close()

    # filter the document list if a search query has been provided
    search_query = request.args.get('q')
    if search_query:
        temp_docs = []
        for i, doc in enumerate(documents):
            if search_query in doc[0]:
                temp_docs.append(doc)
        documents=temp_docs

    return render_template('/documents/mydocuments.html', documents=documents, num_docs=num_docs, search_query=search_query)

@bp.route('/document/view/<document_id>/', methods=['GET', 'POST'])
@check_loggedin
def document_view(document_id):
    '''
    Provides the user with a view of all of the pages stored within a document
    '''

    #create an sqlite connection and retrieve the details of the document provided
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT AccountID, public, DocumentName, Description FROM Document WHERE DocumentID=?', (document_id,))
    res = cursor.fetchone()

    # if the document doesn't exist, return user to dashboard
    if not res:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    account_id, public, title, description = res
    document_owner = True if 'userid' in session and session['userid']==account_id else False

    if public==False and not document_owner:
        db_conn.close()
        return 'the document you attempted to view is private'

    cursor = db_conn.execute('SELECT PageID, Name FROM Page WHERE DocumentID=?', (document_id,))
    pages = cursor.fetchall()

    cursor = db_conn.execute('SELECT COUNT(AccountID) FROM DocumentLike WHERE DocumentID=?', (document_id,))
    num_likes = cursor.fetchone()[0]

    db_conn.close()

    return render_template('/documents/documentview.html', pages=pages, document_owner=document_owner, document_id=document_id, title=title, description=description, num_likes=num_likes, session=session)

@bp.route('/document/add/', methods=['GET', 'POST'])
@check_loggedin
def add_document():
    '''
    Used when a user decides to create a new document
    '''

    # Check if the user has reached their document creation limit #

    # create an sqlite connection and retrieve a count of how many documents the user has created
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT COUNT(DocumentID) FROM Document WHERE AccountID=?', (session['userid'], ))
    num_docs = cursor.fetchone()[0]

    # retrieve the document limit of the users current membership level
    cursor = db_conn.execute('SELECT DocumentLimit FROM MembershipLevel WHERE MembershipLevel=(SELECT MembershipLevel FROM User WHERE AccountID=?)', (session['userid'],))
    doc_limit = cursor.fetchone()[0]

    # if doc_limit is less than 1, then it means that the users membership level has unlimited documents
    if doc_limit>0:
        # redirect the user to the my documents page if they have surpassed their document limit
        if num_docs == doc_limit:
            db_conn.close()
            return redirect(url_for('documents.my_documents'))

    if request.method=='GET':
        db_conn.close()
        return render_template('/documents/editdocument.html', action='add', doc_title="", doc_description="")
    
    elif request.method=='POST':
        # insert the data provided in the post request into the document table
        document_name = request.form['title']
        document_description = request.form['description']
        document_public = 1 if 'public' in request.form else 0

        cursor = db_conn.execute('INSERT INTO Document (DocumentName, Description, Public, AccountID) VALUES (?, ?, ?, ?)', (document_name, document_description, document_public, session['userid']))
        db_conn.commit()
        db_conn.close()

        return redirect(url_for('documents.my_documents'))

@bp.route('/document/edit/<document_id>', methods=['GET', 'POST'])
@check_loggedin
def edit_document(document_id):
    '''
    Used when a user decides to edit a document they own
    '''
    db_conn = sqlite3.connect(config.db_dir)

    cursor = db_conn.execute('SELECT AccountID FROM Document WHERE DocumentID=?', (document_id,))
    account_id = cursor.fetchone()[0]

    if session['userid'] != account_id:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    if request.method=='GET':
        cursor = db_conn.execute('SELECT DocumentName, Description FROM Document WHERE DocumentID=?', (document_id,))
        title, description = cursor.fetchone()
        return render_template('/documents/editdocument.html', action='edit', document_id=document_id, doc_title=title, doc_description=description)
    elif request.method=='POST':
        document_name = request.form['title']
        document_description = request.form['description']
        document_public = 1 if 'public' in request.form else 0

        cursor = db_conn.execute('UPDATE Document SET DocumentName=?, Description=?, Public=? WHERE DocumentID=?', (document_name, document_description, document_public, document_id))
        db_conn.commit()
        db_conn.close()

        return redirect(url_for('documents.my_documents'))

@bp.route('/document/delete/<document_id>/', methods=['GET'])
@check_loggedin
def delete_document(document_id):
    '''
    Used to delete a document and its associated pages
    '''
    
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT AccountID FROM Document WHERE DocumentID=?', (document_id,))
    doc_account_id = cursor.fetchone()[0]

    if session['userid'] != doc_account_id:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    cursor = db_conn.execute('DELETE FROM Page WHERE DocumentID=?', (document_id,))
    db_conn.commit()
    cursor = db_conn.execute('DELETE FROM Document WHERE DocumentID=?', (document_id,))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('documents.my_documents'))

@bp.route('/admin/privatedoc/<document_id>/', methods=['GET'])
@check_loggedin
def private_document(document_id):
    if session['access'] == 2 or session['access'] == 3:
        db_conn = sqlite3.connect(config.db_dir)
        db_conn.execute('UPDATE Document SET Public=0 WHERE DocumentID=?', (document_id,))
        db_conn.commit()
        db_conn.close()

        return redirect(url_for('main.dashboard'))

#############
# PAGES     #
#############

@bp.route('/page/view/<page_id>/', methods=['GET', 'POST'])
@check_loggedin
def page_view(page_id):
    '''
    Displays the content of a page to a user, whether it be within one of their own documents or within
    a publically shared document
    '''

    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT AccountID, public FROM Document WHERE DocumentID=(SELECT DocumentID FROM Page WHERE PageID=?)', (page_id,))
    res = cursor.fetchone()

    if not res:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    account_id, public = res
    document_owner = True if 'userid' in session and session['userid']==account_id else False

    if public==False and not document_owner:
        db_conn.close()
        return 'the document you attempted to view is private'

    cursor = db_conn.execute('SELECT content FROM Page WHERE PageID=?', (page_id,))
    md_content = cursor.fetchone()[0]
    db_conn.close()
    
    html_content = markdown.markdown(md_content)
    
    return render_template('/documents/pageview.html', html_content=html_content, document_owner=document_owner, page_id=page_id)

@bp.route('/page/add/<document_id>/', methods=['GET', 'POST'])
@check_loggedin
def add_page(document_id):
    '''
    Used when a user decides to add a page to one of their documents
    '''

    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT AccountID FROM Document WHERE DocumentID=?', (document_id,))
    account_id = cursor.fetchone()[0]

    if 'userid' not in session or session['userid']!=account_id:
        db_conn.close()
        return 'You do not own this document'

    if request.method=='GET':
        db_conn.close()
        return render_template('/documents/editpage.html', document_id=document_id, page_content='', page_title='', action='add')

    elif request.method=='POST':
        title = request.form['title']
        content = request.form['content']

        cursor = db_conn.execute('INSERT INTO Page (Name, Content, DocumentID) VALUES (?, ?, ?)', (title, content, document_id))
        db_conn.commit()
        db_conn.close()

        return redirect(url_for('documents.document_view', document_id=document_id))

@bp.route('/page/edit/<page_id>/', methods=['GET', 'POST'])
@check_loggedin
def edit_page(page_id):
    '''
    Allows the user to edit the content of a page within one of their own documents
    '''
    
    db_conn = sqlite3.connect(config.db_dir)
    # need to add document id here
    cursor = db_conn.execute('SELECT Document.AccountID, Page.DocumentID, Page.Name, Page.Content FROM Page INNER JOIN Document ON Page.DocumentID=Document.DocumentID WHERE PageID=? ', (page_id,))
    account_id, document_id, page_title, page_content = cursor.fetchone()

    if session['userid']!=account_id:
        db_conn.close()
        return 'You do not own the document this page is attached to'

    if request.method=='GET':
        db_conn.close()
        return render_template('/documents/editpage.html', page_id=page_id, page_content=page_content, page_title=page_title, action='edit')
    elif request.method=='POST':
        title = request.form['title']
        content = request.form['content']

        cursor = db_conn.execute('UPDATE Page SET Name=?, Content=? WHERE PageID=?', (title, content, page_id))
        db_conn.commit()
        db_conn.close()
        
        return redirect(url_for('documents.page_view', page_id=page_id))

@bp.route('/page/delete/<page_id>/', methods=['GET'])
@check_loggedin
def delete_page(page_id):
    '''
    Used to delete a document and its associated pages
    '''
    
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SELECT AccountID, DocumentID FROM Document WHERE DocumentID=(SELECT DocumentID FROM Page WHERE PageID=?)', (page_id,))
    page_account_id, document_id = cursor.fetchone()

    if session['userid'] != page_account_id:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    cursor = db_conn.execute('DELETE FROM Page WHERE PageID=?', (page_id,))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('documents.document_view', document_id=document_id))

#########################
# COMMENTING AND LIKING #
#########################

@bp.route('/<type>/commentlist', methods=['POST'])
@check_loggedin
def comment_list(type):

    request_data = request.get_json()

    db_conn = sqlite3.connect(config.db_dir)
    offset = int(request_data['offset'])*config.num_comments

    if type=='document':
        document_id = request_data['document_id']
        cursor = db_conn.execute('SELECT CommentID FROM DocumentComment WHERE DocumentID=? LIMIT ? OFFSET ?', (document_id, config.num_comments, offset))
    else:
        post_id = request_data['post_id']
        cursor = execute('SELECT CommentID FROM CommunityPostComment WHERE PostID=? LIMIT ? OFFSET ?', (post_id, config.num_comments, offset))

    comment_ids=[id[0] for id in cursor.fetchall()]

    statement_tuple = '?,'*len(comment_ids)
    statement_tuple = statement_tuple[:len(statement_tuple)-1]
    statement = f'SELECT * FROM Comment WHERE CommentID IN ({statement_tuple}) ORDER BY DateEpoch DESC'

    cursor = db_conn.execute(statement, comment_ids)
    comments = cursor.fetchall()

    comment_list = []
    for comment in comments:
        comment_id, account_id, content, dateepoch = comment

        cursor = db_conn.execute('SELECT Username FROM User WHERE AccountID=?', (account_id,))
        username = cursor.fetchone()[0]
        
        date = time.strftime('%d/%m/%Y', time.localtime(dateepoch))

        comment_list.append((account_id, username, content, date))

    return render_template('/documents/commentlist.html', comments=comment_list)

@bp.route('/document/like/<document_id>/', methods=['POST'])
@check_loggedin
def like_document(document_id):
    '''
    Likes or un-likes documents
    '''

    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('SElECT * FROM DocumentLike WHERE AccountID=? AND DocumentID=?', (session['userid'], document_id))
    res = cursor.fetchone()

    if res:
        cursor = db_conn.execute('DELETE FROM DocumentLike WHERE AccountID=? AND DocumentID=?', (session['userid'], document_id))
    else:
        cursor = db_conn.execute('INSERT INTO DocumentLike (AccountID, DocumentID) VALUES (?, ?)', (session['userid'], document_id))

    db_conn.commit()

    cursor = db_conn.execute('SELECT COUNT(AccountID) FROM DocumentLike WHERE DocumentID=?', (document_id,))
    num_likes = cursor.fetchone()[0]

    db_conn.close()

    return str(num_likes), 202

@bp.route('/document/comment/<document_id>/', methods=['POST'])
@check_loggedin
def comment_document(document_id):
    '''
    Adds a comment to a document
    '''

    content = request.form['content']
    print(len(content))
    if len(content)==0:
        redirect(url_for('documents.document_view', document_id=document_id)), 304
    dateepoch = int(time.time())
    
    db_conn = sqlite3.connect(config.db_dir)
    cursor = db_conn.execute('INSERT INTO Comment (AccountID, Content, DateEpoch) VALUES (?, ?, ?)', (session['userid'], content, dateepoch))
    db_conn.commit()

    cursor = db_conn.execute('SELECT CommentID FROM Comment WHERE AccountID=? AND Content=? AND DateEpoch=?', (session['userid'], content, dateepoch))
    comment_id = cursor.fetchone()[0]

    cursor = db_conn.execute('INSERT INTO DocumentComment (CommentID, DocumentID) VALUES (?, ?)', (comment_id, document_id))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('documents.document_view', document_id=document_id))