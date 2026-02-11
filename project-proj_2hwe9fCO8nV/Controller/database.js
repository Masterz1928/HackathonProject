const { db } = require('./database');

const TransactionController = {
    // 1. READ (The "Big Join")
    // This pulls transactions AND their tags in one go
    getAll: () => {
        return new Promise((resolve, reject) => {
            const sql = `
                SELECT t.*, GROUP_CONCAT(tg.name) as tags
                FROM transactions t
                LEFT JOIN transaction_tags tt ON t.id = tt.transaction_id
                LEFT JOIN tags tg ON tt.tag_id = tg.id
                GROUP BY t.id
                ORDER BY t.date DESC
            `;
            db.all(sql, [], (err, rows) => {
                if (err) reject(err);
                else {
                    // Turn "Food,Fun" string back into ["Food", "Fun"] array for the Frontend
                    const formatted = rows.map(row => ({
                        ...row,
                        tags: row.tags ? row.tags.split(',') : []
                    }));
                    resolve(formatted);
                }
            });
        });
    },

    // 2. CREATE (The Multi-Step process)
    create: async (data) => {
        // First: Insert the Transaction
        const transId = await new Promise((resolve, reject) => {
            db.run(`INSERT INTO transactions (title, amount, type, date) VALUES (?, ?, ?, ?)`,
                [data.title, data.amount, data.type, data.date],
                function(err) {
                    if (err) reject(err); else resolve(this.lastID);
                }
            );
        });

        // Second: Link the tags (if any)
        if (data.tags && data.tags.length > 0) {
            for (const tagName of data.tags) {
                await linkTag(transId, tagName);
            }
        }
        return { id: transId, ...data };
    },

    // 3. DELETE
    delete: (id) => {
        return new Promise((resolve, reject) => {
            db.run(`DELETE FROM transactions WHERE id = ?`, [id], (err) => {
                if (err) reject(err); else resolve();
            });
        });
    }
};

// Helper for the many-to-many link
async function linkTag(transactionId, tagName) {
    return new Promise((resolve, reject) => {
        // 1. Create tag if it doesn't exist
        db.run(`INSERT OR IGNORE INTO tags (name) VALUES (?)`, [tagName], function(err) {
            if (err) return reject(err);
            // 2. Get the tag ID
            db.get(`SELECT id FROM tags WHERE name = ?`, [tagName], (err, row) => {
                if (err) return reject(err);
                // 3. Link them in the bridge table
                db.run(`INSERT OR IGNORE INTO transaction_tags (transaction_id, tag_id) VALUES (?, ?)`,
                    [transactionId, row.id], (err) => {
                        if (err) reject(err); else resolve();
                    }
                );
            });
        });
    });
}

module.exports = TransactionController;