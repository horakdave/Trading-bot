console.log("JS file is loaded.");

// Function to calculate moving averages
function calculateMovingAverage(data, windowSize) {
  const movingAverages = [];
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - windowSize + 1);
    const end = i + 1;
    const values = data.slice(start, end).map(d => d.close);
    const average = values.reduce((sum, value) => sum + value, 0) / values.length;
    movingAverages.push(average);
  }
  return movingAverages;
}

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

    const shortMA = calculateMovingAverage(stockData, 5); //5-period moving average
    const longMA = calculateMovingAverage(stockData, 20); //20-period moving average

    updateChart(stockData, shortMA, longMA);
  } catch (error) {
    console.error('Error fetching stock data:', error);
    throw error;
  }
}

function updateChart(data, shortMA, longMA) {
  const tracePrice = {
    x: data.map(d => d.date),
    y: data.map(d => d.close),
    type: 'scatter',
    mode: 'lines',
    name: 'Price'
  };

  const traceShortMA = {
    x: data.map(d => d.date),
    y: shortMA,
    type: 'scatter',
    mode: 'lines',
    name: 'Short MA'
  };

  const traceLongMA = {
    x: data.map(d => d.date),
    y: longMA,
    type: 'scatter',
    mode: 'lines',
    name: 'Long MA'
  };

  const touchPoints = shortMA.slice(1).map((value, index) => (value === longMA[index + 1] ? data[index + 1].date : null));

  const traceTouchPoints = {
    x: touchPoints.filter(point => point !== null),
    y: touchPoints.filter(point => point !== null).map(() => shortMA[1]),
    type: 'scatter',
    mode: 'markers',
    name: 'Touch Point',
    marker: {
      size: 8,
      color: 'red'
    }
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

  Plotly.react('chart', [tracePrice, traceShortMA, traceLongMA, traceTouchPoints], layout);
}

let symbol = 'TSLA';

async function updateData() {
  await getStockData(symbol);
}

updateData();
setInterval(updateData, 60000);
