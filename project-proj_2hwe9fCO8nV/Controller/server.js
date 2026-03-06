const express = require('express');
const cors = require('cors');
const Transaction = require('./CRUD'); // Ensure the file is named CRUD.js

const app = express();

// --- MIDDLEWARE ---
app.use(cors()); 
app.use(express.json()); // Parses incoming JSON data

// --- ROUTES ---

// 0. Server Health Check (Test this in Chrome!)
app.get('/', (req, res) => {
    res.send("🚀 Finance API is alive and running!");
});

// 1. READ ALL
app.get('/api/transactions', async (req, res) => {
    try {
        const data = await Transaction.getAll();
        res.json(data);
    } catch (err) {
        console.error("GET Error:", err.message);
        res.status(500).json({ error: err.message });
    }
});

// 2. CREATE (Merged into one clean route)
app.post('/api/transactions', async (req, res) => {
    const { title, amount } = req.body;
    // Validation: Don't let empty data through!
    if (!title || !amount || amount <= 0) {
        return res.status(400).json({ error: "Title and a valid Amount are required!" });
    }

    try {
        const result = await Transaction.create(req.body);
        res.status(201).json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 3. DELETE
app.delete('/api/transactions/:id', async (req, res) => {
    try {
        await Transaction.delete(req.params.id);
        res.json({ message: "Deleted successfully!" });
    } catch (err) {
        console.error("DELETE Error:", err.message);
        res.status(500).json({ error: err.message });
    }
});

// 4. READ BY TAG
app.get('/api/transactions/tag/:tagName', async (req, res) => {
    try {
        const data = await Transaction.getByTag(req.params.tagName);
        res.json(data);
    } catch (err) {
        console.error("Filter Error:", err.message);
        res.status(500).json({ error: err.message });
    }
});


app.put('/api/transactions/:id', async (req, res) => {
    try {
        const result = await Transaction.update(req.params.id, req.body);
        res.json({ message: "Update successful!", data: result });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/stats/tags', async (req, res) => {
    try {
        const data = await Transaction.getTagStats();
        res.json(data);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
}); 

// --- START SERVER ---
const PORT = 3001;
app.listen(PORT, () => {
    console.log(`\n🚀 Server is blasting off!`);
    console.log(`📡 URL: http://localhost:${PORT}`);
    console.log(`🛠️  Press Ctrl+C to stop the engine\n`);
});