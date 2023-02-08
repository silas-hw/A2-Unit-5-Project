# Note: for an understanding of how the terms 'document' and 'page' relate to each other in this context refer to the design document

from tabnanny import check
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3
import markdown

from .decorators import *

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

    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT DocumentName, Description, Public, DocumentID FROM LoreDocument WHERE AccountID=?', (session['userid'],))
    documents = cursor.fetchall()

    cursor = db_conn.execute('SELECT COUNT(DocumentID) FROM LoreDocument WHERE AccountID=?', (session['userid'], ))
    num_docs = cursor.fetchone()[0]
    db_conn.close()

    search_query = request.args.get('q')
    if search_query:
        temp_docs = []
        for i, doc in enumerate(documents):
            print(doc[0], search_query in doc[0])
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

    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT AccountID, public, DocumentName, Description FROM LoreDocument WHERE DocumentID=?', (document_id,))
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

    cursor = db_conn.execute('SELECT PageID, Name FROM LorePage WHERE DocumentID=?', (document_id,))
    pages = cursor.fetchall()

    db_conn.close()

    return render_template('/documents/documentview.html', pages=pages, document_owner=document_owner, document_id=document_id, title=title, description=description, session=session)

@bp.route('/document/add/', methods=['GET', 'POST'])
@check_loggedin
def add_document():
    '''
    Used when a user decides to create a new document
    '''

    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT COUNT(DocumentID) FROM LoreDocument WHERE AccountID=?', (session['userid'], ))
    num_docs = cursor.fetchone()[0]

    cursor = db_conn.execute('SELECT DocumentLimit FROM MembershipLevel WHERE MembershipLevel=(SELECT MembershipLevel FROM Membership WHERE AccountID=?)', (session['userid'],))
    doc_limit = cursor.fetchone()[0]

    if doc_limit>0:
        if num_docs == doc_limit:
            db_conn.close()
            return redirect(url_for('documents.my_documents'))

    if request.method=='GET':
        db_conn.close()
        return render_template('/documents/editdocument.html', action='add', doc_title="", doc_description="")
    elif request.method=='POST':
        document_name = request.form['title']
        document_description = request.form['description']
        document_public = 1 if 'public' in request.form else 0

        cursor = db_conn.execute('INSERT INTO LoreDocument (DocumentName, Description, Public, AccountID) VALUES (?, ?, ?, ?)', (document_name, document_description, document_public, session['userid']))
        db_conn.commit()
        db_conn.close()

        return redirect(url_for('documents.my_documents'))

@bp.route('/document/edit/<document_id>', methods=['GET', 'POST'])
@check_loggedin
def edit_document(document_id):
    '''
    Used when a user decides to edit a document they own
    '''
    db_conn = sqlite3.connect('./db/prototype.db')

    cursor = db_conn.execute('SELECT AccountID FROM LoreDocument WHERE DocumentID=?', (document_id,))
    account_id = cursor.fetchone()[0]

    if session['userid'] != account_id:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    if request.method=='GET':
        cursor = db_conn.execute('SELECT DocumentName, Description FROM LoreDocument WHERE DocumentID=?', (document_id,))
        title, description = cursor.fetchone()
        return render_template('/documents/editdocument.html', action='edit', document_id=document_id, doc_title=title, doc_description=description)
    elif request.method=='POST':
        document_name = request.form['title']
        document_description = request.form['description']
        document_public = 1 if 'public' in request.form else 0

        cursor = db_conn.execute('UPDATE LoreDocument SET DocumentName=?, Description=?, Public=? WHERE DocumentID=?', (document_name, document_description, document_public, document_id))
        db_conn.commit()
        db_conn.close()

        print('done')

        return redirect(url_for('documents.my_documents'))

@bp.route('/document/delete/<document_id>/', methods=['GET'])
@check_loggedin
def delete_document(document_id):
    '''
    Used to delete a document and its associated pages
    '''
    
    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT AccountID FROM LoreDocument WHERE DocumentID=?', (document_id,))
    doc_account_id = cursor.fetchone()[0]

    if session['userid'] != doc_account_id:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    cursor = db_conn.execute('DELETE FROM LorePage WHERE DocumentID=?', (document_id,))
    db_conn.commit()
    cursor = db_conn.execute('DELETE FROM LoreDocument WHERE DocumentID=?', (document_id,))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('documents.my_documents'))

@bp.route('/admin/privatedoc/<document_id>/', methods=['GET'])
@check_loggedin
def private_document(document_id):
    if session['access'] == 2 or session['access'] == 3:
        db_conn = sqlite3.connect('./db/prototype.db')
        db_conn.execute('UPDATE LoreDocument SET Public=0 WHERE DocumentID=?', (document_id,))
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

    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT AccountID, public FROM LoreDocument WHERE DocumentID=(SELECT DocumentID FROM LorePage WHERE PageID=?)', (page_id,))
    res = cursor.fetchone()

    if not res:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    account_id, public = res
    document_owner = True if 'userid' in session and session['userid']==account_id else False

    if public==False and not document_owner:
        db_conn.close()
        return 'the document you attempted to view is private'

    cursor = db_conn.execute('SELECT content FROM LorePage WHERE PageID=?', (page_id,))
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

    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT AccountID FROM LoreDocument WHERE DocumentID=?', (document_id,))
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

        cursor = db_conn.execute('INSERT INTO LorePage (Name, Content, DocumentID) VALUES (?, ?, ?)', (title, content, document_id))
        db_conn.commit()
        db_conn.close()

        return redirect(url_for('documents.document_view', document_id=document_id))

@bp.route('/page/edit/<page_id>/', methods=['GET', 'POST'])
@check_loggedin
def edit_page(page_id):
    '''
    Allows the user to edit the content of a page within one of their own documents
    '''
    
    db_conn = sqlite3.connect('./db/prototype.db')
    # need to add document id here
    cursor = db_conn.execute('SELECT LoreDocument.AccountID, LorePage.DocumentID, LorePage.Name, LorePage.Content FROM LorePage INNER JOIN LoreDocument ON LorePage.DocumentID=LoreDocument.DocumentID WHERE PageID=? ', (page_id,))
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

        cursor = db_conn.execute('UPDATE LorePage SET Name=?, Content=? WHERE PageID=?', (title, content, page_id))
        db_conn.commit()
        db_conn.close()
        
        return redirect(url_for('documents.page_view', page_id=page_id))

@bp.route('/page/delete/<page_id>/', methods=['GET'])
@check_loggedin
def delete_page(page_id):
    '''
    Used to delete a document and its associated pages
    '''
    
    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT AccountID, DocumentID FROM LoreDocument WHERE DocumentID=(SELECT DocumentID FROM LorePage WHERE PageID=?)', (page_id,))
    page_account_id, document_id = cursor.fetchone()

    if session['userid'] != page_account_id:
        db_conn.close()
        return redirect(url_for('main.dashboard'))

    cursor = db_conn.execute('DELETE FROM LorePage WHERE PageID=?', (page_id,))
    db_conn.commit()
    db_conn.close()

    return redirect(url_for('documents.document_view', document_id=document_id))