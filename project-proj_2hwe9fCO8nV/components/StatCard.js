function StatCard({ title, amount, icon, type, trend }) {
    // type: 'income', 'expense', 'balance'
    
    let colorClass = 'text-gray-900';
    let bgClass = 'bg-gray-100';
    let iconColor = 'text-gray-600';
    let trendColor = 'text-gray-500';

    if (type === 'income') {
        colorClass = 'text-[var(--accent-green)]';
        bgClass = 'bg-green-50';
        iconColor = 'text-green-600';
        trendColor = 'text-green-600';
    } else if (type === 'expense') {
        colorClass = 'text-[var(--accent-red)]';
        bgClass = 'bg-red-50';
        iconColor = 'text-red-600';
        trendColor = 'text-red-600';
    } else if (type === 'balance') {
        colorClass = 'text-[var(--primary-color)]';
        bgClass = 'bg-blue-50';
        iconColor = 'text-blue-600';
        trendColor = 'text-blue-600';
    }

    return (
        <div className="card flex items-center justify-between fade-in" data-name="stat-card" data-file="components/StatCard.js">
            <div>
                <p className="text-sm font-medium text-[var(--text-muted)] mb-1">{title}</p>
                <h3 className={`text-2xl font-bold ${colorClass}`}>{amount}</h3>
                {trend && (
                    <div className={`flex items-center gap-1 text-xs font-medium mt-2 ${trendColor}`}>
                        <span className={trend > 0 ? "icon-trending-up" : "icon-trending-down"}></span>
                        <span>{Math.abs(trend)}% from last month</span>
                    </div>
                )}
            </div>
            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${bgClass}`}>
                <div className={`${icon} text-xl ${iconColor}`}></div>
            </div>
        </div>
    );
}