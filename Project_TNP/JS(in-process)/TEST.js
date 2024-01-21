async function getStockData(symbol, interval = '1m', hoursBack = 24) {
  const endDate = new Date();
  const startDate = new Date(endDate.getTime() - hoursBack * 60 * 60 * 1000);
  const period1 = Math.floor(startDate.getTime() / 1000);
  const period2 = Math.floor(endDate.getTime() / 1000);
  const url = `https://finance.yahoo.com/quote/${symbol}/history?period1=${period1}&period2=${period2}&interval=${interval}&filter=history`;
  const response = await fetch(url);
  const data = await response.json();
  return data;
}

function simpleMovingAverageStrategy(data, shortWindow = 10, longWindow = 50) {
  const signals = {
    price: data.map(d => d.close),
    shortMavg: [],
    longMavg: [],
    signal: [],
    positions: []
  };

  for (let i = shortWindow; i < data.length; i++) {
    signals.shortMavg.push(data.slice(i - shortWindow, i).reduce((a, b) => a + b.close, 0) / shortWindow);
    signals.longMavg.push(data.slice(i - longWindow, i).reduce((a, b) => a + b.close, 0) / longWindow);
    signals.signal.push(signals.shortMavg[i - shortWindow] > signals.longMavg[i - shortWindow] ? 1 : -1);
    signals.positions.push(signals.signal[i - shortWindow] !== signals.signal[i - shortWindow + 1] ? signals.signal[i - shortWindow + 1] : 0);
  }

  return signals;
}

function updateChart(data, signals) {
  const tracePrice = {
    x: data.map(d => d.date),
    y: data.map(d => d.close),
    type: 'scatter',
    mode: 'lines',
    name: 'Price'
  };

  const traceShortMavg = {
    x: signals.signal.map((_, i) => data[i].date),
    y: signals.shortMavg,
    type: 'scatter',
    mode: 'lines',
    name: 'Short MA',
    line: { color: '#F4C20D' }
  };

  const traceLongMavg = {
    x: signals.signal.map((_, i) => data[i].date),
    y: signals.longMavg,
    type: 'scatter',
    mode: 'lines',
    name: 'Long MA',
    line: { color: '#ED4245' }
  };

  const traceBuy = {
    x: signals.positions.map((_, i) => data[i].date).filter(d => d.positions[i] === 1),
    y: signals.positions.map((_, i) => data[i].close).filter(d => d.positions[i] === 1),
    mode: 'markers',
    name: 'Buy',
    marker: { color: '#27AE60', size: 10 }
  };

  const traceSell = {
    x: signals.positions.map((_, i) => data[i].date).filter(d => d.positions[i] === -1),
    y: signals.positions.map((_, i) => data[i].close).filter(d => d.positions[i] === -1),
    mode: 'markers',
    name: 'Sell',
    marker: { color: '#ED4245', size: 10 }
  };

  const layout = {
    title: `${symbol} - Real-Time Moving Average Strategy`,
    xaxis: {
      title: 'Date',
      rangeslider: { visible: false },
      type: 'date'
    },
    yaxis: {
      title: 'Price'
    },
    grid: {
      rows: 5,
      columns: 5,
      pattern: 'independent'
    }
  };

  Plotly.newPlot('chart', [tracePrice, traceShortMavg, traceLongMavg, traceBuy, traceSell], layout);
}

let symbol = 'TSLA';

async function updateData() {
  const data = await getStockData(symbol);
  const signals = simpleMovingAverageStrategy(data);
  updateChart(data, signals);
}

updateData();
setInterval(updateData, 60000); // update every 60 seconds