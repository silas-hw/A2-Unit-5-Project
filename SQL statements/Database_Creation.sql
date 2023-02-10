CREATE TABLE User (
    AccountID INTEGER NOT NULL PRIMARY KEY,

    Username VARCHAR(64) NOT NULL UNIQUE CHECK(length(Username)>3),
    Password VARCHAR(255) NOT NULL CHECK(length(Password) >= 8),
    Email VARCHAR(255) NOT NULL UNIQUE,
    RecieveNewsletter INT NOT NULL DEFAULT 0,

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

CREATE TABLE AccessLevel (
    AccessID INTEGER PRIMARY KEY,
    Name VARCHAR(10) NOT NULL,
    Description VARCHAR(64)
);

INSERT INTO AccessLevel (Name, Description) VALUES ('standard', 'Standard users of the website with no further access rights');
INSERT INTO AccessLevel (Name, Description) VALUES ('mod', 'Have extended access rights but cannot create Newsletters or directly manipulate the database');
INSERT INTO AccessLevel (Name, Description) VALUES ('admin', 'Has full access rights')

CREATE TABLE LoreDocument (
    DocumentID INTEGER PRIMARY KEY,

    DocumentName VARCHAR(64) NOT NULL,
    Description VARCHAR(255),
    Public INT NOT NULL DEFAULT 0,

    AccountID INT NOT NULL,
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);

CREATE TABLE LorePage (
    PageID INTEGER PRIMARY KEY,

    Name VARHCAR(64) NOT NULL,
    Description VARCHAR(255),
    Content VARCHAR(5000),

    DocumentID INT NOT NULL,
    FOREIGN KEY(DocumentID) REFERENCES LoreDocument(DocumentID)
);

CREATE TABLE LoreDocumentComment (
    CommentID INTEGER PRIMARY KEY,

    Content VARCHAR(255) NOT NULL,
    Date STRING(10) NOT NULL,

    DocumentID INT NOT NULL,
    AccountID INT NOT NULL,

    FOREIGN KEY(DocumentID) REFERENCES LoreDocument(DocumentID),
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);

CREATE TABLE LoreDocumentLike (
    LikeID INTEGER PRIMARY KEY,
    
    DocumentID INT NOT NULL,
    AccountID INT NOT NULL,

    FOREIGN KEY(DocumentID) REFERENCES LoreDocument(DocumentID),
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);

CREATE TABLE WebsiteRating (
    RatingID INTEGER PRIMARY KEY,
    Rating INT NOT NULL CHECK(rating<=5),

    AccountID INT NOT NULL UNIQUE,
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);