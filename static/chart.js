const data = JSON.parse(document.getElementById('chart-data').textContent);
const labels = data.map(row => row[0]); // Item names
const prices = data.map(row => row[1]); // Prices

const ctx = document.getElementById('spendingChart').getContext('2d');
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Költések (Ft)',
            data: prices,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
