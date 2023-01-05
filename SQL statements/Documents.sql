--- DOCUMENT VIEW ---

--- used to check if the currently logged in user has access to the 
--- document they are attempting to view
SELECT AccountID, public FROM LoreDocument WHERE DocumentID=?, (document_id,)

--- used to output the pages associated with a particular document
SELECT PageID, Name FROM LorePage WHERE DocumentID=?, (document_id,)


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



