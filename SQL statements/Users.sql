--- retrieves all data associated with a given account ID
SELECT * FROM User WHERE AccountID=?, (account_id)

--- retrieves the name of the access level of a given accountID
SELECT Name FROM AccessLevel WHERE AccessID=?, (res[7],)