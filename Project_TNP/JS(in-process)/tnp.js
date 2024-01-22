console.log("JS file is loaded.");

async function getStockData(symbol, interval = '1m', hoursBack = 24) {
  const endDate = new Date();
  const startDate = new Date(endDate.getTime() - hoursBack * 60 * 60 * 1000);
  const period1 = Math.floor(startDate.getTime() / 1000);
  const period2 = Math.floor(endDate.getTime() / 1000);

  const proxyUrl = 'https://cors-anywhere.herokuapp.com/'; //public proxy url
  const apiUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?period1=${period1}&period2=${period2}&interval=${interval}`;
  
  try {
    const response = await fetch(proxyUrl + apiUrl);
    const data = await response.json();
    
    const timestamps = data.chart.result[0].timestamp.map(timestamp => new Date(timestamp * 1000));
    const closes = data.chart.result[0].indicators.quote[0].close;

    const stockData = timestamps.map((timestamp, index) => ({
      date: timestamp,
      close: closes[index]
    }));

    updateChart(stockData);
  } catch (error) {
    console.error('Error fetching stock data:', error);
    throw error;
  }
}


function updateChart(data) {
  const tracePrice = {
    x: data.map(d => d.date),
    y: data.map(d => d.close),
    type: 'scatter',
    mode: 'lines',
    name: 'Price'
  };

  const layout = {
    title: 'Real-Time Moving Average Strategy',
    xaxis: {
      title: 'Date',
      rangeslider: { visible: false },
      type: 'date'
    },
    yaxis: {
      title: 'Price'
    }
  };

  Plotly.newPlot('chart', [tracePrice], layout);
}

let symbol = 'TSLA';

async function updateData() {
  await getStockData(symbol);
}

updateData();
setInterval(updateData, 60000);
