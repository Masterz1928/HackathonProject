function Sidebar({ activeTab, setActiveTab, mobileMenuOpen, setMobileMenuOpen }) {
    const menuItems = [
        { id: 'dashboard', label: 'Dashboard', icon: 'icon-layout-dashboard' },
        { id: 'transactions', label: 'Transactions', icon: 'icon-list-ordered' },
        { id: 'analytics', label: 'Analytics', icon: 'icon-chart-pie' },
        { id: 'goals', label: 'Savings Goals', icon: 'icon-target' },
        { id: 'settings', label: 'Settings', icon: 'icon-settings' },
    ];

    return (
        <>
            {/* Mobile Overlay */}
            {mobileMenuOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    onClick={() => setMobileMenuOpen(false)}
                ></div>
            )}

            {/* Sidebar Container */}
            <aside 
                className={`fixed top-0 left-0 h-full w-64 bg-white border-r border-gray-200 z-50 transform transition-transform duration-300 ease-in-out md:translate-x-0 ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}
                data-name="sidebar"
                data-file="components/Sidebar.js"
            >
                <div className="p-6 flex items-center gap-3 border-b border-gray-100">
                    <div className="w-8 h-8 bg-[var(--primary-color)] rounded-lg flex items-center justify-center text-white">
                        <div className="icon-wallet text-lg"></div>
                    </div>
                    <span className="text-xl font-bold text-gray-900 tracking-tight">FinanceFlow</span>
                </div>

                <nav className="p-4 space-y-2 mt-4">
                    {menuItems.map((item) => (
                        <div 
                            key={item.id}
                            onClick={() => {
                                setActiveTab(item.id);
                                setMobileMenuOpen(false);
                            }}
                            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                        >
                            <div className={`${item.icon} text-lg`}></div>
                            <span className="font-medium">{item.label}</span>
                        </div>
                    ))}
                </nav>

                <div className="absolute bottom-0 w-full p-4 border-t border-gray-100 bg-gray-50">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-200 flex items-center justify-center">
                            <div className="icon-user text-blue-700"></div>
                        </div>
                        <div>
                            <p className="text-sm font-bold text-gray-900">Harsimranjeet Singh Srau</p>
                            <p className="text-xs text-gray-500">Super Rich Asian</p>
                        </div>
                    </div>
                </div>
            </aside>
        </>
    );
}