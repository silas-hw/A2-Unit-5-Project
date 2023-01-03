# Note: for an understanding of how the terms 'document' and 'page' relate to each other in this context refer to the design document

from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import sqlite3
import markdown

bp = Blueprint('documents', __name__)

@bp.route('/document/view/<document_id>/', methods=['GET', 'POST'])
def document_view(document_id, page_id=None):
    '''
    Provides the user with a view of all of the pages stored within a document
    '''

    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT AccountID, public FROM LoreDocument WHERE DocumentID=?', (document_id,))
    account_id, public = cursor.fetchone()

    document_owner = True if 'userid' in session and session['userid']==account_id else False

    if public==False and not document_owner:
        return 'the document you attempted to view is private'

    cursor = db_conn.execute('SELECT PageID, Name FROM LorePage WHERE DocumentID=?', (document_id,))
    pages = cursor.fetchall()

    return render_template('/documents/documentview.html', pages=pages, document_owner=document_owner, document_id=document_id)

@bp.route('/page/view/<page_id>/', methods=['GET', 'POST'])
def page_view(page_id):
    '''
    Displays the content of a page to a user, whether it be within one of their own documents or within
    a publically shared document
    '''

    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT AccountID, public FROM LoreDocument WHERE DocumentID=(SELECT DocumentID FROM LorePage WHERE PageID=?)', (page_id,))
    account_id, public = cursor.fetchone()

    document_owner = True if 'userid' in session and session['userid']==account_id else False

    if public==False and not document_owner:
        return 'the document you attempted to view is private'

    cursor = db_conn.execute('SELECT content FROM LorePage WHERE PageID=?', (page_id,))
    
    md_content = cursor.fetchone()[0]
    html_content = markdown.markdown(md_content)
    return render_template('/documents/pageview.html', html_content=html_content, document_owner=document_owner, page_id=page_id)

@bp.route('/page/add/<document_id>/', methods=['GET', 'POST'])
def add_page(document_id):
    '''
    Used when a user decides to add a page to one of their documents
    '''

    db_conn = sqlite3.connect('./db/prototype.db')
    cursor = db_conn.execute('SELECT AccountID FROM LoreDocument WHERE DocumentID=?', (document_id,))
    account_id = cursor.fetchone()[0]

    if 'userid' not in session or session['userid']!=account_id:
        return 'You do not own this document'

    if request.method=='GET':
        return render_template('/documents/editpage.html', document_id=document_id, page_content='', page_title='', action='add')

    elif request.method=='POST':
        title = request.form['title']
        content = request.form['content']

        cursor = db_conn.execute('INSERT INTO LorePage (Name, Content, DocumentID) VALUES (?, ?, ?)', (title, content, document_id))
        db_conn.commit()

        return redirect(url_for('documents.page_view', document_id=document_id))

@bp.route('/page/edit/<page_id>/', methods=['GET', 'POST'])
def edit_page(page_id):
    '''
    Allows the user to edit the content of a page within one of their own documents
    '''
    
    db_conn = sqlite3.connect('./db/prototype.db')
    # need to add document id here
    cursor = db_conn.execute('SELECT LoreDocument.AccountID, LorePage.DocumentID, LorePage.Name, LorePage.Content FROM LorePage INNER JOIN LoreDocument ON LorePage.DocumentID=LoreDocument.DocumentID WHERE PageID=? ', (page_id,))
    account_id, document_id, page_title, page_content = cursor.fetchone()

    if 'userid' not in session or session['userid']!=account_id:
        return 'You do not own the document this page is attached to'

    if request.method=='GET':
        return render_template('/documents/editpage.html', page_id=page_id, page_content=page_content, page_title=page_title, action='edit')
    elif request.method=='POST':
        title = request.form['title']
        content = request.form['content']

        cursor = db_conn.execute('UPDATE LorePage SET Name=?, Content=? WHERE PageID=?', (title, content, page_id))
        db_conn.commit()

        return redirect(url_for('documents.page_view', page_id=page_id))