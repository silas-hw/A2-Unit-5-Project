---User Account Tables
CREATE TABLE User (
    AccountID INTEGER NOT NULL PRIMARY KEY,

    Username VARCHAR(64) NOT NULL UNIQUE CHECK(length(Username)>3),
    Password VARCHAR(255) NOT NULL CHECK(length(Password) >= 8),
    Email VARCHAR(255) NOT NULL UNIQUE,
    RecieveNewsletter INT NOT NULL DEFAULT 0,

    Restricted INT DEFAULT 0 CHECK(Restricted == 0 OR Restricted == 1),

    BankAccountNum VARCHAR(17) CHECK(length(BankAccountNum) >= 8),
    BankSortCode STRING(6) CHECK(length(BankSortCode)==6),

    MembershipLevel INT NOT NULL DEFAULT 1,

    AccessLevel INT NOT NULL DEFAULT 1,
    FOREIGN KEY(AccessLevel) REFERENCES AccessLevel(AccessID),
    FOREIGN KEY(MembershipLevel) REFERENCES MembershipLevel(MembershipLevel)
);

CREATE TABLE MembershipLevel (
    MembershipLevel INTEGER NOT NULL PRIMARY KEY,

    Name VARCHAR(64) NOT NULL UNIQUE,
    Description VARCHAR(255) NOT NULL UNIQUE,

    DocumentLimit INT NOT NULL,
    PageLimit INT NOT NULL,
    Price INT NOT NULL CHECK(Price>=0)
);

INSERT INTO MembershipLevel (Name, Description, DocumentLimit, PageLimit, Price) VALUES ('standard', 'The standard free account you can get just by signing up', 15, 50, 0);
INSERT INTO MembershipLevel (Name, Description, DocumentLimit, PageLimit, Price) VALUES ('premium', 'The paid membership that gives you unlimited documents and pages', -1, -1, 10);

CREATE TABLE MembershipPayment (
    AccountID INT NOT NULL UNIQUE,
    DateStartedEpoch INT NOT NULL,
    LastPaymentEpoch INT NOT NULL CHECK(LastPaymentEpoch>=DateStartedEpoch),

    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
)

CREATE TABLE AccessLevel (
    AccessID INTEGER PRIMARY KEY,
    Name VARCHAR(10) NOT NULL,
    Description VARCHAR(64)
);

INSERT INTO AccessLevel (Name, Description) VALUES ('standard', 'Standard users of the website with no further access rights');
INSERT INTO AccessLevel (Name, Description) VALUES ('mod', 'Have extended access rights but cannot create Newsletters or directly manipulate the database');
INSERT INTO AccessLevel (Name, Description) VALUES ('admin', 'Has full access rights')

---Document Tables
CREATE TABLE Document (
    DocumentID INTEGER PRIMARY KEY,

    DocumentName VARCHAR(64) NOT NULL,
    Description VARCHAR(255),
    Public INT NOT NULL DEFAULT 0,

    Restricted INT DEFAULT 0 CHECK(Restricted == 0 OR Restricted == 1),

    AccountID INT NOT NULL,
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);

CREATE TABLE DocumentShare (
    AccountID INT NOT NULL,
    DocumentID INT NOT NULL,

    FOREIGN KEY(AccountID) REFERENCES User(AccountID),
    FOREIGN KEY(DocumentID) REFERENCES Document(DocumentID)
)

CREATE TABLE Page (
    PageID INTEGER PRIMARY KEY,

    Name VARHCAR(64) NOT NULL,
    Description VARCHAR(255),
    Content VARCHAR(5000),

    DocumentID INT NOT NULL,
    FOREIGN KEY(DocumentID) REFERENCES Document(DocumentID)
);

CREATE TABLE DocumentComment (
    CommentID INT NOT NULL,
    DocumentID INT NOT NULL,

    FOREIGN KEY(CommentID) REFERENCES Comment(CommentID),
    FOREIGN KEY(DocumentID) REFERENCES Document(DocumentID)
);

CREATE TABLE DocumentLike (
    LikeID INTEGER PRIMARY KEY,
    
    DocumentID INT NOT NULL,
    AccountID INT NOT NULL,

    FOREIGN KEY(DocumentID) REFERENCES Document(DocumentID),
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);

---Comment (Community Post & Document)
CREATE TABLE Comment (
    CommentID INTEGER PRIMARY KEY,
    AccountID INT NOT NULL,

    Content VARCHAR NOT NULL,
    DateEpoch INT NOT NULL,

    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
)

---Community Posts
CREATE TABLE CommunityPost (
    PostID INTEGER PRIMARY KEY,

    AccountID INT NOT NULL,
    Title VARCHAR NOT NULL,
    Content VARCHAR NOT NULL,

    DateEpoch INT NOT NULL,

    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
)

CREATE TABLE CommunityPostComment (
    CommentID INT NOT NULL,
    PostID INT NOT NULL,

    FOREIGN KEY(PostID) REFERENCES CommunityPost(PostID),
    FOREIGN KEY(CommentID) REFERENCES Comment(CommentID)
)

CREATE TABLE CommunityPostLike (
    LikeID INTEGER PRIMARY KEY,
    PostID INT NOT NULL,
    AccountID INT NOT NULL,

    FOREIGN KEY(PostID) REFERENCES CommunityPost(PostID),
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
)

---Website Rating Table
CREATE TABLE WebsiteRating (
    RatingID INTEGER PRIMARY KEY,
    Rating INT NOT NULL CHECK(rating<=5),

    AccountID INT NOT NULL UNIQUE,
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);

---Admin Tables
CREATE TABLE Newsletter (
    NewsletterID INTEGER PRIMARY KEY,

    AccountID INT NOT NULL,
    Subject VARCHAR NOT NULL,
    Content VARCHAR NOT NULL,

    DateSendEpoch INT NOT NULL,

    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
)