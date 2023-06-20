// 基于准备好的dom，初始化echarts实例
const myChart = echarts.init(document.getElementById('main'));


// 指定图表的配置项和数据
const option = {
    title: {
        text: 'CPU'
    },
    tooltip: {
        trigger: 'axis',
        appendToBody: true,
        valueFormatter: (value) => value + ' %'
    },
    xAxis: {
        type: 'time',
        minInterval: 60 * 1000,
        splitLine: {
            show: true
        }
    },
    yAxis: {
        axisLabel: {
            formatter: '{value} %'
        }
    }
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

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
                if (dataSet[core].length > 288) {
                    dataSet[core].shift()
                }
            }
        }

        let series = []

        for (const core in dataSet) {
            series.push({
                name: core,
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
                data: dataSet[core]
            })
        }

        myChart.setOption({
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
