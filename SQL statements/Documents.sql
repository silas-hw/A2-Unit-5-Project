--- MY DOCUMENTS ---

--- get a list of all the documents that the currently logged in
--- user has created
SELECT DocumentName, Description, Public, DocumentID FROM LoreDocument WHERE AccountID=?, (session['userid'],)

--- count how many documents the currently logged in user
--- has created
SELECT COUNT(DocumentID) FROM LoreDocument WHERE AccountID=?, (session['userid'],)


--- DOCUMENT VIEW ---

--- used to check if the currently logged in user has access to the 
--- document they are attempting to view
SELECT AccountID, public FROM LoreDocument WHERE DocumentID=?, (document_id,)

--- used to output the pages associated with a particular document
SELECT PageID, Name FROM LorePage WHERE DocumentID=?, (document_id,)


--- ADD DOCUMENT ---

--- count how many documents the currently logged in user
--- has created
SELECT COUNT(DocumentID) FROM LoreDocument WHERE AccountID=?, (session['userid'],)

--- check how many documents the current user can create depending
--- on their membership level
SELECT DocumentLimit FROM MembershipLevel WHERE MembershipLevel=(SELECT MembershipLevel FROM Membership WHERE AccountID=?), (session['userid'],)

--- add the new document to the database 
INSERT INTO LoreDocument (DocumentName, Description, Public, AccountID) VALUES (?, ?, ?, ?), (document_name, document_description, document_public, session['userid'])


--- DELETE DOCUMENT ---

--- used to check if the user owns th
e document
SELECT AccountID FROM LoreDocument WHERE DocumentID=?, (document_id,)

--- delete all the pages associated with the document
DELETE FROM LorePage WHERE DocumentID=?, (document_id,)

--- delete the document itself
DELETE FROM LoreDocument WHERE DocumentID=?, (document_id,)


--- PAGE VIEW ---

--- used to check if a user has access to the documen a page is linked to
SELECT AccountID, public FROM LoreDocument WHERE DocumentID=(SELECT DocumentID FROM LorePage WHERE PageID=?), (page_id,)

--- retrieves the data stored about a page to be outputted
SELECT content FROM LorePage WHERE PageID=?, (page_id,)


--- PAGE ADD ---

--- used to check if a user owns the document
SELECT AccountID FROM LoreDocument WHERE DocumentID=?, (document_id,)

--- used to insert the new page into the database
INSERT INTO LorePage (Name, Content, DocumentID) VALUES (?, ?, ?), (title, content, document_id)


--- PAGE EDIT ---

--- used to check if a user owns the document
SELECT LoreDocument.AccountID, LorePage.DocumentID, LorePage.Name, LorePage.Content FROM LorePage INNER JOIN LoreDocument ON LorePage.DocumentID=LoreDocument.DocumentID WHERE PageID=?, (page_id,)

--- updates the data stored about a page in the database
UPDATE LorePage SET Name=?, Content=? WHERE PageID=?, (title, content, page_id)



