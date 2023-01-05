--- LOGIN ---

--- both checks if an acccount with a combined email and password exists and also retrieves
--- that accounts ID and Username
SELECT AccountID, Username FROM User WHERE Email=? AND Password=?, (email, password_hash);

--- REGISTER ---

--- used to ensure an account doesn't already exist
SELECT AccountID FROM User WHERE Email=? OR Username=?, (email, username);

--- inserts entered user data into the database
INSERT INTO User (username, email, password, RecieveNewsletter) VALUES (?, ?, ?, ?), (username, email, password_hash, newsletter);

--- retrieves the account ID of the newly created account so a session can be created
SELECT AccountID FROM User WHERE Email=?, (email,);