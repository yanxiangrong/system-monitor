// 基于准备好的dom，初始化echarts实例
var myChart = echarts.init(document.getElementById('main'));

let dataSet = [];


// 指定图表的配置项和数据
const option = {
    title: {
        text: 'CPU'
    },
    tooltip: {
        trigger: 'axis',
        appendToBody: true
    },
    dataset: {
        source: dataSet,
    },
    xAxis: {
        type: 'time',
        splitNumber: 4,
        minInterval: 60 * 1000
    },
    yAxis: {},
    series: {
        name: '利用率',
        type: 'line',
        symbol: 'none',
        areaStyle: {
            opacity: 0.3,
        },
        lineStyle: {
            width: 1,
        },
    }
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

urlStuff = 'ws'
if (location.protocol === 'https') {
    urlStuff = 'wss'
}

const socket = new WebSocket(urlStuff + '://' + location.host + '/data');
socket.onmessage = function (event) {
    let data = JSON.parse(event.data)
    // console.log(data)
    for (const i of data) {
        if (dataSet.length > 0 && Date.parse(i['time']) <= dataSet[dataSet.length - 1][0]) {
            continue
        }
        dataSet.push([Date.parse(i['time']), i['cpu'][0]['percent']])
    }
    // dataSet.push([data['time'], data['cpu'][0]['percent']])
    // console.log([data['time'], data['cpu'][0]['percent']])
    myChart.setOption({
        dataset: {
            source: dataSet,
        },
    })
}
