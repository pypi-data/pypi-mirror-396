/**
 * Titanic Project - Dynamic Charts (Frontend)
 * 
 * This file demonstrates how to write dynamic charts for the frontend.
 * The API is similar to the Python @chart() decorator.
 * 
 * Users import the chart() function from mlops-charts.js and define their charts.
 */

import { chart } from '/mlops-charts.js';

/**
 * Dynamic chart: NN A vs NN B losses on the same chart
 */
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

/**
 * Static chart comparing test accuracy and precision across models.
 * 
 * For static charts, you can fetch metrics once and render.
 * This example shows how to create a bar chart for comparison.
 */
chart('test_metrics_comparison', (probePaths, ctx, listener) => {
  const canvas = document.createElement('canvas');
  ctx.containerElement.innerHTML = '';
  ctx.containerElement.appendChild(canvas);
  
  // For static charts, we fetch once and render
  listener.subscribeAll(probePaths, (allMetrics) => {
    const groups = {
      'NN A': allMetrics.nn_a || {},
      'NN B': allMetrics.nn_b || {},
      'Linear': allMetrics.linear || {}
    };
    
    const labels = [];
    const accuracies = [];
    const precisions = [];
    
    for (const [label, metrics] of Object.entries(groups)) {
      const acc = ctx.getValue(metrics.test_accuracy);
      const prec = ctx.getValue(metrics.test_precision);
      
      if (acc !== null || prec !== null) {
        labels.push(label);
        accuracies.push(acc || 0);
        precisions.push(prec || 0);
      }
    }
    
    if (labels.length === 0) {
      ctx.containerElement.innerHTML = '<div class="chart-message">Waiting for test metrics...</div>';
      return;
    }
    
    // Create or update chart
    if (ctx.chartInstance) {
      ctx.chartInstance.data.labels = labels;
      ctx.chartInstance.data.datasets[0].data = accuracies;
      ctx.chartInstance.data.datasets[1].data = precisions;
      ctx.chartInstance.update();
    } else {
      const chartInstance = new Chart(canvas, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Accuracy',
              data: accuracies,
              backgroundColor: 'rgba(70, 130, 180, 0.7)',
              borderColor: 'rgb(70, 130, 180)',
              borderWidth: 1
            },
            {
              label: 'Precision',
              data: precisions,
              backgroundColor: 'rgba(255, 127, 80, 0.7)',
              borderColor: 'rgb(255, 127, 80)',
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              beginAtZero: true,
              max: 1.0,
              title: {
                display: true,
                text: 'Score'
              }
            }
          },
          plugins: {
            title: {
              display: true,
              text: 'Test Metrics Comparison'
            },
            legend: {
              display: true
            }
          }
        }
      });
      ctx.setChartInstance(chartInstance);
    }
  });
});

