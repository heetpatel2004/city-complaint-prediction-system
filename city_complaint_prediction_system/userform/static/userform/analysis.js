let statusChart, categoryChart, trendChart;

function loadDashboard() {
    fetch('/dashboard-data/')
    .then(res => res.json())
    .then(data => {

        // STATUS
        const statusLabels = data.status.map(i => i.status);
        const statusCounts = data.status.map(i => i.count);

        // CATEGORY
        const categoryLabels = data.category.map(i => i.category);
        const categoryCounts = data.category.map(i => i.count);

        // TREND
        const trendLabels = data.trend.map(i => i.date);
        const trendCounts = data.trend.map(i => i.count);

        // DESTROY OLD
        if(statusChart) statusChart.destroy();
        if(categoryChart) categoryChart.destroy();
        if(trendChart) trendChart.destroy();

        // STATUS CHART
        statusChart = new Chart(document.getElementById('statusChart'), {
            type: 'bar',
            data: {
                labels: statusLabels,
                datasets: [{
                    data: statusCounts,
                    backgroundColor: ['#ff9f43','#4a7cff','#4bc0c0','#a29bfe']
                }]
            }
        });

        // CATEGORY CHART
        categoryChart = new Chart(document.getElementById('categoryChart'), {
            type: 'pie',
            data: {
                labels: categoryLabels,
                datasets: [{
                    data: categoryCounts,
                    backgroundColor: ['#ff9f43','#4a7cff','#4bc0c0','#a29bfe']
                }]
            }
        });

        // TREND CHART
        trendChart = new Chart(document.getElementById('trendChart'), {
            type: 'line',
            data: {
                labels: trendLabels,
                datasets: [{
                    data: trendCounts,
                    borderColor: '#4a7cff',
                    fill: false,
                    tension: 0.3
                }]
            }
        });

        // SUMMARY (dynamic %)
        let total = categoryCounts.reduce((a, b) => a + b, 0);
        let summaryHTML = "";

        categoryLabels.forEach((label, i) => {
            let percent = total ? ((categoryCounts[i] / total) * 100).toFixed(1) : 0;
            summaryHTML += `<li>${label} <span>${percent}%</span></li>`;
        });

        document.getElementById("summaryList").innerHTML = summaryHTML;

    });
}

// Load + Refresh
loadDashboard();
setInterval(loadDashboard, 5000);