// Controller/transactionController.js
const path = require('path'); // This is built into Node

// This tells Node: "Start exactly where THIS file is, go up one, then into Storage"
const dbFilePath = path.join(__dirname, '..', 'Controller', 'database.js');

const { db, addTransactionWithMultiTags } = require(dbFilePath);const TransactionController = {
    // CREATE
    create: async (data) => {
        // data = { title, amount, type, date, tags }
        return await addTransactionWithMultiTags(
            data.title, 
            data.amount, 
            data.type, 
            data.date, 
            data.tags
        );
    },

    // READ (All)
    getAll: () => {
        return new Promise((resolve, reject) => {
            const sql = `
                SELECT t.*, GROUP_CONCAT(tg.name, ', ') as category
                FROM transactions t
                LEFT JOIN transaction_tags tt ON t.id = tt.transaction_id
                LEFT JOIN tags tg ON tt.tag_id = tg.id
                GROUP BY t.id
            `;
            db.all(sql, [], (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    },

    // DELETE
    delete: (id) => {
        return new Promise((resolve, reject) => {
            // Because of ON DELETE CASCADE, this cleans up tags too!
            db.run(`DELETE FROM transactions WHERE id = ?`, [id], (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    },

    // READ (Filter by Tag)
    getByTag: (tagName) => {
        return new Promise((resolve, reject) => {
            const sql = `
                SELECT t.*, GROUP_CONCAT(tg.name, ', ') as category
                FROM transactions t
                JOIN transaction_tags tt ON t.id = tt.transaction_id
                JOIN tags tg ON tt.tag_id = tg.id
                WHERE t.id IN (
                    SELECT transaction_id FROM transaction_tags 
                    JOIN tags ON transaction_tags.tag_id = tags.id 
                    WHERE tags.name = ?
                )
                GROUP BY t.id
            `;
            db.all(sql, [tagName], (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }
};

module.exports = TransactionController;

