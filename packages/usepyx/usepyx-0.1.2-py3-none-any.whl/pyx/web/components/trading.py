"""
PyX Trading Charts (AG Charts)
Enterprise-grade financial charting for trading applications.
"""
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
import json


@dataclass
class Series:
    """
    Chart series configuration.
    
    Types:
    - 'line', 'area', 'bar', 'column'
    - 'candlestick', 'ohlc' (Financial)
    - 'scatter', 'bubble'
    """
    type: str
    x_key: str = "x"
    y_key: str = "y"
    # For OHLC/Candlestick
    open_key: str = "open"
    high_key: str = "high"
    low_key: str = "low"
    close_key: str = "close"
    # For styling
    name: str = None
    color: str = None
    stroke_width: int = 2
    fill_opacity: float = 0.3
    # Axis assignment
    y_axis: str = None  # For multi-axis charts
    
    def to_ag_series(self) -> Dict:
        """Convert to AG Charts series config"""
        if self.type in ['candlestick', 'ohlc']:
            return {
                "type": self.type,
                "xKey": self.x_key,
                "openKey": self.open_key,
                "highKey": self.high_key,
                "lowKey": self.low_key,
                "closeKey": self.close_key,
                "title": self.name,
            }
        
        series = {
            "type": self.type,
            "xKey": self.x_key,
            "yKey": self.y_key,
        }
        
        if self.name:
            series["title"] = self.name
        if self.color:
            if self.type in ['line', 'area']:
                series["stroke"] = self.color
            else:
                series["fill"] = self.color
        if self.stroke_width and self.type in ['line', 'area']:
            series["strokeWidth"] = self.stroke_width
        if self.fill_opacity and self.type == 'area':
            series["fillOpacity"] = self.fill_opacity
        if self.y_axis:
            series["yAxisId"] = self.y_axis
            
        return series


@dataclass
class Axis:
    """
    Axis configuration for multi-axis charts.
    """
    id: str = None
    position: str = "left"  # 'left', 'right', 'top', 'bottom'
    title: str = None
    type: str = "number"  # 'number', 'category', 'time'
    min: float = None
    max: float = None
    nice: bool = True
    tick_count: int = None
    grid_lines: bool = True
    
    def to_ag_axis(self) -> Dict:
        axis = {
            "type": self.type,
            "position": self.position,
        }
        
        if self.id:
            axis["id"] = self.id
        if self.title:
            axis["title"] = {"text": self.title}
        if self.min is not None:
            axis["min"] = self.min
        if self.max is not None:
            axis["max"] = self.max
        if self.tick_count:
            axis["tick"] = {"count": self.tick_count}
        if not self.grid_lines:
            axis["gridLine"] = {"enabled": False}
            
        return axis


class TradingChart:
    """
    Enterprise Trading Chart Component.
    
    Usage:
        from pyx import TradingChart, Series
        
        # Simple Candlestick
        chart = TradingChart(
            data=ohlc_data,
            series=[Series(type="candlestick")]
        )
        
        # With Volume Overlay
        chart = TradingChart(
            data=ohlc_data,
            series=[
                Series(type="candlestick"),
                Series(type="bar", y_key="volume", y_axis="volume"),
            ],
            multi_axis=True,
        )
        
        # Real-time update
        chart.update_data(new_data)
    """
    
    # AG Charts CDN
    AG_CHARTS_JS = "https://cdn.jsdelivr.net/npm/ag-charts-community@9.0.0/dist/umd/ag-charts-community.min.js"
    
    def __init__(
        self,
        data: List[Dict[str, Any]] = None,
        series: List[Series] = None,
        # Axes
        x_axis: Axis = None,
        y_axes: List[Axis] = None,
        # Features
        title: str = None,
        subtitle: str = None,
        legend: bool = True,
        tooltip: bool = True,
        crosshair: bool = True,
        zoom: bool = True,  # Enable zoom/pan
        navigator: bool = False,  # Range selector at bottom
        # Sizing
        height: str = "400px",
        width: str = "100%",
        # Theme
        theme: str = "ag-default",  # 'ag-default', 'ag-dark', 'ag-material', etc.
        # Events
        on_click: callable = None,
        # ID
        chart_id: str = None,
    ):
        self.data = data or []
        self.series = series or [Series(type="line")]
        self.x_axis = x_axis
        self.y_axes = y_axes
        self.title = title
        self.subtitle = subtitle
        self.legend = legend
        self.tooltip = tooltip
        self.crosshair = crosshair
        self.zoom = zoom
        self.navigator = navigator
        self.height = height
        self.width = width
        self.theme = theme
        self.on_click = on_click
        self.chart_id = chart_id or f"trading-chart-{id(self)}"
        
    def _build_axes(self) -> List[Dict]:
        """Build axes configuration"""
        axes = []
        
        # X Axis
        if self.x_axis:
            axes.append(self.x_axis.to_ag_axis())
        else:
            # Default time axis for trading
            axes.append({
                "type": "time",
                "position": "bottom",
                "nice": True,
            })
        
        # Y Axes
        if self.y_axes:
            for y_axis in self.y_axes:
                axes.append(y_axis.to_ag_axis())
        else:
            # Default number axis
            axes.append({
                "type": "number",
                "position": "left",
                "title": {"text": "Price"},
            })
            
        return axes
    
    def _build_options(self) -> Dict:
        """Build AG Charts options"""
        options = {
            "data": self.data,
            "series": [s.to_ag_series() for s in self.series],
            "axes": self._build_axes(),
            "theme": self.theme,
        }
        
        # Title
        if self.title:
            options["title"] = {"text": self.title}
            if self.subtitle:
                options["subtitle"] = {"text": self.subtitle}
        
        # Legend
        options["legend"] = {"enabled": self.legend}
        
        # Tooltip
        if self.tooltip:
            options["tooltip"] = {"enabled": True}
        
        # Crosshair (very useful for trading)
        if self.crosshair:
            options["axes"][0]["crosshair"] = {"enabled": True}
            if len(options["axes"]) > 1:
                options["axes"][1]["crosshair"] = {"enabled": True}
        
        # Zoom
        if self.zoom:
            options["zoom"] = {
                "enabled": True,
                "enableAxisDragging": True,
                "enablePanning": True,
                "enableScrolling": True,
            }
        
        # Navigator (Range Selector)
        if self.navigator:
            options["navigator"] = {"enabled": True}
        
        return options
        
    def render(self) -> str:
        """Render the chart as HTML"""
        options_json = json.dumps(self._build_options())
        
        # Click handler
        click_handler = ""
        if self.on_click:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_click)
            click_handler = f"""
                options.listeners = {{
                    click: function(event) {{
                        PyX.sendEvent('{handler_name}');
                    }}
                }};
            """
        
        return f"""
        <script src="{self.AG_CHARTS_JS}"></script>
        
        <div id="{self.chart_id}" style="height: {self.height}; width: {self.width};"></div>
        
        <script>
            (function() {{
                const options = {options_json};
                options.container = document.getElementById('{self.chart_id}');
                {click_handler}
                
                const chart = agCharts.AgChart.create(options);
                
                // Store reference for updates
                window.pyxCharts = window.pyxCharts || {{}};
                window.pyxCharts['{self.chart_id}'] = chart;
            }})();
        </script>
        """
    
    def __str__(self):
        return self.render()


class CandlestickChart(TradingChart):
    """
    Pre-configured Candlestick chart for OHLC data.
    
    Usage:
        from pyx import CandlestickChart
        
        data = [
            {"date": "2024-01-01", "open": 100, "high": 105, "low": 98, "close": 103, "volume": 1000000},
            {"date": "2024-01-02", "open": 103, "high": 108, "low": 101, "close": 107, "volume": 1200000},
        ]
        
        chart = CandlestickChart(
            data=data,
            x_key="date",
            with_volume=True,
        )
    """
    
    def __init__(
        self,
        data: List[Dict[str, Any]],
        x_key: str = "date",
        open_key: str = "open",
        high_key: str = "high",
        low_key: str = "low",
        close_key: str = "close",
        volume_key: str = "volume",
        with_volume: bool = True,
        **kwargs
    ):
        # Build series
        series = [
            Series(
                type="candlestick",
                x_key=x_key,
                open_key=open_key,
                high_key=high_key,
                low_key=low_key,
                close_key=close_key,
            )
        ]
        
        y_axes = [Axis(id="price", position="left", title="Price")]
        
        # Add volume overlay
        if with_volume and volume_key:
            series.append(
                Series(
                    type="bar",
                    x_key=x_key,
                    y_key=volume_key,
                    name="Volume",
                    y_axis="volume",
                    fill_opacity=0.3,
                )
            )
            y_axes.append(
                Axis(id="volume", position="right", title="Volume")
            )
        
        # Set default options
        kwargs.setdefault("crosshair", True)
        kwargs.setdefault("zoom", True)
        kwargs.setdefault("navigator", True)
        kwargs.setdefault("height", "500px")
        kwargs.setdefault("theme", "ag-default-dark")
        
        super().__init__(
            data=data,
            series=series,
            y_axes=y_axes,
            x_axis=Axis(type="time", position="bottom"),
            **kwargs
        )


class LineChart(TradingChart):
    """
    Pre-configured Line chart for price/indicator data.
    
    Usage:
        from pyx import LineChart
        
        chart = LineChart(
            data=price_data,
            lines=[
                {"key": "price", "name": "Price", "color": "#22c55e"},
                {"key": "ma20", "name": "MA 20", "color": "#3b82f6"},
                {"key": "ma50", "name": "MA 50", "color": "#f59e0b"},
            ]
        )
    """
    
    def __init__(
        self,
        data: List[Dict[str, Any]],
        x_key: str = "date",
        lines: List[Dict[str, str]] = None,
        **kwargs
    ):
        # Build series from lines config
        series = []
        if lines:
            for line in lines:
                series.append(
                    Series(
                        type="line",
                        x_key=x_key,
                        y_key=line.get("key"),
                        name=line.get("name"),
                        color=line.get("color"),
                        stroke_width=line.get("width", 2),
                    )
                )
        else:
            series = [Series(type="line", x_key=x_key, y_key="value")]
        
        kwargs.setdefault("crosshair", True)
        kwargs.setdefault("zoom", True)
        
        super().__init__(
            data=data,
            series=series,
            x_axis=Axis(type="time", position="bottom"),
            **kwargs
        )


class AreaChart(TradingChart):
    """Pre-configured Area chart."""
    
    def __init__(
        self,
        data: List[Dict[str, Any]],
        x_key: str = "date",
        y_key: str = "value",
        name: str = None,
        color: str = "#3b82f6",
        **kwargs
    ):
        series = [
            Series(
                type="area",
                x_key=x_key,
                y_key=y_key,
                name=name,
                color=color,
                fill_opacity=0.3,
            )
        ]
        
        super().__init__(
            data=data,
            series=series,
            x_axis=Axis(type="time", position="bottom"),
            **kwargs
        )


# Convenience functions
def candlestick_chart(data, **kwargs) -> CandlestickChart:
    """Create a candlestick chart."""
    return CandlestickChart(data=data, **kwargs)

def line_chart(data, **kwargs) -> LineChart:
    """Create a line chart."""
    return LineChart(data=data, **kwargs)

def area_chart(data, **kwargs) -> AreaChart:
    """Create an area chart."""
    return AreaChart(data=data, **kwargs)
