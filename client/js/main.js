var interval_in_milliseconds = 100;

var time_chart = null;
var observable_store = null;
var timer_id = null;
var start_time = 0;
var store_series_dict = {};

dojoConfig = {
    async: true,
    parseOnLoad: false
};

require(['dojox/mobile/parser', 'dojox/mobile/compat', 'dojox/mobile/View', 'dojo/domReady!'], function(parser) {
    parser.parse();
});

dojo.addOnLoad(function(event) {
    initialize_chart();
    start_anchor.onclick = start_anchor_onclick;
    stop_anchor.onclick = stop_anchor_onclick;
});

function initialize_chart(event) {
    require(
    [
        'dojo/store/Observable',
        'dojo/store/Memory',
        'dojox/charting/Chart',
        'dojox/charting/themes/Charged',
        'dojox/charting/plot2d/Lines',
        'dojox/charting/axis2d/Default',
        'dojo/domReady!'
    ], function(Observable, Memory, Chart, theme) {
        var memory_store = new Memory({
            data: {
                identifier: 'id',
                label: 'label',
                items: []
            }
        });
        observable_store = new Observable(memory_store);
        time_chart = new Chart('chart_div');
        time_chart.setTheme(theme)
        .addAxis('x')
        .addAxis('y')
        .addPlot('lines', {type: 'Lines', areas: true, tension: 2})
        .render();
    });
}

function start_anchor_onclick(event) {
    timer_id = window.setInterval(update_chart, interval_in_milliseconds);
    start_time = Date.now();
}

function stop_anchor_onclick(event) {
    window.clearInterval(timer_id);
}

function update_chart(event) {
    require(['dojo/request'], function(request) {
        request.get('/process', {
            handleAs: 'json',
            headers: {'X-Requested-With': null}
        }).then(add_point);
    });
    time_chart.render();
}

function add_point(response) {
    require(['dojox/charting/StoreSeries', 'dojo/domReady!'], function (StoreSeries) {
        for (name in response) {
            if (!(name in store_series_dict)) {
                store_series_dict[name] = new StoreSeries(observable_store, {
                    query: {name: name}
                }, 'point');
                time_chart.addSeries(name, store_series_dict[name]);
            }
            observable_store.notify({
                name: name,
                point: {
                    x: (Date.now() - start_time) / 1000,
                    y: response[name].total_attention_level
                }
            });
        }
    });
}

function draw_processes(main, processes) {
    count = 0;
    max_height = 0;
    
    for (key in processes) {
        if (processes[key].left == undefined) processes[key].left = (count % 10) * 100 + 10;
        if (processes[key].top == undefined) processes[key].top = Math.floor(count / 10) * 100 + 10;
        if (processes[key].width == undefined) processes[key].width = 100;
        if (processes[key].height == undefined) processes[key].height = 100;
        
        new_height = processes[key].top + processes[key].height;
        
        if (new_height > max_height) max_height = new_height;
        
        var div = document.createElement('div');
        div.id = 'div_' + processes[key].name;
        div.innerHTML = 'AV: ' + processes[key].attention_value + '<br>BV: ' + processes[key].boost_value;
        main.appendChild(div);
        // Have to use dojo.require and dojo.ready
        //     instead of require(['dojox.layout.FloatingPane', 'dojo/domReady!'], function() {});
        dojo.require('dojox.layout.FloatingPane');
        dojo.ready(function() {
            var style_str = 'position: absolute;';
            style_str += 'left: ' + processes[key].left + ';';
            style_str += 'top: ' + processes[key].top + ';';
            style_str += 'width:     ' + processes[key].width + ';';
            style_str += 'height: ' + processes[key].height + ';';
            
            var floating_pane = new dojox.layout.FloatingPane({
                title: processes[key].name,
                resizable: true,
                dockable: true,
                style: style_str,
                id: 'fp_' + processes[key].name
            }, div);
            
            floating_pane.startup();
        });
        count++;
    }
    
    main.style.height = max_height + 10;
}