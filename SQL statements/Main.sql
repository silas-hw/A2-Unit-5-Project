--- LANDING PAGE ---

--- used to get the 5 best rated reviews for the website
SELECT Rating, AccountID FROM WebsiteRating ORDER BY Rating DESC LIMIT 5

--- gets the username for a particular rating
SELECT Username FROM User WHERE AccountID=?, (account_id,)


--- DASHBOARD ---

--- gets the 20 most recently published documents
SELECT DocumentName, Description, AccountID, DocumentID FROM LoreDocument WHERE Public=1 ORDER BY DocumentID DESC LIMIT 20

--- gets the username of the account that created a particular document
SELECT Username FROM User WHERE AccountID=?, (account_id,)

