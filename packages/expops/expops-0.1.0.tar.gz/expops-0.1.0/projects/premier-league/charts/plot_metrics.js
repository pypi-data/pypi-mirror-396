import { chart } from '/mlops-charts.js';

// Dynamic chart: NN A vs NN B vs NN C losses on same chart
chart('nn_losses', (probePaths, ctx, listener) => {
  const canvas = document.createElement('canvas');
  ctx.containerElement.innerHTML = '';
  ctx.containerElement.appendChild(canvas);

  const colors = [
    'rgb(75, 192, 192)',
    'rgb(255, 99, 132)',
    'rgb(54, 162, 235)'
  ];

  const chartData = {
    labels: [],
    datasets: []
  };

  let colorIndex = 0;
  const keys = Object.keys(probePaths);
  keys.forEach((k) => {
    chartData.datasets.push({
      label: k.replace(/_/g, ' ').toUpperCase(),
      data: [],
      borderColor: colors[colorIndex % colors.length],
      backgroundColor: colors[colorIndex % colors.length] + '33',
      tension: 0.1,
      fill: false
    });
    colorIndex++;
  });

  const chartInstance = new Chart(canvas, {
    type: 'line',
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        x: { title: { display: true, text: 'Epoch' } },
        y: { title: { display: true, text: 'Loss' }, beginAtZero: false }
      },
      plugins: {
        title: { display: true, text: 'NN Training Loss (A/B)' },
        legend: { display: true }
      },
      animation: { duration: 200 }
    }
  });
  ctx.setChartInstance(chartInstance);

  listener.subscribeAll(probePaths, (allMetrics) => {
    let maxLength = 0;

    chartData.datasets.forEach((dataset, idx) => {
      const probeKey = keys[idx];
      const metrics = allMetrics[probeKey] || {};
      const lossSeries = ctx.toSeries(metrics.train_loss || {});
      dataset.data = lossSeries;
      maxLength = Math.max(maxLength, lossSeries.length);
    });

    chartData.labels = Array.from({ length: maxLength }, (_, i) => i + 1);

    chartInstance.update();
  });
});


