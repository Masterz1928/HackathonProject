// --- 1. MOCK DATA SETUP AND STATE ---
const data = {
    'week': {
        income: 1500.00,
        expense: 450.50,
        transactions: [
            { item: 'Food and drinks', amount: 85.00, date: '25/11/2067', type: 'expense' },
            { item: 'Entertainment', amount: 15.00, date: '24/11/2067', type: 'expense' },
            { item: 'Gambling', amount: 1000.00, date: '23/11/2067', type: 'income' },
        ]
    },
    'month': {
        income: 6200.00,
        expense: 2800.75,
        transactions: [
            { item: 'Gambling Debts', amount: 20000.00, date: '01/11/2025', type: 'expense' },
            { item: 'Salary Deposit', amount: 5000.00, date: '31/10/2025', type: 'income' },
            { item: 'Utilities', amount: 250.75, date: '10/11/2025', type: 'expense' },
            { item: 'Takeout Dinner', amount: 75.00, date: '26/11/2025', type: 'expense' },
        ]
    }
};

let currentView = 'week'; 

// --- 2. THE MAIN DASHBOARD UPDATE FUNCTION ---

/**
 * Updates the metrics, table, and button styles based on the current view data.
 * @param {string} viewKey - 'week' or 'month'
 */
function updateDashboard (viewKey) {
    const viewData = data[viewKey];
    const totalLeft = viewData.income - viewData.expense;
    
    // A. Update Metrics
    document.getElementById('metric-total-income').textContent = `RM ${viewData.income.toFixed(2)}`;
    document.getElementById('metric-total-expense').textContent = `RM ${viewData.expense.toFixed(2)}`;

    const totalLeftEl = document.getElementById('metric-total-left');
    totalLeftEl.textContent = `RM ${totalLeft.toFixed(2)}`;
    // Set color based on balance
    totalLeftEl.style.color = totalLeft >= 0 ? '#1B5E20' : '#B71C1C';

    // B. Render Table Rows
    renderTransactions(viewData.transactions);
    
    // C. Update Button Styles
    document.getElementById('toggle-week').classList.remove('active-view');
    document.getElementById('toggle-month').classList.remove('active-view');
    document.getElementById(`toggle-${viewKey}`).classList.add('active-view');

    currentView = viewKey;
}


// --- 3. RENDER TRANSACTIONS FUNCTION (SITS GLOBALLY) ---

/**
 * Clears the table and draws new rows based on the transaction data provided.
 * @param {Array<Object>} transactions - The array of transaction objects
 */
function renderTransactions(transactions) {
    const tbody = document.getElementById('transaction-body');
    tbody.innerHTML = ''; // IMPORTANT: Clear the old rows first!

    transactions.forEach(tx => {
        const row = document.createElement('tr');
        
        // Use the type property ('income' or 'expense') for color-coding the amount
        const amountColor = tx.type === 'income' ? '#1B5E20' : '#B71C1C'; 
        
        row.innerHTML = `
            <td>${tx.item}</td>
            <td style="color: ${amountColor};">${tx.amount.toFixed(2)}</td>
            <td>${tx.date}</td>
        `;
        tbody.appendChild(row);
    });
}


// --- 4. INITIALIZATION AND EVENT LISTENERS (SITS GLOBALLY) ---

// Wait for the entire HTML document to load before running any script
document.addEventListener('DOMContentLoaded', () => {
    
    // Initial load: Display the default 'week' view
    updateDashboard(currentView);

    // Event Listener for the MONTH button
    document.getElementById('toggle-month').addEventListener('click', () => {
        updateDashboard('month');
    });

    // Event Listener for the WEEK button
    document.getElementById('toggle-week').addEventListener('click', () => {
        updateDashboard('week');
    });
});