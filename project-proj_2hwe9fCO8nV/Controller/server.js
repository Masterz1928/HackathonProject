const express = require('express');
const fs = require('fs');
const cors = require('cors'); // <--- THIS was likely missing!
const Transaction = require('./CRUD'); // Your CRUD.js file in the same folder

const app = express();

// Middleware
app.use(cors()); // Now 'cors' is defined!
app.use(express.json());

// 1. READ ALL
app.get('/api/transactions', async (req, res) => {
    try {
        const data = await Transaction.getAll();
        res.json(data);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 2. CREATE
app.post('/api/transactions', async (req, res) => {
    try {
        await Transaction.create(req.body);
        res.status(201).json({ message: "Added!" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// 3. DELETE
app.delete('/api/transactions/:id', async (req, res) => {
    try {
        await Transaction.delete(req.params.id);
        res.json({ message: "Deleted!" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
    
// This catches the 'POST' request from the React app
app.post('/api/transactions', async (req, res) => {
    try {
        // req.body is the data packet we sent from React
        await Transaction.create(req.body); 
        res.status(201).json({ message: "Transaction added to SQLite!" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(3001, () => console.log("Server running on 3001"));