// Controller/CRUD.js
const { db } = require('./database');

const TransactionController = {
    // 1. CREATE (The Multi-Step process)
    create: async (data) => {
        // Step A: Insert the transaction first
        const transId = await new Promise((resolve, reject) => {
            db.run(
                `INSERT INTO transactions (title, amount, type, date) VALUES (?, ?, ?, ?)`,
                [data.title, data.amount, data.type, data.date],
                function (err) {
                    if (err) reject(err);
                    else resolve(this.lastID); // Get the ID of the new transaction
                }
            );
        });

        // Step B: Link the tags (if any)
        if (data.tags && data.tags.length > 0) {
            for (const tagName of data.tags) {
                await linkTag(transId, tagName);
            }
        }

        return { id: transId, ...data };
    },

    // 2. READ (All with their tags)
    getAll: () => {
        return new Promise((resolve, reject) => {
            const sql = `
                SELECT t.*, COALESCE(GROUP_CONCAT(tg.name, ', '), '') as category
                FROM transactions t
                LEFT JOIN transaction_tags tt ON t.id = tt.transaction_id
                LEFT JOIN tags tg ON tt.tag_id = tg.id
                GROUP BY t.id
                ORDER BY t.date DESC
            `;
            db.all(sql, [], (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    },

    // 3. DELETE
    delete: (id) => {
        return new Promise((resolve, reject) => {
            // ON DELETE CASCADE in database.js handles the tag links automatically!
            db.run(`DELETE FROM transactions WHERE id = ?`, [id], (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    },

    // Updating transaction 
    update: async (id, data) => {
        return new Promise((resolve, reject) => {
            // We use serialize to ensure these run in order
            db.serialize(async () => {
                try {
                    // Step A: Update the main transaction
                    db.run(
                        `UPDATE transactions SET title = ?, amount = ?, type = ?, date = ? WHERE id = ?`,
                        [data.title, data.amount, data.type, data.date, id],
                        function(err) { if (err) reject(err); }
                    );

                    // Step B: Wipe old tag links for this transaction
                    db.run(`DELETE FROM transaction_tags WHERE transaction_id = ?`, [id], (err) => {
                        if (err) reject(err);
                    });

                    // Step C: Link the new set of tags
                    if (data.tags && data.tags.length > 0) {
                        for (const tagName of data.tags) {
                            await linkTag(id, tagName); // This is the helper function we wrote earlier
                        }
                    }

                    resolve({ id, ...data });
                } catch (err) {
                    reject(err);
                }
            });
        });
    },

    // 4. READ (Filter by Tag)
getTagStats: () => {
        return new Promise((resolve, reject) => {
            const sql = `
                SELECT tg.name, COUNT(tt.transaction_id) as count
                FROM tags tg
                LEFT JOIN transaction_tags tt ON tg.id = tt.tag_id
                GROUP BY tg.id
                ORDER BY count DESC
            `;
            db.all(sql, [], (err, rows) => {
                if (err) reject(err); else resolve(rows);
            });
        });
    }
};

// --- PRIVATE HELPER FUNCTION ---
// This handles the "Many-to-Many" logic
async function linkTag(transactionId, tagName) {
    return new Promise((resolve, reject) => {
        // 1. Create tag if it doesn't exist (INSERT OR IGNORE)
        db.run(`INSERT OR IGNORE INTO tags (name) VALUES (?)`, [tagName], function (err) {
            if (err) return reject(err);

            // 2. Get the tag's ID
            db.get(`SELECT id FROM tags WHERE name = ?`, [tagName], (err, row) => {
                if (err) return reject(err);

                // 3. Link the transaction to the tag in the bridge table
                db.run(
                    `INSERT OR IGNORE INTO transaction_tags (transaction_id, tag_id) VALUES (?, ?)`,
                    [transactionId, row.id],
                    (err) => {
                        if (err) reject(err);
                        else resolve();
                    }
                );
            });
        });
    });
}

module.exports = TransactionController;