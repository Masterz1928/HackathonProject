function TransactionTable({ transactions }) {
    return (
        <div className="card fade-in" style={{ animationDelay: '0.2s' }} data-name="transaction-table" data-file="components/TransactionTable.js">
            <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-lg text-gray-800">Recent Transactions</h3>
                <button className="text-sm font-medium text-[var(--primary-color)] hover:underline">View All</button>
            </div>
            
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr>
                            <th className="pb-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Transaction</th>
                            <th className="pb-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Category</th>
                            <th className="pb-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</th>
                            <th className="pb-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Amount</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {transactions.map((tx) => (
                            <tr key={tx.id} className="group hover:bg-gray-50 transition-colors">
                                <td className="py-4 pr-4">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${tx.type === 'income' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                            <div className={tx.type === 'income' ? 'icon-arrow-down-left' : 'icon-arrow-up-right'}></div>
                                        </div>
                                        <span className="font-medium text-gray-900 group-hover:text-[var(--primary-color)] transition-colors">{tx.title}</span>
                                    </div>
                                </td>
                                <td className="py-4 text-sm text-gray-500">
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                        {tx.category}
                                    </span>
                                </td>
                                <td className="py-4 text-sm text-gray-500">{tx.date}</td>
                                <td className={`py-4 text-sm font-bold text-right ${tx.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                                    {tx.type === 'income' ? '+' : '-'} RM {tx.amount.toFixed(2)}
                                </td>
                            </tr>
                        ))}
                        {transactions.length === 0 && (
                            <tr>
                                <td colSpan="4" className="py-8 text-center text-gray-500">
                                    No transactions found. Start by adding one!
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}