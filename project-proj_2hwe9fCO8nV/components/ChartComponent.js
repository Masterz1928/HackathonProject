function ChartComponent({ incomeData, expenseData }) {
    const chartRef = React.useRef(null);
    const canvasRef = React.useRef(null);

    React.useEffect(() => {
        const ctx = canvasRef.current.getContext('2d');
        
        if (chartRef.current) {
            chartRef.current.destroy();
        }

        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

        chartRef.current = new window.ChartJS(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Income',
                        data: incomeData, // e.g. [120, 200, 150, 80, 70, 110, 130]
                        backgroundColor: '#10B981',
                        borderRadius: 4,
                        barPercentage: 0.6,
                    },
                    {
                        label: 'Expense',
                        data: expenseData, // e.g. [80, 100, 50, 40, 120, 60, 90]
                        backgroundColor: '#EF4444',
                        borderRadius: 4,
                        barPercentage: 0.6,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#1f2937',
                        bodyColor: '#4b5563',
                        borderColor: '#e5e7eb',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true,
                        boxPadding: 4
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#f3f4f6',
                            drawBorder: false,
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            color: '#9ca3af'
                        },
                        border: {
                            display: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            color: '#9ca3af'
                        },
                        border: {
                            display: false
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });

        return () => {
            if (chartRef.current) {
                chartRef.current.destroy();
            }
        };
    }, [incomeData, expenseData]);

    return (
        <div className="card h-80 relative fade-in" style={{ animationDelay: '0.1s' }} data-name="chart-component" data-file="components/ChartComponent.js">
            <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-lg text-gray-800">Weekly Overview</h3>
                <div className="text-sm text-gray-500">Last 7 Days</div>
            </div>
            <div className="relative h-64 w-full">
                <canvas ref={canvasRef}></canvas>
            </div>
        </div>
    );
}