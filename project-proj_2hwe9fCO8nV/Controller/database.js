const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

// 1. Setup Folder & Database Connection
// This file is in 'Controller', so we go UP to find 'Storage'
const storageDir = path.join(__dirname, '..', 'Storage');
if (!fs.existsSync(storageDir)) fs.mkdirSync(storageDir);

const dbPath = path.join(storageDir, 'databasefinance.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) console.error("Database opening error:", err);
    else console.log("✅ Connected to SQLite database.");
});

// 2. Initialize Tables
db.serialize(() => {
    db.run("PRAGMA foreign_keys = ON");

    db.run(`CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT, 
        amount REAL, 
        type TEXT, 
        date TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT UNIQUE NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS transaction_tags (
        transaction_id INTEGER, 
        tag_id INTEGER,
        FOREIGN KEY(transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
        FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (transaction_id, tag_id)
    )`);

    console.log("1. Tables are ready.");
    // Only run the test if you really want to see it in the terminal
    // runSimpleTest(); 
});

// 3. The Multi-Tag Logic (Defined here, EXPORTED to CRUD.js)
async function addTransactionWithMultiTags(title, amount, type, date, tagArray) {
    return new Promise((resolve, reject) => {
        db.run(`INSERT INTO transactions (title, amount, type, date) VALUES (?, ?, ?, ?)`, 
        [title, amount, type, date], async function(err) {
            if (err) return reject(err);
            const transId = this.lastID;
            
            try {
                for (const tagName of tagArray) {
                    await linkTransactionToTag(transId, tagName);
                }
                resolve(transId);
            } catch (e) { reject(e); }
        });
    });
}

// 4. Helper Function
async function linkTransactionToTag(transactionId, tagName) {
    return new Promise((resolve, reject) => {
        db.run(`INSERT OR IGNORE INTO tags (name) VALUES (?)`, [tagName], function(err) {
            if (err) return reject(err);
            db.get(`SELECT id FROM tags WHERE name = ?`, [tagName], (err, row) => {
                if (err) return reject(err);
                db.run(`INSERT OR IGNORE INTO transaction_tags (transaction_id, tag_id) VALUES (?, ?)`, 
                [transactionId, row.id], (err) => {
                    if (err) reject(err); else resolve();
                });
            });
        });
    });
}

// 5. Test Functions (Optional)
function getExpenses() {
    const sql = `
        SELECT t.id, t.title, t.amount, GROUP_CONCAT(tg.name, ', ') as category
        FROM transactions t
        LEFT JOIN transaction_tags tt ON t.id = tt.transaction_id
        LEFT JOIN tags tg ON tt.tag_id = tg.id
        GROUP BY t.id
    `;
    db.all(sql, [], (err, rows) => {
        console.log("\n--- My Expense List ---");
        console.table(rows);
    });
}

async function runSimpleTest() {
    console.log("2. Running Test...");
    try {
        await addTransactionWithMultiTags("Fancy Dinner", 150.00, 'expense', "2026-01-23", ["Food", "DateNight", "Luxury"]);
        getExpenses();
    } catch (err) {
        console.error("Test Error:", err);
    }
}

// 6. EXPORTS (CRUD.js will import these)
module.exports = { 
    db, 
    addTransactionWithMultiTags, 
    linkTransactionToTag 
};