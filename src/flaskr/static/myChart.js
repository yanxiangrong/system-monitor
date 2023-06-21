// 基于准备好的dom，初始化echarts实例
const cpuChart = echarts.init(document.getElementById('chart-cpu'));
const memoryChart = echarts.init(document.getElementById('chart-memory'));
const diskIOChart = echarts.init(document.getElementById('chart-disk-io'));
const netIOChart = echarts.init(document.getElementById('chart-net-io'));
const diskPartsChart = initChart(document.getElementById('chart-disk-parts'));

function initChart(dom) {
    let title = document.createElement('span')
    let chart = document.createElement('div')
    title.className = 'progress-bar-title'
    title.innerHTML = '外存用量'
    chart.className = 'progress-chart'
    dom.appendChild(title)
    dom.appendChild(chart)
    return chart
}

function updateDiskParts(data) {
    for (const i in data) {
        let part = data[i]
        let id = 'chart-disk-parts' + part['device']
        let barDom = diskPartsChart.children
        if (barDom.length > i && barDom[i].id === id) {
            for (const div of barDom[i].children) {
                if (div.className === 'progress-bar-name') {
                    div.innerHTML = part['device']
                } else if (div.className === 'progress-bar-value') {
                    div.innerHTML = part['used'] + ' / ' + part['total'] + ' GB'
                } else if (div.className === 'progress-bar-bg') {
                    let bar = div.firstChild
                    bar.style.width = part['percent'] + '%'
                }
            }
        } else {
            while (barDom.length > i + 1) {
                barDom[i].remove()
            }

            let div = document.createElement('div')
            div.id = id
            let title = document.createElement('div')
            title.className = 'progress-bar-name'
            title.innerHTML = part['device']
            div.appendChild(title)

            let value = document.createElement('div')
            value.className = 'progress-bar-value'
            value.innerHTML = part['used'] + ' / ' + part['total'] + ' GB'
            div.appendChild(value)

            let barBg = document.createElement('div')
            let bar = document.createElement('div')
            barBg.className = "progress-bar-bg"
            bar.className = "progress-bar"

            bar.style.width = '0%'

            barBg.appendChild(bar)
            div.appendChild(barBg)

            diskPartsChart.appendChild(div)

            setTimeout(function () {
                bar.style.width = part['percent'] + '%'
                bar.style.transition = 'width 1s linear'
                setTimeout(function () {
                    bar.style.transition = 'width 0.3s linear'
                }, 300)
            }, 0)
        }
    }
}


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
        text: 'CPU 利用率'
    },
    tooltip: {
        trigger: 'axis',
        appendToBody: true,
        valueFormatter: (value) => value + ' %'
    },
    xAxis: xAxisOpt,
    yAxis: {
        name: '%',
    }
};

const memoryChartOpt = {
    title: {
        text: '内存用量'
    },
    tooltip: {
        trigger: 'axis',
        appendToBody: true,
        valueFormatter: (value) => value + ' GB'
    },
    xAxis: xAxisOpt,
    yAxis: {
        name: 'GB',
    }
};

const diskIOChartOpt = {
    title: {
        text: '外存流量'
    },
    tooltip: {
        trigger: 'axis',
        appendToBody: true,
        valueFormatter: (value) => value + ' MB/s'
    },
    xAxis: xAxisOpt,
    yAxis: {
        name: 'MB/s',
    }
};

const netIOChartOpt = {
    ...diskIOChartOpt,
    title: {
        text: '网络流量'
    }
}


// 使用刚指定的配置项和数据显示图表。
cpuChart.setOption(cpuChartOpt);
memoryChart.setOption(memoryChartOpt);
diskIOChart.setOption(diskIOChartOpt);
netIOChart.setOption(netIOChartOpt);

let dataSet = {
    'cpu': {},
    'memory': [],
    'swap': [],
    'disk_io': {
        'read': [],
        'write': []
    },
    'net_io': {
        'read': [],
        'write': []
    }
}

let latest_time = 0
let max = {}
let diskParts = []

function update(data) {
    for (const item of data) {
        let i_time = Date.parse(item['time'])
        if (i_time < latest_time) {
            continue
        }
        latest_time = i_time

        for (const key in item) {
            if (key === 'cpu') {
                for (const core in item['cpu']) {
                    if (!(core in dataSet['cpu'])) {
                        dataSet['cpu'][core] = []
                    }

                    dataSet['cpu'][core].push({
                        name: i_time,
                        value: [i_time, item['cpu'][core]['percent']]
                    })
                    if (i_time - dataSet['cpu'][core][0].name >= 86400000) {
                        dataSet['cpu'][core].shift()
                    }
                }
            } else if (['memory', 'swap'].includes(key)) {
                max[key] = item[key]['total']

                dataSet[key].push({
                    name: i_time,
                    value: [i_time, item[key]['used']]
                })
                if (i_time - dataSet[key][0].name >= 86400000) {
                    dataSet[key].shift()
                }
            } else if (['disk_io', 'net_io'].includes(key)) {
                let read = 0
                let write = 0

                for (const dev of item[key]) {
                    if (key === 'disk_io') {
                        read += dev['read']
                        write += dev['write']
                    } else {
                        read += dev['recv']
                        write += dev['send']
                    }
                }
                dataSet[key]['read'].push({
                    name: i_time,
                    value: [i_time, read]
                })
                dataSet[key]['write'].push({
                    name: i_time,
                    value: [i_time, write]
                })
                if (i_time - dataSet[key]['read'].name >= 86400000) {
                    dataSet[key].shift()
                }
            } else if (key === 'disk_parts') {
                diskParts = item['disk_parts']
            }
        }

    }

    let series = []

    for (const core in dataSet['cpu']) {
        series.push({
            ...seriesOpt,
            name: core,
            data: dataSet['cpu'][core]
        })
    }

    cpuChart.setOption({
        series: series
    })

    memoryChart.setOption({
        yAxis: {
            max: Math.max(max['memory'], max['swap'])
        },
        series: [{
            ...seriesOpt,
            name: '内存',
            markLine: {
                symbol: 'none',
                data: [{
                    name: '内存总量',
                    yAxis: max['memory'],
                    label: {
                        show: false
                    }
                }]
            },
            data: dataSet['memory']
        }, {
            ...seriesOpt,
            name: '交换',
            markLine: {
                symbol: 'none',
                data: [{
                    name: '交换总量',
                    yAxis: max['swap'],
                    label: {
                        show: false
                    }
                }]
            },
            data: dataSet['swap']
        }]
    })

    diskIOChart.setOption({
        series: [{
            ...seriesOpt,
            name: '读取',
            data: dataSet['disk_io']['read']
        }, {
            ...seriesOpt,
            name: '写入',
            data: dataSet['disk_io']['write']
        }]
    })
    netIOChart.setOption({
        series: [{
            ...seriesOpt,
            name: '接收',
            data: dataSet['net_io']['read']
        }, {
            ...seriesOpt,
            name: '发送',
            data: dataSet['net_io']['write']
        }]
    })

    updateDiskParts(diskParts)
}

function connect() {
    let urlStuff = 'ws'
    if (location.protocol === 'https') {
        urlStuff = 'wss'
    }

    const socket = new WebSocket(urlStuff + '://' + location.host + '/data');
    socket.onmessage = function (event) {
        let data = JSON.parse(event.data)
        console.log(data)
        update(data)
    }

    socket.onclose = function () {
        console.log('Socket is closed. Reconnect will be attempted in 10 second.');
        setTimeout(function () {
            connect();
        }, 10000);
    }
}

connect()
