const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

// 1. Setup Folder & Connection
const storageDir = path.join(__dirname, '..', 'Storage');
if (!fs.existsSync(storageDir)) fs.mkdirSync(storageDir);

const dbPath = path.join(storageDir, 'databasefinance.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) console.error("Database opening error:", err);
    else console.log("✅ Connected to SQLite database.");
});

// 2. Setup Tables
db.serialize(() => {
    db.run("PRAGMA foreign_keys = ON");

    // Transactions Table
    db.run(`CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT, 
        amount REAL, 
        type TEXT, 
        date TEXT
    )`);

    // Tags Table (The master list of tags)
    db.run(`CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT UNIQUE NOT NULL
    )`);

    // The Bridge Table (Links them together)
    db.run(`CREATE TABLE IF NOT EXISTS transaction_tags (
        transaction_id INTEGER, 
        tag_id INTEGER,
        FOREIGN KEY(transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
        FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (transaction_id, tag_id)
    )`);

    console.log("✅ Database tables initialized.");
});

// We ONLY export the 'db' connection now.
module.exports = { db };