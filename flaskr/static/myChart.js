// 基于准备好的dom，初始化echarts实例
const cpuChart = echarts.init(document.getElementById('chart-cpu'));


const xAxisOpt = {
    type: 'time',
    minInterval: 60 * 1000,
    splitLine: {
        show: true
    }
}

const seriesOpt = {
    type: 'line',
    symbol: 'none',
    connectNulls: true,
    areaStyle: {
        opacity: 0.2,
    },
    lineStyle: {
        width: 1,
        opacity: 0.8,
    },
}
// 指定图表的配置项和数据
const cpuChartOpt = {
    title: {
        text: 'CPU'
    },
    tooltip: {
        trigger: 'axis',
        appendToBody: true,
        valueFormatter: (value) => value + ' %'
    },
    xAxis: xAxisOpt,
    yAxis: {
        axisLabel: {
            formatter: '{value} %'
        }
    }
};

// 使用刚指定的配置项和数据显示图表。
cpuChart.setOption(cpuChartOpt);

let dataSet = {};

function connect() {
    let urlStuff = 'ws'
    if (location.protocol === 'https') {
        urlStuff = 'wss'
    }

    const socket = new WebSocket(urlStuff + '://' + location.host + '/data');
    socket.onmessage = function (event) {
        let data = JSON.parse(event.data)
        // console.log(data)


        for (const i of data) {
            for (const core in i['cpu']) {
                if (!(core in dataSet)) {
                    dataSet[core] = []
                }

                if (dataSet[core].length > 0 && Date.parse(i['time']) <= dataSet[core][dataSet[core].length - 1].value[0]) {
                    continue
                }
                dataSet[core].push({name: i['time'], value: [Date.parse(i['time']), i['cpu'][core]['percent']]})
                if (dataSet[core][0].value[dataSet[core][0].value.length - 1] - dataSet[core][0].value[0] >= 86400000) {
                    dataSet[core].shift()
                }
            }
        }

        let series = []

        for (const core in dataSet) {
            series.push({
                ...seriesOpt,
                name: core,
                data: dataSet[core]
            })
        }

        cpuChart.setOption({
            series: series
        })
    }

    socket.onclose = function () {
        console.log('Socket is closed. Reconnect will be attempted in 10 second.');
        setTimeout(function () {
            connect();
        }, 10000);
    }
}

connect()
