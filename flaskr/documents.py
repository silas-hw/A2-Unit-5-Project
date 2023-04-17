# Note: for an understanding of how the terms 'document' and 'page' relate to each other in this context refer to the design document

from flask import Blueprint, render_template, request, session, redirect, url_for, abort
import sqlite3
import markdown
import time

# local imports
from .decorators import *
from .algorithms import *
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
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT DocumentName, Description, Public, DocumentID FROM Document WHERE AccountID=?', (session['userid'],))
    documents = cursor.fetchall()

    # count how many documents the user has created
    cursor = db_conn.execute('SELECT COUNT(DocumentID) FROM Document WHERE AccountID=?', (session['userid'], ))
    num_docs = cursor.fetchone()[0]

    # retrieve the document limit based on the users current membership level
    cursor = db_conn.execute('SELECT DocumentLimit FROM MembershipLevel WHERE MembershipLevel=(SELECT MembershipLevel from User WHERE AccountID=?)', (session['userid'],))
    doc_limit = int(cursor.fetchone()[0])

    db_conn.close()

    # filter the document list if a search query has been provided
    search_query = request.args.get('q')
    if search_query:
        temp_docs = []
        for i, doc in enumerate(documents):
            if search_query in doc[0]:
                temp_docs.append(doc)
        documents=temp_docs

    return render_template('/documents/mydocuments.html', documents=documents, num_docs=num_docs, doc_limit=doc_limit, search_query=search_query, session=session)

@bp.route('/document/view/<document_id>/', methods=['GET', 'POST'])
@check_loggedin
def document_view(document_id):
    '''
    Provides the user with a view of all of the pages stored within a document
    '''

    #create an sqlite connection and retrieve the details of the document provided
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT AccountID, public, DocumentName, Description, Restricted FROM Document WHERE DocumentID=?', (document_id,))
    res = cursor.fetchone()

    # if the document doesn't exist, return user to dashboard
    if not res:
        db_conn.close()
        return render_template('errors/error_base.html', error_title='404', error_message='Document does not exist', session=session), 404

    account_id, public, title, description, restricted = res
    document_owner = True if 'userid' in session and session['userid']==account_id else False

    # if the document is private or restricted and the user doesn't own the document, or the user is not a moderator, then return an error message
    if (public==False or restricted) and not document_owner and session['access']==1:
        db_conn.close()
        return render_template('errors/error_base.html', error_title='403: Forbidden', error_message='The document is either private or restricted by a moderator', session=session), 403

    cursor = db_conn.execute('SELECT PageID, Name FROM Page WHERE DocumentID=?', (document_id,))
    pages = cursor.fetchall()

    cursor = db_conn.execute('SELECT COUNT(AccountID) FROM DocumentLike WHERE DocumentID=?', (document_id,))
    num_likes = cursor.fetchone()[0]

    db_conn.close()

    return render_template('/documents/documentview.html', pages=pages, document_owner=document_owner, document_id=document_id, title=title, description=description, num_likes=num_likes, session=session, restricted=restricted)

@bp.route('/document/add/', methods=['GET', 'POST'])
@check_loggedin
def add_document():
    '''
    Used when a user decides to create a new document
    '''

    # Check if the user has reached their document creation limit #

    # create an sqlite connection and retrieve a count of how many documents the user has created
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT COUNT(DocumentID) FROM Document WHERE AccountID=?', (session['userid'], ))
    num_docs = cursor.fetchone()[0]

    # retrieve the document limit of the users current membership level
    cursor = db_conn.execute('SELECT DocumentLimit FROM MembershipLevel WHERE MembershipLevel=(SELECT MembershipLevel FROM User WHERE AccountID=?)', (session['userid'],))
    doc_limit = cursor.fetchone()[0]

    # if doc_limit is less than 1, then it means that the users membership level has unlimited documents
    if doc_limit>0:
        # redirect the user to the my documents page if they have surpassed their document limit
        if num_docs >= doc_limit:
            db_conn.close()
            return redirect(url_for('documents.my_documents'))

    try:
        if request.method=='GET':
            db_conn.close()
            return render_template('/documents/editdocument.html', action='add', doc_title="", doc_description="", session=session)
        
        elif request.method=='POST':
            # insert the data provided in the post request into the document table
            document_name = request.form['title']
            document_description = request.form['description']
            document_public = 1 if 'public' in request.form else 0

            # data validation
            assert len(document_name)>=1, 'Document name cannot be empty'

            cursor = db_conn.execute('INSERT INTO Document (DocumentName, Description, Public, AccountID) VALUES (?, ?, ?, ?)', (document_name, document_description, document_public, session['userid']))
            db_conn.commit()
            db_conn.close()

            return redirect(url_for('documents.my_documents'))
    except AssertionError as err:
        db_conn.close()

        err_msg = err
        return render_template('/documents/editdocument.html', action='add', doc_title='', doc_description='', err_msg=err_msg, session=session)

@bp.route('/document/edit/<document_id>', methods=['GET', 'POST'])
@check_loggedin
def edit_document(document_id):
    '''
    Used when a user decides to edit a document they own
    '''
    db_conn = sqlite3.connect(config.DB_DIR)

    # check if the current users owns the document, redirecting them if they do not
    cursor = db_conn.execute('SELECT AccountID FROM Document WHERE DocumentID=?', (document_id,))
    account_id = cursor.fetchone()[0]

    if session['userid'] != account_id:
        db_conn.close()
        return render_template('errors/error_base.html', error_title='403: Forbidden', error_message="It doesn't seem like you have access to that document", session=session), 403

    cursor = db_conn.execute('SELECT * FROM Document WHERE DocumentID=?', (document_id,))
    if not cursor.fetchone():
        db_conn.close()
        return render_template('errors/error_base.html', error_title='404', error_message='Document does not exist', session=session), 404
    
    cursor = db_conn.execute('SELECT DocumentName, Description FROM Document WHERE DocumentID=?', (document_id,))
    title, description = cursor.fetchone()

    try:
        if request.method=='GET':
            db_conn.close()
            return render_template('/documents/editdocument.html', action='edit', document_id=document_id, doc_title=title, doc_description=description, session=session)
        elif request.method=='POST':
            # retrieve all the data provided in the form
            document_name = request.form['title']
            document_description = request.form['description']
            document_public = 1 if 'public' in request.form else 0

            # data validation
            assert len(document_name)>=1, 'Document name cannot be empty'

            # Update the data stored in the database about the provided document
            cursor = db_conn.execute('UPDATE Document SET DocumentName=?, Description=?, Public=? WHERE DocumentID=?', (document_name, document_description, document_public, document_id))
            db_conn.commit()
            db_conn.close()

            return redirect(url_for('documents.my_documents'))
    except AssertionError as err:
        db_conn.close()

        err_msg = err
        return render_template('/documents/editdocument.html', action='edit', document_id=document_id, doc_title=title, doc_description=description, err_msg=err_msg, session=session)

@bp.route('/document/delete/<document_id>/', methods=['GET'])
@check_loggedin
def delete_document(document_id):
    '''
    Used to delete a document and its associated pages
    '''
    
    # check if the user owns the document, redirecting them if they do not
    db_conn = sqlite3.connect(config.DB_DIR)
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
@check_moderator
def private_document(document_id):
    '''
    Allows a document to be made private by a moderator
    '''

    # update a document to change its Public field to False 
    db_conn = sqlite3.connect(config.DB_DIR)
    db_conn.execute('UPDATE Document SET Public=0 WHERE DocumentID=?', (document_id,))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('main.dashboard'))

@bp.route('/admin/document/restrict/<document_id>')
@check_loggedin
@check_moderator
def restrict_document(document_id):
    '''
    Allows a document to be restricted by a moderator.
    '''
    db_conn = sqlite3.connect(config.DB_DIR)
    db_conn.execute('UPDATE Document SET Restricted=1 WHERE DocumentID=?', (document_id,))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('main.dashboard'))

@bp.route('/admin/document/unrestrict/<document_id>')
@check_loggedin
@check_moderator
def unrestrict_document(document_id):
    '''
    Allows a document to be unrestricted by a moderator
    '''

    db_conn = sqlite3.connect(config.DB_DIR)
    db_conn.execute('UPDATE Document SET Restricted=0 WHERE DocumentID=?', (document_id,))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('main.dashboard'))

##########
# PAGES  #
##########

@bp.route('/page/view/<page_id>/', methods=['GET', 'POST'])
@check_loggedin
def page_view(page_id):
    '''
    Displays the content of a page to a user, whether it be within one of their own documents or within
    a publically shared document
    '''

    # retrieve data relating to the document that the page belongs to
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT AccountID, public FROM Document WHERE DocumentID=(SELECT DocumentID FROM Page WHERE PageID=?)', (page_id,))
    res = cursor.fetchone()

    # the page doesn't exist then redirect the user
    if not res:
        db_conn.close()
        return render_template('errors/error_base.html', error_title='404', error_message="That page doesn't exist", session=session), 404

    # check if the user should have access to the document the page belongs to, redirecting them if they do not
    account_id, public = res
    document_owner = True if 'userid' in session and session['userid']==account_id else False

    if public==False and not document_owner:
        db_conn.close()
        return render_template('errors/error_base.html', error_title='403: Forbidden', error_message="Uh oh... you don't have access to that document", session=session), 403

    # retrieve the content of the page from the database
    cursor = db_conn.execute('SELECT content FROM Page WHERE PageID=?', (page_id,))
    md_content = cursor.fetchone()[0]
    db_conn.close()
    
    # render the markdown text into HTML
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    
    return render_template('/documents/pageview.html', html_content=html_content, document_owner=document_owner, page_id=page_id, session=session)

@bp.route('/page/add/<document_id>/', methods=['GET', 'POST'])
@check_loggedin
def add_page(document_id):
    '''
    Used when a user decides to add a page to one of their documents
    '''

    # check if the user owns the document the page belongs to, returning an error message if they do not
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT AccountID FROM Document WHERE DocumentID=?', (document_id,))
    account_id = cursor.fetchone()[0]

    if 'userid' not in session or session['userid']!=account_id:
        db_conn.close()
        return 'You do not own this document'

    try:
        if request.method=='GET':
            db_conn.close()
            return render_template('/documents/editpage.html', document_id=document_id, page_content='', page_title='', action='add', session=session)

        elif request.method=='POST':
            # retrieve data provided in the form
            title = request.form['title']
            content = request.form['content']

            # data validation
            assert len(title)>=1, 'Page title cannot be empty'

            # add a new entry to the database containing the provided data
            cursor = db_conn.execute('INSERT INTO Page (Name, Content, DocumentID) VALUES (?, ?, ?)', (title, content, document_id))
            db_conn.commit()
            db_conn.close()

            return redirect(url_for('documents.document_view', document_id=document_id))
    except AssertionError as err:
        db_conn.close()

        err_msg = err()
        return render_template('/documents/editpage.html', document_id=document_id, page_content=request.form['content'], page_title='', action='add', err_msg=err_msg, session=session)

@bp.route('/page/edit/<page_id>/', methods=['GET', 'POST'])
@check_loggedin
def edit_page(page_id):
    '''
    Allows the user to edit the content of a page within one of their own documents
    '''
    
    # retrieve data relating to the document the page belongs to and the page itself
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT Document.AccountID, Page.DocumentID, Page.Name, Page.Content FROM Page INNER JOIN Document ON Page.DocumentID=Document.DocumentID WHERE PageID=? ', (page_id,))
    account_id, document_id, page_title, page_content = cursor.fetchone()

    # return an error message if the user doesn't own the document the page belongs to
    if session['userid']!=account_id:
        db_conn.close()
        return render_template('errors/error_base.html', error_title='403: Forbidden', error_message="Uh oh... you don't have access to that document", session=session), 403
    
    try:
        if request.method=='GET':
            db_conn.close()
            return render_template('/documents/editpage.html', page_id=page_id, page_content=page_content, page_title=page_title, action='edit', session=session)
        elif request.method=='POST':
            # retrieve data provided in the form
            title = request.form['title']
            content = request.form['content']

            # data validation
            assert len(title)>=1, 'Page title cannot be empty'

            # update the data stored in the database about the page ID provided
            cursor = db_conn.execute('UPDATE Page SET Name=?, Content=? WHERE PageID=?', (title, content, page_id))
            db_conn.commit()
            db_conn.close()
            
            return redirect(url_for('documents.page_view', page_id=page_id))
    except AssertionError as err:
        db_conn.close()

        err_msg = err
        return render_template('/documents/editpage.html', page_id=page_id, page_content=page_content, page_title=page_title, action='edit', err_msg=err_msg, session=session)

@bp.route('/page/delete/<page_id>/', methods=['GET'])
@check_loggedin
def delete_page(page_id):
    '''
    Used to delete a document and its associated pages
    '''
    
    # retrieve data relating to the document that the page belongs to
    db_conn = sqlite3.connect(config.DB_DIR)
    cursor = db_conn.execute('SELECT AccountID, DocumentID FROM Document WHERE DocumentID=(SELECT DocumentID FROM Page WHERE PageID=?)', (page_id,))
    page_account_id, document_id = cursor.fetchone()

    # if the page doesn't exist, redirect the user
    if not document_id:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    # if the user doesn't own the document, redirect the user
    if session['userid'] != page_account_id:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    # delete the entry in the database belonging to the page ID provided
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
    '''
    Returns a list of comment for a given community post or document
    '''

    # liking is done by JavaScript, so request data is given in the json format
    request_data = request.get_json()

    db_conn = sqlite3.connect(config.DB_DIR)
    offset = int(request_data['offset'])*config.COMMENT_LIMIT # determines how far into the table comments should be retrieved from

    # retrieve data from the corresponding table depending on whether comments for a document or comments for a community post are being retrieved
    if type=='document':
        document_id = request_data['document_id']
        cursor = db_conn.execute('SELECT CommentID FROM DocumentComment WHERE DocumentID=? LIMIT ? OFFSET ?', (document_id, config.COMMENT_LIMIT, offset))
    else:
        post_id = request_data['post_id']
        cursor = db_conn.execute('SELECT CommentID FROM CommunityPostComment WHERE PostID=? LIMIT ? OFFSET ?', (post_id, config.COMMENT_LIMIT, offset))

    comment_ids=[id[0] for id in cursor.fetchall()] # create a table of comment IDs from the comments retrieved

    # generate an SQL statement to retrieve all the comments associated with a document or post
    statement = f'SELECT * FROM Comment WHERE CommentID IN ({sql_prepared_tuple(len(comment_ids))}) ORDER BY DateEpoch DESC'

    cursor = db_conn.execute(statement, comment_ids)
    comments = cursor.fetchall()

    # convert the Unix timestamp for each comment into a human-readable date format
    comment_list = []
    for comment in comments:
        comment_id, account_id, content, dateepoch = comment

        cursor = db_conn.execute('SELECT Username FROM User WHERE AccountID=?', (account_id,))
        username = cursor.fetchone()[0]
        
        date = time.strftime('%d/%m/%Y', time.localtime(dateepoch))

        comment_list.append((comment_id, account_id, username, content, date))

    return render_template('/documents/commentlist.html', comments=comment_list, session=session)

@bp.route('/document/like/<document_id>', methods=['POST'])
@check_loggedin
def like_document(document_id):
    '''
    Likes or un-likes documents
    '''

    db_conn = sqlite3.connect(config.DB_DIR)

    # if the document doesn't exist then redirect the user
    cursor = db_conn.execute('SElECT * FROM Document WHERE DocumentID=?', (document_id,))
    if not cursor.fetchone():
        db_conn.close()
        return render_template('errors/error_base.html', error_title='404', error_message="Hmph... that document doesn't exist", session=session), 403

    cursor = db_conn.execute('SELECT * FROM DocumentLike WHERE AccountID=? AND DocumentID=?', (session['userid'], document_id))
    res = cursor.fetchone()

    # if a like by a user already exists for the document, delete the corresponding entry in the DocumnetLike table (i.e. unlike)
    if res:
        cursor = db_conn.execute('DELETE FROM DocumentLike WHERE AccountID=? AND DocumentID=?', (session['userid'], document_id))
    # if not, create an entry in the DocumentLike table
    else:
        cursor = db_conn.execute('INSERT INTO DocumentLike (AccountID, DocumentID) VALUES (?, ?)', (session['userid'], document_id))

    db_conn.commit()

    # count how many likes the document associated with the given Document ID has
    cursor = db_conn.execute('SELECT COUNT(AccountID) FROM DocumentLike WHERE DocumentID=?', (document_id,))
    num_likes = cursor.fetchone()[0]

    db_conn.close()
    
    # return the number of likes so that the screen can be updated on the client end
    return str(num_likes), 202

@bp.route('/document/comment/<document_id>/', methods=['POST'])
@check_loggedin
def comment_document(document_id):
    '''
    Adds a comment to a document
    '''
    db_conn = sqlite3.connect(config.DB_DIR)

    # if the document doesn't exist then redirect the user
    cursor = db_conn.execute('SElECT AccountID, Public FROM Document WHERE DocumentID=?', (document_id,))
    res = cursor.fetchone()
    if not res:
        db_conn.close()
        return render_template('errors/error_base.html', error_title='404', error_message="Uh oh... that document doesn't seem to exist", session=session), 403

    owner_id, public = res # unpack the retrieve data

    # if the user doesn't have access to the document then redirect them
    if session['userid']!=owner_id and public==0:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    # retrieve the data provided in the form
    content = request.form['content']
    try:
        assert content, 'comment body must be provided'
    except AssertionError:
        return redirect(url_for('documents.document_view', document_id=document_id), 304)
    
    # insert a new field into the database with the provided data
    dateepoch = int(time.time())
    cursor = db_conn.execute('INSERT INTO Comment (AccountID, Content, DateEpoch) VALUES (?, ?, ?)', (session['userid'], content, dateepoch))
    db_conn.commit()

    # get the comment ID of the new comment
    cursor = db_conn.execute('SELECT CommentID FROM Comment WHERE AccountID=? AND Content=? AND DateEpoch=?', (session['userid'], content, dateepoch))
    comment_id = cursor.fetchone()[0]

    # make a new entry in the DocumentComment table linking the document and the new comment
    cursor = db_conn.execute('INSERT INTO DocumentComment (CommentID, DocumentID) VALUES (?, ?)', (comment_id, document_id))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('documents.document_view', document_id=document_id))

@bp.route('/document/comment/delete/<comment_id>/', methods=['GET'])
@check_loggedin
def delete_comment(comment_id):
    db_conn = sqlite3.connect(config.DB_DIR)
 
    cursor = db_conn.execute('SELECT DocumentID FROM DocumentComment WHERE CommentID=?', (comment_id,))
    document_id = cursor.fetchone()[0]

    # if the user attempting to delete the comment is not an admin, verify that they are the one who created the comment
    if session['access']==1:
        cursor = db_conn.execute('SELECT AccountID FROM Comment WHERE CommentID=?', (comment_id,))
        owner_id = cursor.fetchone()[0]

        # if the user does not own the document, redirect them
        if session['userid'] != owner_id:
            db_conn.close()
            return redirect(url_for('documents.document_view', document_id=document_id), 304)
    
    # delete the comment from the DocumentComment link table and the Comment table
    db_conn.execute('DELETE FROM DocumentComment WHERE CommentID=?', (comment_id,))
    db_conn.commit()
    db_conn.execute('DELETE FROM Comment WHERE CommentID=?', (comment_id))
    db_conn.commit()

    db_conn.close()

    return redirect(url_for('documents.document_view', document_id=document_id))