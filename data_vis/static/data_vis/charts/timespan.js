//location.href = "http://example.com";

// reads arguments from preview chart
function ReadArgumentsFromPreviewChart() {

    this.brushSpanSelector = "div#preview_chart > div#linewithfocuschart_container > svg > g > g > g.nv-context > g.nv-x.nv-brush > rect.extent";
    this.brushSelector ="div#preview_chart > div#linewithfocuschart_container > svg > g > g > g.nv-context > g.nv-x.nv-brush > rect.background";

    this.getSpanStartPosition = function() {
        return $(this.brushSpanSelector).attr("x")
    };

    this.getSpanWidth = function () {
        return $(this.brushSpanSelector).attr("width")
    };

    this.getTotalWidth = function () {
        return $(this.brushSelector).attr("width")
    };

    this.getValues = function () {
        var fromX = parseFloat(this.getSpanStartPosition());
        var timespanWidth = parseFloat(this.getSpanWidth());

        return  {
            "from": fromX,
            "to": fromX + timespanWidth,
            "totalWidth": this.getTotalWidth()
        }
    };

    this.isChartSelectable = function() {
        if ($(this.brushSelector).length > 0)
            if ($(this.brushSpanSelector).length > 0)
            return true;
        return false;
    };
}

// construct new url with arguments from preview chart
function ConstructLinkFromPreviewChart(href) {

    this.url = href;

    this.getUrl = function() {
        var values = new ReadArgumentsFromPreviewChart().getValues();
        return this.url + "?" + "relFrom=" + (values.from/values.totalWidth).toPrecision(4) +
            "&relTo=" + (values.to/values.totalWidth).toPrecision(4);
    };

}

// open new url
function ForwardWithPreviewArguments(href) {

    this.href = href;

    this.forward = function (href) {
        var args = new ReadArgumentsFromPreviewChart();
        if (args.isChartSelectable()) {
            console.log("selectable")
            window.open(new ConstructLinkFromPreviewChart(this.href).getUrl(), "_self")
        } else {
            console.log("nOt selectable:" + self.href);
            window.open(this.href, "_self")
        }
    };

    this.forward();
}


// replace old href attributes and register on click functions
$(function() {
    var lcd = $("#line_chart_details");
    var href = lcd.attr("href");
    console.log("href caught: " + href)
    lcd.attr("href", "javascript:void(0)");
    lcd.attr("onclick", " var f = new ForwardWithPreviewArguments(\"" + href + "\");");

    var pcd = $("#pie_chart_details");
    href = pcd.attr("href");
    console.log("href caught: " + href)
    pcd.attr("href", "javascript:void(0)");
    pcd.attr("onclick", " var f = new ForwardWithPreviewArguments(\"" + href + "\");");
});