var chart = null;

dojoConfig =
{
    async: true,
    parseOnLoad: false
};

require(['dojox/mobile/parser', 'dojox/mobile/compat', 'dojox/mobile/View', 'dojo/domReady!'], function(parser)
{
    parser.parse();
});

function draw_processes(main, processes)
{
    count = 0;
    max_height = 0;
    
    for (key in processes)
    {
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
        dojo.ready(function()
        {
            var style_str = 'position: absolute;';
            style_str += 'left: ' + processes[key].left + ';';
            style_str += 'top: ' + processes[key].top + ';';
            style_str += 'width: ' + processes[key].width + ';';
            style_str += 'height: ' + processes[key].height + ';';
            
            var floating_pane = new dojox.layout.FloatingPane(
            {
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

function draw_chart(series)
{
    for (key in series) chart.addSeries(key, series[key]);
    chart.render();
    var debug = document.getElementById('debug');
    length = series[key].length;
    debug.innerHTML += series[key][length-1].x + ',';
}

function run()
{
    $.ajax({
        type: 'POST',
        url: 'http://localhost:8000/compete',
        data: {param: 1}
    }).done(function (output)
    {
        draw_chart(output.series);
    });
}

function init()
{
    var main = document.getElementById('main');
    require(['dojo/request'], function(request)
    {
        request.get('http://localhost:8000/process', {handleAs: 'json', headers: {'X-Requested-With': null}}).then
        (
            function(objects)
            {
                draw_processes(main, objects);
            },
            function(error) { console.log('[ Error ] ' + error); }
        );
    });
    
    require(['dojox/charting/Chart', 'dojox/charting/themes/Charged', 'dojox/charting/plot2d/Scatter', 'dojox/charting/plot2d/Markers', 'dojox/charting/axis2d/Default', 'dojo/domReady!'], function(Chart, theme)
    {
        chart = new Chart('chart_node');
        chart.setTheme(theme);
        chart.addPlot('default',
        {
            type: 'Scatter',
        });
        chart.addAxis('x');
        chart.addAxis('y', {vertical: true});
        chart.render();
    });
}
