DROP TABLE IF EXISTS account;

CREATE TABLE account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user TEXT NOT NULL,
    txndate TIMESTAMP NOT NULL,
    txntype TEXT NOT NULL,
    txncategory TEXT NOT NULL,
    txndescription TEXT NOT NULL,
    amount INTEGER NOT NULL,
    bank TEXT NOT NULL,
    planningmonth TEXT NOT NULL
);

