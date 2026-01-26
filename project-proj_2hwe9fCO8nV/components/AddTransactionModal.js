function AddTransactionModal({ isOpen, onClose, onAdd }) {
    if (!isOpen) return null;

    const [type, setType] = React.useState('expense');
    const [title, setTitle] = React.useState('');
    const [amount, setAmount] = React.useState('');
    const [category, setCategory] = React.useState('');
    const [date, setDate] = React.useState(new Date().toISOString().split('T')[0]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!title || !amount) return;

        onAdd({
            title,
            amount: parseFloat(amount),
            type,
            category: category || 'General',
            date: date.split('-').reverse().join('/') // Format YYYY-MM-DD to DD/MM/YYYY
        });
        
        // Reset form
        setTitle('');
        setAmount('');
        setCategory('');
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm fade-in" data-name="add-transaction-modal" data-file="components/AddTransactionModal.js">
            <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl transform transition-all scale-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                    <h2 className="text-xl font-bold text-gray-900">Add Transaction</h2>
                    <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
                        <div className="icon-x text-gray-500"></div>
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {/* Toggle Type */}
                    <div className="flex p-1 bg-gray-100 rounded-xl mb-6">
                        <button
                            type="button"
                            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${type === 'expense' ? 'bg-white shadow text-red-600' : 'text-gray-500 hover:text-gray-700'}`}
                            onClick={() => setType('expense')}
                        >
                            Expense
                        </button>
                        <button
                            type="button"
                            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${type === 'income' ? 'bg-white shadow text-green-600' : 'text-gray-500 hover:text-gray-700'}`}
                            onClick={() => setType('income')}
                        >
                            Income
                        </button>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <input 
                            type="text" 
                            required
                            placeholder="e.g. Groceries, Freelance Work"
                            className="w-full px-4 py-2 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Amount (RM)</label>
                            <input 
                                type="number" 
                                required
                                step="0.01"
                                placeholder="0.00"
                                className="w-full px-4 py-2 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                                value={amount}
                                onChange={(e) => setAmount(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                            <select 
                                className="w-full px-4 py-2 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all appearance-none bg-white"
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                            >
                                <option value="">Select...</option>
                                <option value="Food">Food & Dining</option>
                                <option value="Transport">Transportation</option>
                                <option value="Shopping">Shopping</option>
                                <option value="Housing">Housing</option>
                                <option value="Salary">Salary</option>
                                <option value="Investment">Investment</option>
                            </select>
                        </div>
                    </div>
                     <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                        <input 
                            type="date" 
                            required
                            className="w-full px-4 py-2 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                        />
                    </div>

                    <div className="pt-4">
                        <button type="submit" className="w-full btn-primary justify-center py-3 text-lg shadow-lg shadow-blue-900/20">
                            Save Transaction
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}