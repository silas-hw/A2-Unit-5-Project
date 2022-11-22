CREATE TABLE User (
    AccountID INTEGER NOT NULL PRIMARY KEY,

    Username VARCHAR(64) NOT NULL UNIQUE CHECK(length(Username)>3),
    Password VARCHAR(255) NOT NULL CHECK(length(Password) >= 8),
    Email VARCHAR(255) NOT NULL UNIQUE,
    RecieveNewsletter INT NOT NULL DEFAULT 0,

    BankAccountNum VARCHAR(17) CHECK(length(BankAccountNum) >= 8),
    BankSortCode STRING(6) CHECK(length(BankSortCode)==6),

    AccessLevel INT NOT NULL DEFAULT 0,
    FOREIGN KEY(AccessLevel) REFERENCES AccessLevel(AccessLevel)
);

CREATE TABLE AccessLevel (
    AccessLevel INTEGER PRIMARY KEY,
    Name VARCHAR(5) NOT NULL,
    Description VARCHAR(64)
);

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
    Descriptoin VARCHAR(255),
    Content VARCHAR(5000),

    DocumentID INT NOT NULL,
    FOREIGN KEY(DocumentID) REFERENCES LoreDocument(DocumentID)
);

CREATE TABLE LoreDocumentComment (
    CommentID INTEGER PRIMARY KEY,

    Content VARCHAR(255) NOT NULL,
    Date STRING(10) NOT NULL,

    DocumentID INT NOT NULL,
    FOREIGN KEY(DocumentID) REFERENCES LoreDocument(DocumentID)

    AccountID INT NOT NULL,
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);

CREATE TABLE LoreDocumentLike (
    LikeID INTEGER PRIMARY KEY,
    
    DocumentID INT NOT NULL,
    FOREIGN KEY(DocumentID) REFERENCES LoreDocument(DocumentID)

    AccountID INT NOT NULL,
    FOREIGN KEY(AccountID) REFERENCES User(AccountID)
);