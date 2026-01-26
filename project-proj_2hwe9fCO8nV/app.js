function App() {
    const [activeTab, setActiveTab] = React.useState('dashboard');
    const [transactions, setTransactions] = React.useState([]);
    const [isModalOpen, setIsModalOpen] = React.useState(false);
    const [loading, setLoading] = React.useState(true);

    // --- CONNECTION: LOAD DATA FROM BACKEND ---
    React.useEffect(() => {
        fetchTransactions();
    }, []);

    const fetchTransactions = async () => {
        try {
            const response = await fetch('http://localhost:3001/api/transactions');
            const data = await response.json();
            setTransactions(data);
            setLoading(false);
        } catch (error) {
            console.error("Connection failed. Is the server running?", error);
        }
    };

    // --- CONNECTION: SEND DATA TO BACKEND ---
    const handleAddTransaction = async (newTx) => {
        try {
            const response = await fetch('http://localhost:3001/api/transactions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: newTx.title,
                    amount: parseFloat(newTx.amount),
                    type: newTx.type,
                    date: new Date().toISOString().split('T')[0], // Today's date
                    tags: newTx.category.split(',').map(tag => tag.trim()) 
                })
            });

            if (response.ok) {
                fetchTransactions(); // Refresh the list
                setIsModalOpen(false); // Close the popup
            }
        } catch (error) {
            console.error("Add failed:", error);
        }
    };

    // --- CONNECTION: DELETE DATA FROM BACKEND ---
    const handleDelete = async (id) => {
        if (!window.confirm("Delete this transaction?")) return;
        try {
            const response = await fetch(`http://localhost:3001/api/transactions/${id}`, {
                method: 'DELETE'
            });
            if (response.ok) fetchTransactions();
        } catch (error) {
            console.error("Delete failed:", error);
        }
    };

    // Logic for cards
    const totalIncome = transactions.filter(t => t.type === 'income').reduce((acc, curr) => acc + curr.amount, 0);
    const totalExpense = transactions.filter(t => t.type === 'expense').reduce((acc, curr) => acc + curr.amount, 0);

    return (
        <div className="flex min-h-screen bg-[var(--bg-color)]">
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
            
            <main className="flex-1 md:ml-64 p-8 transition-all duration-300">
                <header className="flex justify-between items-center mb-10 fade-in">
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <button onClick={() => setIsModalOpen(true)} className="btn-primary">
                        <i className="lucide-plus text-lg"></i>
                        <span>Add Expense</span>
                    </button>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 fade-in">
                    <StatCard title="Income" amount={`RM ${totalIncome.toFixed(2)}`} type="income" />
                    <StatCard title="Expenses" amount={`RM ${totalExpense.toFixed(2)}`} type="expense" />
                    <StatCard title="Balance" amount={`RM ${(totalIncome - totalExpense).toFixed(2)}`} type="balance" />
                </div>

                <div className="card fade-in">
                    <TransactionTable transactions={transactions} onDelete={handleDelete} />
                </div>
            </main>

            <AddTransactionModal 
                isOpen={isModalOpen} 
                onClose={() => setIsModalOpen(false)} 
                onAdd={handleAddTransaction} 
            />
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);